"""Testes do endpoint GET /api/vendedores/{vendedor_id}/historico.

Usam o app real, os CSVs reais e um RegistroFeedbackService apontando para um
arquivo TEMPORÁRIO, trocado via dependency_overrides (nenhum teste toca no
registro real do projeto).
"""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from domain.feedback_roteiro import FeedbackRoteiro
from endpoints.dependencias import obter_registro_feedbacks
from main import app
from services.registro_feedback import RegistroFeedbackService


class TestHistoricoVendedor(unittest.TestCase):
    """Testes da rota de histórico individual."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente uma vez (o app real)."""
        cls.client = TestClient(app)

    def setUp(self):
        """Troca o registro real por um temporário, só durante este teste.

        dependency_overrides é o "gancho" do FastAPI para substituir uma
        dependência: a rota continua pedindo obter_registro_feedbacks, mas
        recebe o nosso serviço de teste. No fim, addCleanup remove a troca.
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.service = RegistroFeedbackService(
            arquivo=Path(self._diretorio_temporario.name)
            / "registro_feedbacks.json"
        )
        app.dependency_overrides[obter_registro_feedbacks] = lambda: self.service
        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_feedbacks, None
        )

    def test_bianca_tem_quatro_meses_e_novembro_parcial(self):
        """O resumo mensal traz 2026-08 a 2026-11, com novembro parcial.

        Novembro tem apenas 1 dia com dados, então o aviso de mês parcial é
        essencial para não comparar um mês incompleto com um mês cheio.
        """
        resposta = self.client.get("/api/vendedores/C0031/historico")

        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()

        self.assertEqual(dados["vendedor_id"], "C0031")
        self.assertEqual(dados["nome"], "Bianca Rocha")
        self.assertEqual(dados["cargo"], "vendedor")

        meses = [item["mes"] for item in dados["resumo_mensal"]]
        self.assertEqual(
            meses, ["2026-08", "2026-09", "2026-10", "2026-11"]
        )

        por_mes = {
            item["mes"]: item for item in dados["resumo_mensal"]
        }
        self.assertTrue(por_mes["2026-11"]["mes_parcial"])
        self.assertFalse(por_mes["2026-10"]["mes_parcial"])

    def test_anotacoes_dela_e_do_time_ficam_separadas(self):
        """3 anotações sobre a Bianca e 2 sobre o time, sem outras pessoas.

        As anotações sobre colegas não podem aparecer no histórico dela:
        seriam um vazamento de assunto de outra pessoa.
        """
        dados = self.client.get("/api/vendedores/C0031/historico").json()

        self.assertEqual(len(dados["anotacoes"]), 3)
        self.assertEqual(
            {anotacao["sobre"] for anotacao in dados["anotacoes"]},
            {"Bianca Rocha"},
        )

        self.assertEqual(len(dados["anotacoes_do_time"]), 2)
        self.assertTrue(
            all(
                anotacao["e_do_time"]
                for anotacao in dados["anotacoes_do_time"]
            )
        )

    def test_feedbacks_preparados_comeca_vazio_e_recebe_um(self):
        """Sem registro, a lista vem vazia; após registrar, vem 1 resumo.

        O resumo tem só id, mês e horário: o TEXTO do roteiro não entra no
        histórico.
        """
        vazio = self.client.get("/api/vendedores/C0031/historico").json()
        self.assertEqual(vazio["feedbacks_preparados"], [])

        registro = self.service.registrar(
            "C0031",
            "Bianca Rocha",
            "2026-10",
            FeedbackRoteiro(
                pontos_positivos=["texto único que não deve aparecer"],
                pontos_melhoria=["outro texto"],
                possiveis_motivos=["mais um"],
                roteiro_conversa=["pergunta?"],
            ),
        )

        resposta = self.client.get("/api/vendedores/C0031/historico")
        dados = resposta.json()

        self.assertEqual(len(dados["feedbacks_preparados"]), 1)

        resumo = dados["feedbacks_preparados"][0]
        self.assertEqual(
            set(resumo), {"feedback_id", "mes_referencia", "gerado_em"}
        )
        self.assertEqual(resumo["feedback_id"], registro.feedback_id)
        self.assertEqual(resumo["mes_referencia"], "2026-10")

        # O conteúdo do roteiro NÃO pode ter vazado para a resposta.
        self.assertNotIn("texto único que não deve aparecer", resposta.text)

    def test_gerente_e_id_inexistente_devolvem_404(self):
        """C0030 (gerente) e um ID qualquer não são vendedores: 404."""
        for vendedor_id in ("C0030", "XXXX"):
            with self.subTest(vendedor_id=vendedor_id):
                resposta = self.client.get(
                    f"/api/vendedores/{vendedor_id}/historico"
                )

                self.assertEqual(resposta.status_code, 404)
                corpo = resposta.json()
                self.assertEqual(set(corpo), {"erro"})
                self.assertIn("não encontrado", corpo["erro"])

    def test_resposta_nao_tem_nan(self):
        """O JSON bruto não contém NaN nem Infinity."""
        resposta = self.client.get("/api/vendedores/C0031/historico")

        self.assertNotIn("NaN", resposta.text)
        self.assertNotIn("Infinity", resposta.text)

    def test_as_duas_rotas_do_arquivo_convivem(self):
        """A rota de um segmento e a de dois segmentos não conflitam.

        /api/vendedores/L004 continua respondendo a lista, e
        /api/vendedores/C0031 (um segmento) é tratado como LOJA inexistente,
        não como histórico.
        """
        lista = self.client.get("/api/vendedores/L004")
        self.assertEqual(lista.status_code, 200)
        self.assertEqual(len(lista.json()["vendedores"]), 8)

        um_segmento = self.client.get("/api/vendedores/C0031")
        self.assertEqual(um_segmento.status_code, 404)
        self.assertEqual(
            um_segmento.json(), {"erro": "Loja 'C0031' não encontrada."}
        )
