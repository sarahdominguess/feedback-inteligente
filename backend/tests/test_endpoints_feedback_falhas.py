"""Testes dos caminhos de FALHA do POST /api/feedback/gerar.

Arquivo separado do test_endpoints_feedback.py de propósito: ali ficam os
testes do caminho feliz; aqui, o que acontece quando a IA ou a gravação
falham. A IA é um dublê programado para levantar a exceção desejada — nenhum
teste chama a internet.
"""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from domain.excecoes import (
    DadosIndisponiveisError,
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
)
from domain.feedback_roteiro import FeedbackRoteiro
from endpoints.dependencias import obter_llm_service, obter_registro_feedbacks
from main import app
from services.registro_feedback import RegistroFeedbackService


class LLMQueFalha:
    """Dublê da IA que só levanta a exceção programada.

    Dublê (fake): objeto de mentira que ocupa o lugar do serviço real no
    teste. Aqui ele nem devolve roteiro — serve para simular cada tipo de
    falha sem depender da internet.
    """

    def __init__(self, erro: Exception):
        self.erro = erro
        self.chamadas = 0

    def gerar_roteiro_feedback(self, vendedor_id, mes_referencia=None):
        """Conta a chamada e levanta o erro programado."""
        self.chamadas += 1
        raise self.erro


class LLMFunciona:
    """Dublê mínimo da IA que devolve um roteiro válido.

    Usado quando o teste precisa passar da etapa da IA para chegar à etapa
    da gravação.
    """

    def gerar_roteiro_feedback(self, vendedor_id, mes_referencia=None):
        """Devolve um roteiro fixo, sempre com as quatro listas preenchidas."""
        return FeedbackRoteiro(
            pontos_positivos=["Bom atendimento"],
            pontos_melhoria=["Oferecer mais peças"],
            possiveis_motivos=["Correria no sábado"],
            roteiro_conversa=["Como foi o sábado?"],
        )


class RegistroQueFalha:
    """Dublê do registro que simula um disco indisponível ao gravar."""

    def __init__(self):
        self.chamadas = 0

    def registrar(self, **kwargs):
        """Aceita os argumentos da rota e falha na gravação."""
        self.chamadas += 1
        raise DadosIndisponiveisError(
            "Não foi possível gravar: disco cheio em C:\\dados\\interno.json"
        )


class TestFalhasNaGeracao(unittest.TestCase):
    """Testes dos erros da rota de geração de feedback."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente com raise_server_exceptions=False.

        Com o padrão (True), o TestClient relança a exceção inesperada em vez
        de devolver a resposta. Queremos ver exatamente o que o navegador
        recebe: o 500 amigável.
        """
        cls.client = TestClient(app, raise_server_exceptions=False)

    def setUp(self):
        """Registro real temporário + espaço para trocar a IA em cada teste."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.service = RegistroFeedbackService(
            arquivo=Path(self._diretorio_temporario.name)
            / "registro_feedbacks.json"
        )

        app.dependency_overrides[obter_registro_feedbacks] = (
            lambda: self.service
        )
        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_feedbacks, None
        )
        self.addCleanup(
            app.dependency_overrides.pop, obter_llm_service, None
        )

    def _usar_llm(self, llm) -> None:
        """Aponta a dependência da IA para o dublê informado."""
        app.dependency_overrides[obter_llm_service] = lambda: llm

    def _gerar(self, vendedor_id: str = "C0031"):
        """Chama a rota de geração com o corpo mínimo."""
        return self.client.post(
            "/api/feedback/gerar", json={"vendedor_id": vendedor_id}
        )

    def test_vendedor_inexistente_ou_gerente_nao_chama_a_ia(self):
        """C9999 e C0030 dão 404 e o dublê nunca é chamado."""
        fake = LLMQueFalha(RuntimeError("não deveria ser chamada"))
        self._usar_llm(fake)

        for vendedor_id in ("C9999", "C0030"):
            with self.subTest(vendedor_id=vendedor_id):
                resposta = self._gerar(vendedor_id)

                self.assertEqual(resposta.status_code, 404)
                corpo = resposta.json()
                self.assertEqual(set(corpo), {"erro"})
                self.assertIn("não encontrado", corpo["erro"])

        self.assertEqual(fake.chamadas, 0)

    def test_ia_indisponivel_devolve_503_e_nao_registra(self):
        """Falha externa da IA vira 503, sem gravar nada."""
        self._usar_llm(
            LLMQueFalha(
                LLMIndisponivelError("Tempo esgotado ao falar com a IA.")
            )
        )

        resposta = self._gerar()

        self.assertEqual(resposta.status_code, 503)
        self.assertIn("Tempo esgotado", resposta.json()["erro"])

        # Nada foi gravado: o registro continua vazio.
        self.assertEqual(self.service.listar(), [])

    def test_resposta_invalida_da_ia_devolve_502_e_nao_registra(self):
        """Resposta ruim da IA vira 502, sem gravar nada."""
        self._usar_llm(
            LLMQueFalha(
                LLMRespostaInvalidaError("A IA devolveu um JSON inválido.")
            )
        )

        resposta = self._gerar()

        self.assertEqual(resposta.status_code, 502)
        self.assertIn("JSON inválido", resposta.json()["erro"])
        self.assertEqual(self.service.listar(), [])

    def test_ia_nao_configurada_devolve_500_sem_vazar_detalhes(self):
        """Sem chave, a resposta é 500 com texto fixo, sem chave nem caminhos."""
        self._usar_llm(
            LLMQueFalha(
                LLMNaoConfiguradoError(
                    "Copie backend/.env.example para backend/.env e preencha "
                    "DEEPSEEK_API_KEY."
                )
            )
        )

        resposta = self._gerar()

        self.assertEqual(resposta.status_code, 500)

        mensagem = resposta.json()["erro"]
        self.assertIn("não está configurado", mensagem)
        self.assertNotIn("DEEPSEEK", mensagem)
        self.assertNotIn(".env", mensagem)
        self.assertNotIn("backend", mensagem)
        self.assertNotIn("chave", mensagem.lower())

    def test_falha_ao_gravar_registro_devolve_500_claro(self):
        """Se a gravação falha, o erro aparece (não é escondido).

        É melhor avisar que o registro não foi salvo do que fingir sucesso:
        sem registro, a regional não acompanha os feedbacks preparados.
        """
        # IA ok para chegar até a gravação; o registro é que falha.
        self._usar_llm(LLMFunciona())

        registro_falho = RegistroQueFalha()
        app.dependency_overrides[obter_registro_feedbacks] = (
            lambda: registro_falho
        )

        resposta = self._gerar()

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(registro_falho.chamadas, 1)

        mensagem = resposta.json()["erro"]
        self.assertIn("Não foi possível carregar os dados", mensagem)

        # O caminho interno do disco NÃO aparece na resposta.
        self.assertNotIn("C:", mensagem)
        self.assertNotIn(".json", mensagem)

    def test_erro_inesperado_devolve_500_generico_sem_vazar_mensagem(self):
        """Exceção não prevista vira 500 genérico; o texto original não sai."""
        self._usar_llm(
            LLMQueFalha(RuntimeError("mensagem-secreta-do-servidor"))
        )

        # assertLogs captura o log do traceback e evita o barulho no console.
        with self.assertLogs("endpoints.erros", level="ERROR"):
            resposta = self._gerar()

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(
            resposta.json(), {"erro": "Erro interno do servidor."}
        )
        self.assertNotIn("mensagem-secreta-do-servidor", resposta.text)
