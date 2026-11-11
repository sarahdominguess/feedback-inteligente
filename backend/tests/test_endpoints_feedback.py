"""Testes do endpoint POST /api/feedback/gerar.

A IA é substituída por um falso (dependency_overrides), então NENHUM teste
chama a internet. O registro também vai para um arquivo temporário.
"""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from domain.feedback_roteiro import FeedbackRoteiro
from endpoints.dependencias import obter_llm_service, obter_registro_feedbacks
from main import app
from services.registro_feedback import RegistroFeedbackService


class LLMFalso:
    """Dublê do LLMService: devolve um roteiro fixo e anota as chamadas.

    Dublê (ou "fake") é um objeto de mentira usado no teste no lugar do
    serviço real. Assim o teste é rápido, gratuito e não depende da internet.
    Só implementamos o método que a rota usa.
    """

    def __init__(self):
        # Lista de (vendedor_id, mes_referencia) recebidos, na ordem.
        self.chamadas = []

    def gerar_roteiro_feedback(self, vendedor_id, mes_referencia=None):
        """Guarda os argumentos e devolve um roteiro sempre válido."""
        self.chamadas.append((vendedor_id, mes_referencia))
        return FeedbackRoteiro(
            pontos_positivos=["Alta conversão com as clientes"],
            pontos_melhoria=["Vender mais de uma peça por atendimento"],
            possiveis_motivos=["Correria no sábado"],
            roteiro_conversa=[
                "Como foi o seu sábado mais cheio?",
                "O que te ajudaria a oferecer mais peças?",
                "O que você mudaria no próximo sábado?",
            ],
        )


class TestGerarFeedback(unittest.TestCase):
    """Testes da geração de feedback com IA falsa e registro temporário."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente do app real uma vez."""
        cls.client = TestClient(app)

    def setUp(self):
        """Troca IA e registro por versões de teste, só durante este teste."""
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

    def test_gera_roteiro_e_grava_registro(self):
        """A resposta traz as 4 listas, id, horário e um registro é gravado.

        O dublê precisa receber exatamente o ID pedido e mês None (todo o
        histórico).
        """
        resposta = self.client.post(
            "/api/feedback/gerar", json={"vendedor_id": "C0031"}
        )

        self.assertEqual(resposta.status_code, 200, resposta.text)
        dados = resposta.json()

        self.assertEqual(
            set(dados),
            {
                "feedback_id",
                "vendedor_id",
                "vendedor_nome",
                "mes_referencia",
                "gerado_em",
                "roteiro",
            },
        )
        self.assertEqual(dados["vendedor_id"], "C0031")
        self.assertEqual(dados["vendedor_nome"], "Bianca Rocha")
        self.assertIsNone(dados["mes_referencia"])
        self.assertTrue(dados["feedback_id"])
        self.assertTrue(dados["gerado_em"])

        # As quatro listas vêm preenchidas (o roteiro do dublê).
        roteiro = dados["roteiro"]
        self.assertEqual(
            set(roteiro),
            {
                "pontos_positivos",
                "pontos_melhoria",
                "possiveis_motivos",
                "roteiro_conversa",
            },
        )
        self.assertTrue(all(len(itens) > 0 for itens in roteiro.values()))

        # O dublê recebeu os argumentos certos e só uma vez.
        self.assertEqual(self.llm.chamadas, [("C0031", None)])

        # E o registro local ficou com 1 item.
        registros = self.service.listar("C0031")
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].feedback_id, dados["feedback_id"])

    def test_com_mes_referencia(self):
        """Com mês informado, ele chega ao serviço de IA e vai ao registro."""
        resposta = self.client.post(
            "/api/feedback/gerar",
            json={"vendedor_id": "C0031", "mes_referencia": "2026-10"},
        )

        self.assertEqual(resposta.status_code, 200, resposta.text)
        self.assertEqual(resposta.json()["mes_referencia"], "2026-10")

        self.assertEqual(self.llm.chamadas, [("C0031", "2026-10")])
        self.assertEqual(
            self.service.listar("C0031")[0].mes_referencia, "2026-10"
        )

    def test_duas_geracoes_criam_ids_diferentes(self):
        """Gerar duas vezes cria dois registros distintos, com ids únicos."""
        primeira = self.client.post(
            "/api/feedback/gerar", json={"vendedor_id": "C0031"}
        ).json()
        segunda = self.client.post(
            "/api/feedback/gerar", json={"vendedor_id": "C0031"}
        ).json()

        self.assertNotEqual(primeira["feedback_id"], segunda["feedback_id"])
        self.assertEqual(len(self.service.listar("C0031")), 2)

    def test_historico_passa_a_listar_o_feedback_gerado(self):
        """Depois de gerar, o histórico da Bianca mostra o roteiro preparado."""
        gerado = self.client.post(
            "/api/feedback/gerar",
            json={"vendedor_id": "C0031", "mes_referencia": "2026-10"},
        ).json()

        historico = self.client.get(
            "/api/vendedores/C0031/historico"
        ).json()

        preparados = historico["feedbacks_preparados"]
        self.assertEqual(len(preparados), 1)
        self.assertEqual(preparados[0]["feedback_id"], gerado["feedback_id"])
        self.assertEqual(preparados[0]["mes_referencia"], "2026-10")

    def test_corpo_sem_vendedor_id_devolve_400(self):
        """Faltando vendedor_id, o erro é 400 com mensagem em português."""
        resposta = self.client.post("/api/feedback/gerar", json={})

        self.assertEqual(resposta.status_code, 400)
        corpo = resposta.json()
        self.assertEqual(set(corpo), {"erro"})
        self.assertIn("vendedor_id", corpo["erro"])
        self.assertIn("campo obrigatório", corpo["erro"])

        # Nada foi gerado nem gravado.
        self.assertEqual(self.llm.chamadas, [])
        self.assertEqual(self.service.listar(), [])

    def test_mes_invalido_devolve_400(self):
        """Mês fora de AAAA-MM é recusado antes de qualquer chamada à IA."""
        resposta = self.client.post(
            "/api/feedback/gerar",
            json={"vendedor_id": "C0031", "mes_referencia": "2026-13"},
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("mes_referencia", resposta.json()["erro"])
        self.assertEqual(self.llm.chamadas, [])

    def test_vendedor_inexistente_nao_chama_a_ia(self):
        """ID desconhecido ou do gerente dá 404 sem gastar chamada de IA."""
        for vendedor_id in ("C9999", "C0030"):
            with self.subTest(vendedor_id=vendedor_id):
                resposta = self.client.post(
                    "/api/feedback/gerar", json={"vendedor_id": vendedor_id}
                )

                self.assertEqual(resposta.status_code, 404)
                self.assertEqual(set(resposta.json()), {"erro"})

        # O dublê nunca foi chamado e nada foi gravado.
        self.assertEqual(self.llm.chamadas, [])
        self.assertEqual(self.service.listar(), [])
