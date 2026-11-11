"""Testes dos mapeadores de domínio para DTO.

Usam os CSVs reais (Bianca, C0031) para provar que a tradução não altera
nenhum número: os valores do DTO precisam bater com os do domínio.
"""

import unittest
from datetime import date

from config import DATA_DIR
from contracts.mapeadores import (
    anotacao_de,
    comparativo_de,
    metricas_de,
    resumo_mensal_de,
    roteiro_de,
)
from domain.anotacao import Anotacao
from domain.feedback_roteiro import FeedbackRoteiro
from services.data_loader import DataLoader


class TestMapeadoresComDadosReais(unittest.TestCase):
    """Testes dos mapeadores contra os dados reais da Bianca."""

    @classmethod
    def setUpClass(cls):
        """Carrega os CSVs uma vez e guarda a Bianca para todos os testes."""
        cls.loader = DataLoader(data_dir=DATA_DIR)
        cls.bianca = cls.loader.buscar_vendedor_por_nome("Bianca")

    def test_metricas_da_bianca(self):
        """As métricas do DTO são as mesmas do domínio, sem recálculo.

        No histórico completo: conversão ≈ 0,505 (50,5%) e ticket médio
        ≈ R$ 206,30. Os demais campos devem ser idênticos aos métodos do
        Vendedor.
        """
        metricas = metricas_de(self.bianca)

        self.assertAlmostEqual(metricas.conversao, 0.505, delta=0.001)
        self.assertAlmostEqual(metricas.ticket_medio, 206.3, delta=0.1)

        # Mesma fonte de dados: comparar com os métodos do próprio Vendedor.
        self.assertEqual(metricas.valor_vendido, self.bianca.valor_vendido())
        self.assertEqual(metricas.vendas, self.bianca.vendas())
        self.assertEqual(metricas.pecas, self.bianca.pecas())
        self.assertEqual(metricas.atendimentos, self.bianca.atendimentos())
        self.assertEqual(
            metricas.pecas_por_atendimento,
            self.bianca.pecas_por_atendimento(),
        )

    def test_mes_parcial_no_resumo_mensal(self):
        """Novembro (1 dia) é parcial; outubro (27 dias) não é.

        O mapeador deriva mes_parcial da regra compartilhada: menos de 10
        dias com dados significa mês incompleto.
        """
        resumos = {
            item["mes"]: resumo_mensal_de(item)
            for item in self.bianca.resumo_mensal()
        }

        self.assertIn("2026-10", resumos)
        self.assertIn("2026-11", resumos)

        self.assertEqual(resumos["2026-11"].dias_com_dados, 1)
        self.assertTrue(resumos["2026-11"].mes_parcial)

        self.assertEqual(resumos["2026-10"].dias_com_dados, 27)
        self.assertFalse(resumos["2026-10"].mes_parcial)

    def test_comparativo_tem_as_tres_metricas(self):
        """Conversão é 1ª de 8 (acima); P.A. e ticket são 8ª de 8 (abaixo)."""
        comparativo = comparativo_de(
            self.loader.obter_comparativo_time("C0031")
        )

        self.assertEqual(len(comparativo), 3)

        por_nome = {metrica.nome: metrica for metrica in comparativo}

        conversao = por_nome["conversao"]
        self.assertEqual(conversao.posicao, 1)
        self.assertEqual(conversao.total_vendedores, 8)
        self.assertEqual(conversao.situacao, "acima")

        pa = por_nome["pecas_por_atendimento"]
        self.assertEqual(pa.posicao, 8)
        self.assertEqual(pa.total_vendedores, 8)
        self.assertEqual(pa.situacao, "abaixo")

        ticket = por_nome["ticket_medio"]
        self.assertEqual(ticket.posicao, 8)
        self.assertEqual(ticket.situacao, "abaixo")

    def test_anotacao_de_marca_anotacao_do_time(self):
        """A anotação "(time)" sai com e_do_time True; a de pessoa, False."""
        do_time = Anotacao(
            data=date(2026, 8, 24),
            sobre="(time)",
            texto="Sábado corrido.",
        )
        de_pessoa = Anotacao(
            data=date(2026, 8, 6),
            sobre="Bianca Rocha",
            texto="Atendeu bem no sábado.",
        )

        self.assertTrue(anotacao_de(do_time).e_do_time)
        self.assertFalse(anotacao_de(de_pessoa).e_do_time)

        # Data, sobre e texto são copiados sem alteração.
        dto = anotacao_de(de_pessoa)
        self.assertEqual(dto.data, date(2026, 8, 6))
        self.assertEqual(dto.sobre, "Bianca Rocha")
        self.assertEqual(dto.texto, "Atendeu bem no sábado.")

    def test_roteiro_de_preserva_as_quatro_listas(self):
        """O DTO do roteiro traz as quatro listas com o mesmo conteúdo."""
        roteiro = FeedbackRoteiro(
            pontos_positivos=["Alta conversão"],
            pontos_melhoria=["Vender mais de uma peça"],
            possiveis_motivos=["Correria no sábado"],
            roteiro_conversa=["Como foi o sábado?", "O que te ajudaria?"],
        )

        dto = roteiro_de(roteiro)

        self.assertEqual(dto.pontos_positivos, roteiro.pontos_positivos)
        self.assertEqual(dto.pontos_melhoria, roteiro.pontos_melhoria)
        self.assertEqual(dto.possiveis_motivos, roteiro.possiveis_motivos)
        self.assertEqual(dto.roteiro_conversa, roteiro.roteiro_conversa)
