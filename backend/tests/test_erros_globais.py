"""Testes do tratamento global de erros da API.

Criam um app de teste (FastAPI + tratadores + rotas temporárias que levantam
cada exceção) e conferem status e corpo de cada resposta. TestClient é um
cliente de mentira: chama a API em memória, sem abrir porta de rede.
"""

import re
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from domain.excecoes import (
    DadosIndisponiveisError,
    DominioError,
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
    LojaNaoEncontradaError,
    VendedorNaoEncontradoError,
)
from endpoints.erros import registrar_tratadores_de_erro


class EntradaTeste(BaseModel):
    """Modelo mínimo só para provocar um erro de validação (400)."""

    vendedor_id: str
    mes_referencia: str | None = None

    @field_validator("mes_referencia")
    @classmethod
    def _validar_mes(cls, valor: str | None) -> str | None:
        """Mesma regra do contrato real: mês no formato AAAA-MM."""
        if valor is None:
            return None
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", valor):
            raise ValueError(
                'O mês deve estar no formato "AAAA-MM" (ex.: "2026-10").'
            )
        return valor


def criar_app_de_teste() -> FastAPI:
    """Monta um app com os tratadores e uma rota para cada tipo de erro.

    Cada rota faz só `raise ...`: o objetivo é ver como o tratador devolve
    isso ao cliente, sem envolver dados reais.
    """
    app = FastAPI()
    registrar_tratadores_de_erro(app)

    @app.get("/vendedor-inexistente")
    def vendedor_inexistente():
        raise VendedorNaoEncontradoError(
            "Vendedor com ID 'C9999' não encontrado."
        )

    @app.get("/loja-inexistente")
    def loja_inexistente():
        raise LojaNaoEncontradaError("Loja 'L999' não encontrada.")

    @app.get("/dados-indisponiveis")
    def dados_indisponiveis():
        # Mensagem interna com caminho de arquivo: não pode sair na resposta.
        raise DadosIndisponiveisError(
            "Arquivo de dados não encontrado: C:\\dados\\secreto.csv"
        )

    @app.get("/erro-de-dominio")
    def erro_de_dominio():
        raise DominioError("Falha de negócio qualquer.")

    @app.get("/llm-indisponivel")
    def llm_indisponivel():
        raise LLMIndisponivelError("Tempo esgotado ao falar com a IA.")

    @app.get("/llm-resposta-invalida")
    def llm_resposta_invalida():
        raise LLMRespostaInvalidaError("A IA devolveu um JSON inválido.")

    @app.get("/llm-nao-configurado")
    def llm_nao_configurado():
        # Mensagem interna citando o arquivo .env e a variável da chave.
        raise LLMNaoConfiguradoError(
            "Copie backend/.env.example para backend/.env e preencha "
            "DEEPSEEK_API_KEY."
        )

    @app.post("/validar")
    def validar(entrada: EntradaTeste):
        return {"ok": True}

    @app.get("/metodo-errado")
    def metodo_errado():
        return {"ok": True}

    @app.get("/explode")
    def explode():
        raise RuntimeError("detalhe secreto que não pode vazar")

    return app


class TestErrosGlobais(unittest.TestCase):
    """Testes de status e corpo de cada tratador."""

    @classmethod
    def setUpClass(cls):
        """Cria o app e o cliente uma vez para todos os testes.

        raise_server_exceptions=False: com o padrão (True), o TestClient
        relança a exceção em vez de devolver a resposta de erro. Como aqui
        queremos justamente ver a resposta que o navegador receberia,
        desligamos o relançamento.
        """
        cls.client = TestClient(
            criar_app_de_teste(), raise_server_exceptions=False
        )

    def _corpo(self, resposta) -> dict:
        """Devolve o JSON da resposta, garantindo o formato {"erro": ...}."""
        corpo = resposta.json()
        self.assertEqual(set(corpo), {"erro"})
        return corpo

    def test_vendedor_nao_encontrado_404(self):
        """Vendedor inexistente vira 404 com a mensagem da exceção."""
        resposta = self.client.get("/vendedor-inexistente")

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            self._corpo(resposta)["erro"],
            "Vendedor com ID 'C9999' não encontrado.",
        )

    def test_loja_nao_encontrada_404(self):
        """Loja inexistente também vira 404."""
        resposta = self.client.get("/loja-inexistente")

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            self._corpo(resposta)["erro"], "Loja 'L999' não encontrada."
        )

    def test_llm_indisponivel_503(self):
        """Falha temporária da IA vira 503 (tente de novo mais tarde)."""
        resposta = self.client.get("/llm-indisponivel")

        self.assertEqual(resposta.status_code, 503)
        self.assertIn("Tempo esgotado", self._corpo(resposta)["erro"])

    def test_llm_resposta_invalida_502(self):
        """Resposta inválida da IA vira 502 (o provedor respondeu mal)."""
        resposta = self.client.get("/llm-resposta-invalida")

        self.assertEqual(resposta.status_code, 502)
        self.assertIn("JSON inválido", self._corpo(resposta)["erro"])

    def test_llm_nao_configurado_500_sem_vazar_detalhes(self):
        """IA sem configuração vira 500 com texto fixo, sem .env nem chave."""
        resposta = self.client.get("/llm-nao-configurado")

        self.assertEqual(resposta.status_code, 500)

        mensagem = self._corpo(resposta)["erro"]
        self.assertIn("não está configurado", mensagem)

        # Nada de caminho de arquivo ou nome da variável da chave.
        self.assertNotIn(".env", mensagem)
        self.assertNotIn("DEEPSEEK", mensagem)
        self.assertNotIn("backend", mensagem)

    def test_dados_indisponiveis_500_sem_vazar_caminho(self):
        """Falha ao ler dados vira 500 sem mostrar o caminho do arquivo."""
        resposta = self.client.get("/dados-indisponiveis")

        self.assertEqual(resposta.status_code, 500)

        mensagem = self._corpo(resposta)["erro"]
        self.assertIn("Não foi possível carregar os dados", mensagem)
        self.assertNotIn("C:", mensagem)
        self.assertNotIn(".csv", mensagem)

    def test_dominio_generico_500(self):
        """Qualquer outro erro de negócio vira 500 com texto genérico."""
        resposta = self.client.get("/erro-de-dominio")

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(
            self._corpo(resposta)["erro"],
            "Não foi possível concluir a operação.",
        )

    def test_validacao_vira_400_legivel(self):
        """Mês inválido vira 400 com campo e problema, sem estrutura técnica."""
        resposta = self.client.post(
            "/validar",
            json={"vendedor_id": "C0031", "mes_referencia": "2026-13"},
        )

        self.assertEqual(resposta.status_code, 400)

        mensagem = self._corpo(resposta)["erro"]
        self.assertIn("mes_referencia", mensagem)
        self.assertIn("AAAA-MM", mensagem)

        # Nada da estrutura interna do Pydantic.
        self.assertNotIn("loc", mensagem)
        self.assertNotIn("input", mensagem)
        self.assertNotIn("Value error", mensagem)

    def test_campo_obrigatorio_faltando_vira_400(self):
        """Campo obrigatório ausente aparece como "campo obrigatório"."""
        resposta = self.client.post(
            "/validar", json={"mes_referencia": "2026-10"}
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(
            self._corpo(resposta)["erro"],
            "vendedor_id: campo obrigatório",
        )

    def test_rota_inexistente_devolve_404_em_portugues(self):
        """Rota que não existe mantém o 404, mas com mensagem em português."""
        resposta = self.client.get("/rota-que-nao-existe")

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            self._corpo(resposta)["erro"], "Recurso não encontrado."
        )

    def test_metodo_errado_devolve_405_em_portugues(self):
        """Método não permitido mantém o 405, com mensagem em português."""
        resposta = self.client.post("/metodo-errado")

        self.assertEqual(resposta.status_code, 405)
        self.assertEqual(
            self._corpo(resposta)["erro"],
            "Método não permitido para esta rota.",
        )

    def test_erro_inesperado_500_sem_vazar_mensagem(self):
        """Erro não previsto vira 500 genérico e o traceback vai só para o log."""
        # assertLogs captura o registro do logger e evita que o traceback
        # apareça no console do teste.
        with self.assertLogs("endpoints.erros", level="ERROR") as registro:
            resposta = self.client.get("/explode")

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(
            self._corpo(resposta)["erro"], "Erro interno do servidor."
        )

        # A mensagem original não aparece nem na resposta nem no log.
        self.assertNotIn("secreto", resposta.text)
        self.assertTrue(
            any(
                "Erro interno não tratado" in linha
                for linha in registro.output
            )
        )
