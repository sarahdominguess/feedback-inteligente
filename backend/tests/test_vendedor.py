"""Testes da entidade Vendedor e das métricas calculadas.

Usam dados sintéticos pequenos, criados aqui mesmo (sem ler CSV), para conferir
as contas à mão. Se uma métrica mudar sem querer, estes testes avisam.
"""

import unittest
from datetime import date

from domain.indicador_diario import IndicadorDiario
from domain.vendedor import Vendedor


def criar_indicador(
    mes: int,
    dia: int,
    valor: float,
    vendas: int,
    pecas: int,
    atendimentos: int,
) -> IndicadorDiario:
    """Cria um IndicadorDiario de 2026 para usar nos testes.

    É uma função auxiliar: evita repetir o mesmo bloco de criação em cada
    teste. Todos os indicadores usam o vendedor fictício "C0031".
    """
    return IndicadorDiario(
        data=date(2026, mes, dia),
        vendedor_id="C0031",
        valor_vendido=valor,
        vendas=vendas,
        pecas=pecas,
        atendimentos=atendimentos,
    )


class TestVendedor(unittest.TestCase):
    """Testes das somas, métricas, metas e proteções do Vendedor."""

    def setUp(self):
        """Monta um vendedor com dois dias de agosto e um de setembro.

        Contas à mão:
        - Agosto: 300 + 100 = 400 de valor; 2 + 1 = 3 vendas; 3 + 1 = 4 peças;
          4 + 4 = 8 atendimentos.
        - Setembro: 500 de valor; 2 vendas; 2 peças; 5 atendimentos.
        - Todo o histórico: 900 de valor; 5 vendas; 6 peças; 13 atendimentos.

        A lista é passada fora de ordem (agosto, setembro, agosto) de propósito,
        para provar que o Vendedor ordena os indicadores por data.
        """
        self.indicadores = [
            criar_indicador(8, 1, 300.0, 2, 3, 4),
            criar_indicador(9, 1, 500.0, 2, 2, 5),
            criar_indicador(8, 2, 100.0, 1, 1, 4),
        ]

        self.vendedor = Vendedor(
            vendedor_id="C0031",
            nome="Bianca Rocha",
            cargo="vendedor",
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            indicadores=self.indicadores,
            metas={"2026-08": 200.0, "2026-10": 0.0},
        )

    def test_somas_de_todo_o_historico(self):
        """Sem mês, as somas consideram todos os registros.

        Esperado: 900 de valor, 5 vendas, 6 peças e 13 atendimentos.
        """
        self.assertEqual(self.vendedor.valor_vendido(), 900.0)
        self.assertEqual(self.vendedor.vendas(), 5)
        self.assertEqual(self.vendedor.pecas(), 6)
        self.assertEqual(self.vendedor.atendimentos(), 13)

    def test_somas_de_um_mes_especifico(self):
        """Com o mês, só os dias daquele mês entram na conta.

        Agosto: 400 de valor, 3 vendas, 4 peças e 8 atendimentos.
        """
        self.assertEqual(self.vendedor.valor_vendido("2026-08"), 400.0)
        self.assertEqual(self.vendedor.vendas("2026-08"), 3)
        self.assertEqual(self.vendedor.pecas("2026-08"), 4)
        self.assertEqual(self.vendedor.atendimentos("2026-08"), 8)

    def test_metricas_conferidas_a_mao(self):
        """Confere as três métricas com as contas feitas à mão.

        Agosto:
        - ticket médio = 400 ÷ 3 ≈ 133,33.
        - P.A. = 4 ÷ 3 ≈ 1,33.
        - conversão = 3 ÷ 8 = 0,375.

        Todo o histórico:
        - ticket médio = 900 ÷ 5 = 180.
        - P.A. = 6 ÷ 5 = 1,2.
        - conversão = 5 ÷ 13 ≈ 0,3846.
        """
        self.assertAlmostEqual(self.vendedor.ticket_medio("2026-08"), 400 / 3)
        self.assertAlmostEqual(
            self.vendedor.pecas_por_atendimento("2026-08"), 4 / 3
        )
        self.assertAlmostEqual(self.vendedor.conversao("2026-08"), 0.375)

        self.assertAlmostEqual(self.vendedor.ticket_medio(), 180.0)
        self.assertAlmostEqual(self.vendedor.pecas_por_atendimento(), 1.2)
        self.assertAlmostEqual(self.vendedor.conversao(), 5 / 13)

    def test_denominador_zero_retorna_none(self):
        """Sem vendas ou sem atendimentos, a métrica é None (nunca erro).

        Criamos um vendedor com um único dia todo zerado: não há como dividir
        por zero, então ticket médio, P.A. e conversão devem ser None.
        """
        vendedor_zerado = Vendedor(
            vendedor_id="C9999",
            nome="Pessoa Sem Vendas",
            cargo="vendedor",
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            indicadores=[criar_indicador(8, 1, 0.0, 0, 0, 0)],
        )

        self.assertIsNone(vendedor_zerado.ticket_medio("2026-08"))
        self.assertIsNone(vendedor_zerado.pecas_por_atendimento("2026-08"))
        self.assertIsNone(vendedor_zerado.conversao("2026-08"))

        # Mês sem nenhum registro também devolve None nas métricas.
        self.assertIsNone(self.vendedor.ticket_medio("2026-07"))
        self.assertIsNone(self.vendedor.pecas_por_atendimento("2026-07"))
        self.assertIsNone(self.vendedor.conversao("2026-07"))

    def test_meta_e_atingimento(self):
        """Confere a busca de meta e o cálculo do atingimento.

        Agosto: meta de 200 e 400 vendidos → 400 ÷ 200 = 2,0 (200% da meta).
        Setembro: sem meta → None.
        Outubro: meta cadastrada como 0 → atingimento None (não divide por zero).
        """
        self.assertEqual(self.vendedor.meta_do_mes("2026-08"), 200.0)
        self.assertAlmostEqual(self.vendedor.atingimento_meta("2026-08"), 2.0)

        self.assertIsNone(self.vendedor.meta_do_mes("2026-09"))
        self.assertIsNone(self.vendedor.atingimento_meta("2026-09"))

        self.assertEqual(self.vendedor.meta_do_mes("2026-10"), 0.0)
        self.assertIsNone(self.vendedor.atingimento_meta("2026-10"))

    def test_gerente_sem_metas_nao_quebra(self):
        """O gerente vende, mas não tem meta individual: metas vazias funcionam.

        Mesmo sem meta, as somas e métricas continuam sendo calculadas.
        """
        gerente = Vendedor(
            vendedor_id="C0030",
            nome="Diego Furtado",
            cargo="gerente",
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            indicadores=[criar_indicador(8, 1, 334.06, 1, 2, 4)],
        )

        self.assertEqual(gerente.cargo, "gerente")
        self.assertEqual(gerente.metas, {})
        self.assertEqual(gerente.valor_vendido("2026-08"), 334.06)
        self.assertIsNone(gerente.meta_do_mes("2026-08"))
        self.assertIsNone(gerente.atingimento_meta("2026-08"))

    def test_meses_e_dias_com_dados(self):
        """Os meses saem em ordem e os dias contam os registros do mês."""
        self.assertEqual(
            self.vendedor.meses_com_dados(), ("2026-08", "2026-09")
        )
        self.assertEqual(self.vendedor.dias_com_dados("2026-08"), 2)
        self.assertEqual(self.vendedor.dias_com_dados("2026-09"), 1)
        self.assertEqual(self.vendedor.dias_com_dados("2026-07"), 0)

    def test_resumo_mensal(self):
        """O resumo traz um dicionário por mês, com todas as chaves pedidas."""
        resumo = self.vendedor.resumo_mensal()

        self.assertEqual(len(resumo), 2)

        chaves = {
            "mes",
            "dias_com_dados",
            "valor_vendido",
            "vendas",
            "pecas",
            "atendimentos",
            "ticket_medio",
            "pecas_por_atendimento",
            "conversao",
            "meta",
            "atingimento_meta",
        }
        self.assertEqual(set(resumo[0]), chaves)

        agosto = resumo[0]
        self.assertEqual(agosto["mes"], "2026-08")
        self.assertEqual(agosto["dias_com_dados"], 2)
        self.assertEqual(agosto["valor_vendido"], 400.0)
        self.assertEqual(agosto["vendas"], 3)
        self.assertEqual(agosto["pecas"], 4)
        self.assertEqual(agosto["atendimentos"], 8)
        self.assertAlmostEqual(agosto["ticket_medio"], 400 / 3)
        self.assertAlmostEqual(agosto["pecas_por_atendimento"], 4 / 3)
        self.assertAlmostEqual(agosto["conversao"], 0.375)
        self.assertEqual(agosto["meta"], 200.0)
        self.assertAlmostEqual(agosto["atingimento_meta"], 2.0)

        setembro = resumo[1]
        self.assertEqual(setembro["mes"], "2026-09")
        self.assertIsNone(setembro["meta"])
        self.assertIsNone(setembro["atingimento_meta"])

    def test_indicadores_sao_copiados_e_ordenados(self):
        """A lista original não altera o Vendedor e o histórico fica ordenado."""
        # Guardamos o tamanho antes e mexemos na lista usada no construtor.
        self.indicadores.append(criar_indicador(10, 1, 50.0, 1, 1, 2))

        # O Vendedor deve continuar com os 3 indicadores originais.
        self.assertEqual(len(self.vendedor.indicadores), 3)

        # E eles devem estar em ordem crescente de data.
        datas = [indicador.data for indicador in self.vendedor.indicadores]
        self.assertEqual(
            datas,
            [date(2026, 8, 1), date(2026, 8, 2), date(2026, 9, 1)],
        )

    def test_colecoes_publicas_nao_sao_alteraveis(self):
        """A API pública não permite modificar indicadores nem identidade.

        - indicadores é uma tupla: tentar trocar um item levanta TypeError.
        - nome é uma propriedade sem "setter": atribuir levanta AttributeError.
        - metas devolve cópia: mexer no dicionário devolvido não altera o objeto.
        """
        self.assertIsInstance(self.vendedor.indicadores, tuple)

        with self.assertRaises(TypeError):
            self.vendedor.indicadores[0] = criar_indicador(8, 3, 1.0, 1, 1, 1)

        with self.assertRaises(AttributeError):
            self.vendedor.nome = "Outro Nome"

        copia_das_metas = self.vendedor.metas
        copia_das_metas["2026-08"] = 999.0
        self.assertEqual(self.vendedor.meta_do_mes("2026-08"), 200.0)
