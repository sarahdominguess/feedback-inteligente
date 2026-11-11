"""Testes do endpoint GET /api/vendedores/{loja_id}.

Usam o app real com TestClient e os CSVs reais de backend/data: o objetivo é
conferir a resposta que o frontend vai receber, sem simular dados.
"""

import unittest

from fastapi.testclient import TestClient

from config import DATA_DIR
from main import app
from services.data_loader import DataLoader


class TestListaVendedores(unittest.TestCase):
    """Testes da rota que lista os vendedores de uma loja."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente e lê a ordem esperada direto do DataLoader."""
        cls.client = TestClient(app)
        cls.loader = DataLoader(data_dir=DATA_DIR)

    def _lista(self, loja_id: str = "L004", **parametros) -> dict:
        """Chama a rota e devolve o JSON, exigindo status 200."""
        resposta = self.client.get(
            f"/api/vendedores/{loja_id}", params=parametros
        )
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()

    def _por_id(self, vendedores: list[dict], vendedor_id: str) -> dict:
        """Acha um vendedor na lista devolvida pela API."""
        for vendedor in vendedores:
            if vendedor["vendedor_id"] == vendedor_id:
                return vendedor
        self.fail(f"Vendedor {vendedor_id} não veio na resposta")

    def test_lista_tem_8_vendedores_sem_gerente(self):
        """A loja L004 tem 8 vendedores, na ordem do CSV, sem o gerente.

        O gerente (C0030) atende no caixa, mas não entra na lista de
        vendedores nem no comparativo do time.
        """
        dados = self._lista()

        self.assertEqual(dados["loja_id"], "L004")
        self.assertEqual(dados["loja_nome"], "Aurora Shopping Centro")
        self.assertIsNone(dados["mes"])

        vendedores = dados["vendedores"]
        self.assertEqual(len(vendedores), 8)
        self.assertNotIn("C0030", [v["vendedor_id"] for v in vendedores])
        self.assertTrue(
            all(v["cargo"] == "vendedor" for v in vendedores)
        )

        # A ordem da API é a mesma do arquivo (DataLoader).
        esperada = [
            vendedor.vendedor_id
            for vendedor in self.loader.listar_vendedores()
        ]
        self.assertEqual(
            [v["vendedor_id"] for v in vendedores], esperada
        )

    def test_metricas_da_bianca(self):
        """No histórico completo, a conversão da Bianca é ≈ 0,505 (50,5%)."""
        bianca = self._por_id(self._lista()["vendedores"], "C0031")

        self.assertAlmostEqual(
            bianca["metricas"]["conversao"], 0.505, delta=0.001
        )
        self.assertAlmostEqual(
            bianca["metricas"]["ticket_medio"], 206.3, delta=0.1
        )

    def test_comparativo_da_bianca(self):
        """Conversão é 1ª de 8 ("acima"); P.A. é 8ª de 8 ("abaixo")."""
        bianca = self._por_id(self._lista()["vendedores"], "C0031")

        por_nome = {
            metrica["nome"]: metrica
            for metrica in bianca["comparativo"]
        }

        self.assertEqual(len(por_nome), 3)

        conversao = por_nome["conversao"]
        self.assertEqual(conversao["posicao"], 1)
        self.assertEqual(conversao["total_vendedores"], 8)
        self.assertEqual(conversao["situacao"], "acima")

        pa = por_nome["pecas_por_atendimento"]
        self.assertEqual(pa["posicao"], 8)
        self.assertEqual(pa["situacao"], "abaixo")

    def test_mes_altera_os_valores(self):
        """?mes=2026-10 usa só outubro e devolve números diferentes do total.

        O valor vendido de outubro é menor que o de todo o histórico, então
        as métricas precisam mudar quando o mês é informado.
        """
        total = self._por_id(self._lista()["vendedores"], "C0031")
        outubro_json = self._lista(mes="2026-10")

        self.assertEqual(outubro_json["mes"], "2026-10")

        outubro = self._por_id(outubro_json["vendedores"], "C0031")
        self.assertLess(
            outubro["metricas"]["valor_vendido"],
            total["metricas"]["valor_vendido"],
        )

    def test_mes_invalido_devolve_400(self):
        """Mês fora de AAAA-MM vira 400 com {"erro": ...} legível."""
        resposta = self.client.get(
            "/api/vendedores/L004", params={"mes": "2026-13"}
        )

        self.assertEqual(resposta.status_code, 400)

        corpo = resposta.json()
        self.assertEqual(set(corpo), {"erro"})
        self.assertIn("mes", corpo["erro"])
        self.assertIn("formato inválido", corpo["erro"])

    def test_loja_inexistente_devolve_404(self):
        """Loja diferente da configurada vira 404 com a mensagem da exceção."""
        resposta = self.client.get("/api/vendedores/L999")

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            resposta.json(), {"erro": "Loja 'L999' não encontrada."}
        )

    def test_loja_em_minusculas_funciona(self):
        """O código da loja é comparado sem diferenciar maiúsculas."""
        resposta = self.client.get("/api/vendedores/l004")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["loja_id"], "L004")

    def test_resposta_nao_tem_nan(self):
        """O JSON bruto não contém NaN nem Infinity (valores vazios = null)."""
        resposta = self.client.get("/api/vendedores/L004")

        self.assertNotIn("NaN", resposta.text)
        self.assertNotIn("Infinity", resposta.text)
