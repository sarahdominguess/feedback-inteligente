"""Teste de integração do perfil da Bianca com os CSVs reais do desafio.

Confere, com tolerância, os números esperados do histórico completo: alta
conversão (1ª do time) e P.A. e ticket médio abaixo dos colegas (8ª posição).
"""

import unittest

from config import DATA_DIR
from services.data_loader import DataLoader


class TestIntegracaoBianca(unittest.TestCase):
    """Compara a Bianca real (C0031) com a média dos 8 vendedores."""

    @classmethod
    def setUpClass(cls):
        """Carrega os CSVs reais uma única vez para todos os testes."""
        cls.loader = DataLoader(data_dir=DATA_DIR)
        cls.bianca = cls.loader.buscar_vendedor_por_nome("Bianca")
        cls.comparativo = cls.loader.obter_comparativo_time("C0031")

    def _metrica(self, nome: str):
        """Devolve a MetricaComparada com o nome pedido.

        Se o nome não existir, o teste falha com uma mensagem clara em vez de
        um erro obscuro de índice.
        """
        for metrica in self.comparativo.metricas:
            if metrica.nome == nome:
                return metrica
        raise AssertionError(f"Métrica não encontrada no comparativo: {nome}")

    def test_identificacao_da_bianca(self):
        """A busca por primeiro nome encontra a Bianca e usa todo o histórico."""
        self.assertEqual(self.bianca.vendedor_id, "C0031")
        self.assertEqual(self.bianca.nome, "Bianca Rocha")
        self.assertIsNone(self.comparativo.mes)
        self.assertEqual(self.comparativo.vendedor_id, "C0031")

    def test_conversao_acima_do_time(self):
        """Conversão ≈ 0,505: melhor do time (1ª de 8), situação "acima"."""
        metrica = self._metrica("conversao")

        self.assertAlmostEqual(metrica.valor, 0.505, delta=0.001)
        self.assertEqual(metrica.posicao, 1)
        self.assertEqual(metrica.total_vendedores, 8)
        self.assertEqual(metrica.situacao, "acima")

    def test_pa_abaixo_do_time(self):
        """P.A. ≈ 1,224 contra média ≈ 1,755: 8ª de 8, situação "abaixo"."""
        metrica = self._metrica("pecas_por_atendimento")

        self.assertAlmostEqual(metrica.valor, 1.224, delta=0.001)
        self.assertAlmostEqual(metrica.media_time, 1.755, delta=0.001)
        self.assertEqual(metrica.posicao, 8)
        self.assertEqual(metrica.total_vendedores, 8)
        self.assertEqual(metrica.situacao, "abaixo")

    def test_ticket_medio_abaixo_do_time(self):
        """Ticket ≈ R$ 206,3 contra média ≈ R$ 303,8: 8ª de 8, "abaixo"."""
        metrica = self._metrica("ticket_medio")

        self.assertAlmostEqual(metrica.valor, 206.3, delta=0.1)
        self.assertAlmostEqual(metrica.media_time, 303.8, delta=0.1)
        self.assertEqual(metrica.posicao, 8)
        self.assertEqual(metrica.total_vendedores, 8)
        self.assertEqual(metrica.situacao, "abaixo")

    def test_atingimento_da_meta_em_outubro(self):
        """Em outubro de 2026, a Bianca atingiu ≈ 1,124 (112,4% da meta)."""
        self.assertAlmostEqual(
            self.bianca.atingimento_meta("2026-10"), 1.124, delta=0.001
        )
