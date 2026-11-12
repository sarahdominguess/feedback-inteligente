"""Testes do endpoint GET /api/regional/desempenho-gerente.

Usam o app real, os CSVs reais e um registro TEMPORÁRIO compartilhado entre
as rotas (via dependency_overrides). Nenhum teste toca o registro real nem
chama a internet.
"""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from domain.feedback_roteiro import FeedbackRoteiro
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_llm_service,
    obter_registro_feedbacks,
)
from main import app
from services.registro_feedback import RegistroFeedbackService


class LLMFalso:
    """Dublê da IA: devolve um roteiro fixo, sem rede."""

    def gerar_roteiro_feedback(self, vendedor_id, mes_referencia=None):
        """Devolve um roteiro com as quatro listas preenchidas."""
        return FeedbackRoteiro(
            pontos_positivos=["Alta conversão"],
            pontos_melhoria=["Oferecer mais peças"],
            possiveis_motivos=["Correria no sábado"],
            roteiro_conversa=["Como foi o sábado?"],
        )


class TestDesempenhoRegional(unittest.TestCase):
    """Testes da visão executiva da regional."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente do app real uma vez."""
        cls.client = TestClient(app)

    def setUp(self):
        """Registro temporário compartilhado pelas rotas + IA falsa."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.service = RegistroFeedbackService(
            arquivo=Path(self._diretorio_temporario.name)
            / "registro_feedbacks.json"
        )
        self.llm = LLMFalso()

        app.dependency_overrides[obter_registro_feedbacks] = (
            lambda: self.service
        )
        app.dependency_overrides[obter_llm_service] = lambda: self.llm

        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_feedbacks, None
        )
        self.addCleanup(
            app.dependency_overrides.pop, obter_llm_service, None
        )

        # Limpa o consolidado em cache para cada teste começar do zero
        # (o cache é por par de dependências; o serviço muda a cada teste).
        obter_consolidado_regional.cache_clear()
        self.addCleanup(obter_consolidado_regional.cache_clear)

    def _desempenho(self) -> dict:
        """Chama a rota e devolve o JSON, exigindo status 200."""
        resposta = self.client.get("/api/regional/desempenho-gerente")
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()

    def test_estrutura_e_numeros_do_contrato(self):
        """A resposta traz todos os blocos do contrato com os dados reais.

        Outubro tem meta de 317.200 e a regional tem 5 anotações.
        """
        dados = self._desempenho()

        self.assertEqual(
            set(dados),
            {
                "gerente_id",
                "gerente_nome",
                "loja_id",
                "loja_nome",
                "periodo_inicio",
                "periodo_fim",
                "resultado_loja",
                "acompanhamento_feedback",
                "anotacoes_regional",
                "feedbacks_preparados",
            },
        )

        self.assertEqual(dados["gerente_nome"], "Diego Furtado")
        self.assertEqual(dados["loja_id"], "L004")

        self.assertEqual(len(dados["resultado_loja"]), 4)
        outubro = next(
            item
            for item in dados["resultado_loja"]
            if item["mes"] == "2026-10"
        )
        self.assertEqual(outubro["meta_loja"], 317200.0)

        self.assertEqual(len(dados["anotacoes_regional"]), 5)

        # Nenhum NaN/Infinity no texto bruto do JSON.
        resposta = self.client.get("/api/regional/desempenho-gerente")
        self.assertNotIn("NaN", resposta.text)
        self.assertNotIn("Infinity", resposta.text)

    def test_roteiro_gravado_aparece_no_acompanhamento(self):
        """Depois de gravar no serviço, a Bianca fica "com_roteiro"."""
        self.service.registrar(
            "C0031",
            "Bianca Rocha",
            "2026-10",
            FeedbackRoteiro(
                pontos_positivos=["Alta conversão"],
                pontos_melhoria=["Oferecer mais peças"],
                possiveis_motivos=["Correria"],
                roteiro_conversa=["Como foi o sábado?"],
            ),
        )

        acompanhamento = self._desempenho()["acompanhamento_feedback"]

        bianca = next(
            item
            for item in acompanhamento["vendedores"]
            if item["vendedor_id"] == "C0031"
        )
        self.assertEqual(bianca["situacao"], "com_roteiro")
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 1)
        self.assertEqual(acompanhamento["vendedores_com_roteiro"], 1)
        self.assertAlmostEqual(acompanhamento["cobertura"], 0.125)

    def test_gerar_feedback_e_ver_na_regional(self):
        """Integração entre rotas: o roteiro gerado aparece na regional.

        Isso prova que POST /api/feedback/gerar e GET
        /api/regional/desempenho-gerente usam o MESMO registro.
        """
        geracao = self.client.post(
            "/api/feedback/gerar",
            json={"vendedor_id": "C0031", "mes_referencia": "2026-10"},
        )
        self.assertEqual(geracao.status_code, 200, geracao.text)

        acompanhamento = self._desempenho()["acompanhamento_feedback"]

        bianca = next(
            item
            for item in acompanhamento["vendedores"]
            if item["vendedor_id"] == "C0031"
        )
        self.assertEqual(bianca["situacao"], "com_roteiro")
        self.assertEqual(bianca["roteiros_preparados"], 1)
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 1)
