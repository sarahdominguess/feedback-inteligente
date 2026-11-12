"""Testes do POST /api/regional/feedback/gerar.

A IA é um dublê trocado via dependency_overrides; os registros (vendedores e
gerente) apontam para pastas temporárias. Nenhum teste chama a internet nem
toca nos arquivos reais de backend/data.
"""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from domain.excecoes import (
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
)
from domain.feedback_roteiro import FeedbackRoteiro
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_data_loader,
    obter_llm_service,
    obter_registro_feedbacks,
    obter_registro_feedbacks_regional,
)
from main import app
from services.data_loader import DataLoader
from services.registro_feedback import RegistroFeedbackService
from services.registro_feedback_regional import RegistroFeedbackRegionalService


def roteiro_valido() -> FeedbackRoteiro:
    """Devolve um roteiro simples com as quatro listas preenchidas."""
    return FeedbackRoteiro(
        pontos_positivos=["Loja organizada e time engajado"],
        pontos_melhoria=["Delegar o caixa no horário de pico"],
        possiveis_motivos=["Movimento concentrado no almoço"],
        roteiro_conversa=[
            "Como foi a semana com o time?",
            "O que ajudaria a delegar mais?",
            "Que combinado fazemos para amanhã?",
        ],
    )


class LLMFalso:
    """Dublê da IA que devolve um roteiro fixo e guarda as chamadas."""

    def __init__(self):
        self.chamadas = []

    def gerar_roteiro_feedback_gerente(self, desempenho, mes_referencia=None):
        """Registra os argumentos e devolve um roteiro válido."""
        self.chamadas.append(
            {"desempenho": desempenho, "mes_referencia": mes_referencia}
        )
        return roteiro_valido()


class LLMQueFalha:
    """Dublê da IA que só levanta a exceção programada."""

    def __init__(self, erro: Exception):
        self.erro = erro
        self.chamadas = 0

    def gerar_roteiro_feedback_gerente(self, desempenho, mes_referencia=None):
        """Conta a chamada e levanta o erro programado (nada é gravado)."""
        self.chamadas += 1
        raise self.erro


class TestGeracaoDeFeedbackParaOGerente(unittest.TestCase):
    """Testes do caminho feliz, das validações e das falhas da IA."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente do app real uma vez."""
        cls.client = TestClient(app)

    def setUp(self):
        """Serviços temporários, DataLoader simples e espaço para a IA."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)
        diretorio = Path(self._diretorio_temporario.name)

        self.registro_vendedores = RegistroFeedbackService(
            arquivo=diretorio / "registro_feedbacks.json"
        )
        self.registro_regional = RegistroFeedbackRegionalService(
            arquivo=diretorio / "registro_feedbacks_regional.json"
        )

        app.dependency_overrides[obter_data_loader] = lambda: DataLoader()
        app.dependency_overrides[obter_registro_feedbacks] = (
            lambda: self.registro_vendedores
        )
        app.dependency_overrides[obter_registro_feedbacks_regional] = (
            lambda: self.registro_regional
        )

        # Cada teste escolhe a IA que quer usar (feliz ou com falha).
        self.addCleanup(app.dependency_overrides.pop, obter_data_loader, None)
        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_feedbacks, None
        )
        self.addCleanup(
            app.dependency_overrides.pop,
            obter_registro_feedbacks_regional,
            None,
        )
        self.addCleanup(
            app.dependency_overrides.pop, obter_llm_service, None
        )

        # O consolidado guarda o resultado em cache por par de dependências;
        # como as dependências mudam a cada teste, limpamos.
        obter_consolidado_regional.cache_clear()
        self.addCleanup(obter_consolidado_regional.cache_clear)

    def _usar_llm(self, llm) -> None:
        """Aponta a dependência da IA para o dublê informado."""
        app.dependency_overrides[obter_llm_service] = lambda: llm

    def _gerar(self, corpo):
        """Faz o POST na rota de geração e devolve a resposta crua."""
        return self.client.post("/api/regional/feedback/gerar", json=corpo)

    def _historico(self) -> dict:
        """Busca o histórico da loja e devolve o JSON, exigindo 200."""
        resposta = self.client.get("/api/regional/lojas/L004/historico")
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()

    def _acompanhamento(self) -> dict:
        """Busca o consolidado e devolve o bloco de acompanhamento."""
        resposta = self.client.get("/api/regional/desempenho-gerente")
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()["acompanhamento_feedback"]

    # -----------------------------------------------------------------
    # Caminho feliz
    # -----------------------------------------------------------------

    def test_caminho_feliz_grava_e_devolve_o_roteiro(self):
        """200 com as quatro listas; o roteiro fica no registro da regional."""
        llm = LLMFalso()
        self._usar_llm(llm)

        resposta = self._gerar(
            {"loja_id": "L004", "mes_referencia": "2026-10"}
        )

        self.assertEqual(resposta.status_code, 200, resposta.text)
        dados = resposta.json()

        self.assertEqual(dados["loja_id"], "L004")
        self.assertEqual(dados["loja_nome"], "Aurora Shopping Centro")
        self.assertEqual(dados["gerente_id"], "C0030")
        self.assertEqual(dados["gerente_nome"], "Diego Furtado")
        self.assertEqual(dados["mes_referencia"], "2026-10")
        self.assertEqual(
            set(dados["roteiro"]),
            {
                "pontos_positivos",
                "pontos_melhoria",
                "possiveis_motivos",
                "roteiro_conversa",
            },
        )
        self.assertEqual(
            dados["roteiro"]["pontos_positivos"],
            ["Loja organizada e time engajado"],
        )

        # A IA recebeu o consolidado da loja e o mês pedido.
        self.assertEqual(len(llm.chamadas), 1)
        self.assertEqual(llm.chamadas[0]["desempenho"]["loja_id"], "L004")
        self.assertEqual(llm.chamadas[0]["mes_referencia"], "2026-10")

        # O roteiro foi gravado no registro DA REGIONAL.
        registros = self.registro_regional.listar("L004")
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].feedback_id, dados["feedback_id"])

    def test_roteiro_aparece_no_historico_da_loja(self):
        """Depois de gerar, o roteiro entra em feedbacks_preparados."""
        self._usar_llm(LLMFalso())

        self._gerar({"loja_id": "L004"})

        preparados = self._historico()["feedbacks_preparados"]
        self.assertEqual(len(preparados), 1)
        self.assertEqual(
            preparados[0]["roteiro"]["roteiro_conversa"],
            [
                "Como foi a semana com o time?",
                "O que ajudaria a delegar mais?",
                "Que combinado fazemos para amanhã?",
            ],
        )

    # -----------------------------------------------------------------
    # Validações antes da IA
    # -----------------------------------------------------------------

    def test_mes_em_formato_invalido_devolve_400(self):
        """Mês fora de AAAA-MM é recusado antes de qualquer chamada."""
        llm = LLMFalso()
        self._usar_llm(llm)

        resposta = self._gerar(
            {"loja_id": "L004", "mes_referencia": "2026-13"}
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(llm.chamadas, [])
        self.assertEqual(self.registro_regional.listar(), [])

    def test_loja_desconhecida_devolve_404_sem_chamar_a_ia(self):
        """Loja fora da configuração dá 404 e o dublê nunca é chamado."""
        llm = LLMFalso()
        self._usar_llm(llm)

        resposta = self._gerar({"loja_id": "L999"})

        self.assertEqual(resposta.status_code, 404)
        corpo = resposta.json()
        self.assertEqual(set(corpo), {"erro"})
        self.assertIn("L999", corpo["erro"])
        self.assertEqual(llm.chamadas, [])
        self.assertEqual(self.registro_regional.listar(), [])

    # -----------------------------------------------------------------
    # Falhas da IA
    # -----------------------------------------------------------------

    def test_falhas_da_ia_devolvem_o_status_certo_e_nao_gravam(self):
        """Cada erro de LLM existente vira 500/502/503, sem gravar nada."""
        casos = [
            (
                "indisponivel",
                LLMIndisponivelError("Tempo esgotado ao falar com a IA."),
                503,
            ),
            (
                "resposta_invalida",
                LLMRespostaInvalidaError("A IA devolveu um JSON inválido."),
                502,
            ),
            (
                "nao_configurada",
                LLMNaoConfiguradoError("A chave da API não está configurada."),
                500,
            ),
        ]

        for nome, erro, status in casos:
            with self.subTest(caso=nome):
                llm = LLMQueFalha(erro)
                self._usar_llm(llm)

                resposta = self._gerar({"loja_id": "L004"})

                self.assertEqual(resposta.status_code, status, resposta.text)
                self.assertIn("erro", resposta.json())
                self.assertEqual(llm.chamadas, 1)
                self.assertEqual(self.registro_regional.listar(), [])

    # -----------------------------------------------------------------
    # Isolamento do registro dos vendedores
    # -----------------------------------------------------------------

    def test_gerar_para_o_gerente_nao_muda_o_registro_dos_vendedores(self):
        """O roteiro do gerente não entra na cobertura dos vendedores."""
        self._usar_llm(LLMFalso())

        antes = self._acompanhamento()
        self.assertEqual(antes["total_roteiros_preparados"], 0)
        self.assertEqual(antes["vendedores_com_roteiro"], 0)
        self.assertEqual(antes["cobertura"], 0.0)

        self._gerar({"loja_id": "L004", "mes_referencia": "2026-10"})

        depois = self._acompanhamento()
        self.assertEqual(depois, antes)
        self.assertEqual(self.registro_vendedores.listar(), [])
        self.assertEqual(len(self.registro_regional.listar()), 1)


if __name__ == "__main__":
    unittest.main()
