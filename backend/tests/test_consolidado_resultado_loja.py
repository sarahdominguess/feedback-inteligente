"""Testes do consolidado mensal da loja (visão regional).

Duas estratégias: stubs pequenos (para conferir cada fórmula à mão) e os CSVs
reais (para provar que o serviço fecha com os números do desafio).
"""

import unittest

from config import DATA_DIR
from services.consolidado_regional import ConsolidadoRegional
from services.data_loader import DataLoader


class PessoaFalsa:
    """Vendedor ou gerente de mentira, com valores e dias por mês.

    Só implementa o que o consolidado usa: valor vendido, meses com dados e
    dias com dados. Assim o teste controla os números sem CSV.
    """

    def __init__(self, valores: dict, dias: dict | None = None):
        self._valores = valores
        self._dias = dias or {}

    def valor_vendido(self, mes: str | None = None) -> float:
        """Valor vendido no mês (0 quando não há registro)."""
        return self._valores.get(mes, 0.0)

    def meses_com_dados(self) -> tuple[str, ...]:
        """Meses em que esta pessoa aparece, em ordem."""
        return tuple(sorted(self._valores))

    def dias_com_dados(self, mes: str) -> int:
        """Quantos dias esta pessoa tem no mês."""
        return self._dias.get(mes, 0)


class DataLoaderFalso:
    """DataLoader de mentira: devolve as pessoas e as metas combinadas."""

    def __init__(self, vendedores, gerente, metas):
        self._vendedores = vendedores
        self._gerente = gerente
        self._metas = metas

    def listar_vendedores(self):
        """Lista os vendedores combinados no teste."""
        return list(self._vendedores)

    def obter_vendas_do_gerente(self):
        """Devolve o gerente como Vendedor."""
        return self._gerente

    def obter_meta_loja(self, mes: str) -> float | None:
        """Meta da loja no mês (None quando não há)."""
        return self._metas.get(mes)


class TestConsolidadoComStubs(unittest.TestCase):
    """Testes das fórmulas com números escolhidos à mão."""

    def setUp(self):
        """Monta janeiro (meta 1000) e fevereiro (sem meta).

        Janeiro: vendedores 100 + 200 = 300; gerente 50; loja 350.
        Fevereiro: vendedores 0; gerente 40; loja 40; meta 0 (indisponível).
        """
        self.ana = PessoaFalsa(
            {"2026-01": 100.0}, {"2026-01": 5}
        )
        self.bruno = PessoaFalsa(
            {"2026-01": 200.0, "2026-02": 0.0}, {"2026-02": 3}
        )
        self.gerente = PessoaFalsa(
            {"2026-01": 50.0, "2026-02": 40.0},
            {"2026-01": 26, "2026-02": 2},
        )

        self.loader = DataLoaderFalso(
            [self.ana, self.bruno],
            self.gerente,
            {"2026-01": 1000.0, "2026-02": 0.0},
        )

        # O registro ainda não é usado neste método; None é suficiente.
        self.consolidado = ConsolidadoRegional(self.loader, None)

    def test_formulas_de_janeiro(self):
        """Confere soma, atingimentos e participação de janeiro."""
        janeiro = self.consolidado.obter_resultado_loja()[0]

        self.assertEqual(janeiro["mes"], "2026-01")
        self.assertEqual(janeiro["vendas_vendedores"], 300.0)
        self.assertEqual(janeiro["vendas_gerente"], 50.0)
        self.assertEqual(janeiro["vendas_loja"], 350.0)
        self.assertEqual(janeiro["meta_loja"], 1000.0)

        # 350 ÷ 1000 = 0,35 e 300 ÷ 1000 = 0,30.
        self.assertAlmostEqual(janeiro["atingimento_loja"], 0.35)
        self.assertAlmostEqual(janeiro["atingimento_vendedores"], 0.30)

        # 50 ÷ 350 = participação do gerente nas vendas da loja.
        self.assertAlmostEqual(
            janeiro["participacao_gerente"], 50.0 / 350.0
        )

        # O mês tem 26 dias (o maior entre as pessoas): não é parcial.
        self.assertEqual(janeiro["dias_com_dados"], 26)
        self.assertFalse(janeiro["mes_parcial"])

    def test_mes_com_meta_zero_e_mes_parcial(self):
        """Meta 0 => atingimentos None; 3 dias => mês parcial True."""
        fevereiro = self.consolidado.obter_resultado_loja()[1]

        self.assertEqual(fevereiro["mes"], "2026-02")
        self.assertEqual(fevereiro["vendas_vendedores"], 0.0)
        self.assertEqual(fevereiro["vendas_gerente"], 40.0)
        self.assertEqual(fevereiro["vendas_loja"], 40.0)
        self.assertEqual(fevereiro["meta_loja"], 0.0)

        # Divisão por meta zero não existe: None (vira null no JSON).
        self.assertIsNone(fevereiro["atingimento_loja"])
        self.assertIsNone(fevereiro["atingimento_vendedores"])

        # O gerente fez 100% das vendas do mês: 40 ÷ 40 = 1,0.
        self.assertAlmostEqual(fevereiro["participacao_gerente"], 1.0)

        self.assertEqual(fevereiro["dias_com_dados"], 3)
        self.assertTrue(fevereiro["mes_parcial"])

    def test_denominadores_ausentes_viram_none(self):
        """Sem vendas na loja e sem meta, tudo que divide fica None."""
        vazio = PessoaFalsa({}, {})
        gerente_vazio = PessoaFalsa({}, {})

        loader = DataLoaderFalso([vazio], gerente_vazio, {})
        consolidado = ConsolidadoRegional(loader, None)

        # Sem nenhum mês com dados, o resultado é uma lista vazia.
        self.assertEqual(consolidado.obter_resultado_loja(), [])

    def test_dicionario_tem_exatamente_os_campos_do_contrato(self):
        """Cada item traz só os campos de ResultadoLojaMesDTO."""
        janeiro = self.consolidado.obter_resultado_loja()[0]

        self.assertEqual(
            set(janeiro),
            {
                "mes",
                "mes_parcial",
                "dias_com_dados",
                "meta_loja",
                "vendas_loja",
                "atingimento_loja",
                "vendas_vendedores",
                "atingimento_vendedores",
                "vendas_gerente",
                "participacao_gerente",
            },
        )


class TestConsolidadoComDadosReais(unittest.TestCase):
    """Teste de fumaça contra os CSVs reais de backend/data."""

    @classmethod
    def setUpClass(cls):
        """Cria o consolidado com o DataLoader real (sem registro)."""
        cls.loader = DataLoader(data_dir=DATA_DIR)
        cls.consolidado = ConsolidadoRegional(cls.loader, None)
        cls.por_mes = {
            item["mes"]: item
            for item in cls.consolidado.obter_resultado_loja()
        }

    def test_quatro_meses(self):
        """Os dados reais cobrem agosto a novembro de 2026, em ordem."""
        self.assertEqual(
            list(self.por_mes), ["2026-08", "2026-09", "2026-10", "2026-11"]
        )

    def test_outubro_de_2026(self):
        """Outubro tem meta de 317.200 e os números batem com os CSVs.

        Vendedores ≈ 315.781,85 (≈99,55% da meta); com o gerente, a loja
        chega a ≈326.697,48 (≈103% da meta). O gerente fez ≈10.915,63.
        """
        outubro = self.por_mes["2026-10"]

        self.assertEqual(outubro["meta_loja"], 317200.0)

        self.assertAlmostEqual(
            outubro["vendas_vendedores"], 315781.85, delta=0.01
        )
        self.assertAlmostEqual(
            outubro["atingimento_vendedores"], 0.9955, delta=0.001
        )

        self.assertAlmostEqual(
            outubro["vendas_loja"], 326697.48, delta=0.01
        )
        self.assertAlmostEqual(
            outubro["atingimento_loja"], 1.03, delta=0.01
        )

        # 10.915,63 é o valor real da soma diária (arredonda para 10.916).
        self.assertAlmostEqual(
            outubro["vendas_gerente"], 10916.0, delta=0.5
        )

        # Coerência: loja = vendedores + gerente.
        self.assertAlmostEqual(
            outubro["vendas_loja"],
            outubro["vendas_vendedores"] + outubro["vendas_gerente"],
            places=2,
        )

    def test_novembro_e_mes_parcial(self):
        """Novembro tem 1 dia com dados (mês em andamento) e é parcial."""
        novembro = self.por_mes["2026-11"]

        self.assertEqual(novembro["dias_com_dados"], 1)
        self.assertTrue(novembro["mes_parcial"])
