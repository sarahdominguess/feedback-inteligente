"""Testes do construtor de prompt de feedback (mensagens para a IA).

A maior parte usa dados sintéticos (inventados no próprio teste), sem ler CSV.
No fim, uma classe de integração usa os CSVs reais para conferir o prompt da
Bianca. Nenhum teste chama a internet.
"""

import unittest
from datetime import date

from config import DATA_DIR
from domain.anotacao import Anotacao
from domain.comparativo_time import ComparativoTime, MetricaComparada
from domain.indicador_diario import IndicadorDiario
from domain.vendedor import Vendedor
from services.data_loader import DataLoader
from services.prompt_feedback import (
    SISTEMA_PROMPT,
    formatar_mes,
    formatar_moeda,
    formatar_numero,
    formatar_percentual,
    montar_mensagens,
)


def criar_vendedor_sintetico() -> Vendedor:
    """Cria uma vendedora fictícia com três dias de dados e uma meta.

    Outubro/2026 tem dois dias e meta de R$ 800,00 (atingimento de 100%).
    Novembro/2026 tem um único dia, para testar o aviso de mês parcial.
    """
    indicadores = [
        IndicadorDiario(
            data=date(2026, 10, 1),
            vendedor_id="C9000",
            valor_vendido=500.0,
            vendas=2,
            pecas=3,
            atendimentos=4,
        ),
        IndicadorDiario(
            data=date(2026, 10, 2),
            vendedor_id="C9000",
            valor_vendido=300.0,
            vendas=1,
            pecas=1,
            atendimentos=2,
        ),
        IndicadorDiario(
            data=date(2026, 11, 1),
            vendedor_id="C9000",
            valor_vendido=200.0,
            vendas=1,
            pecas=1,
            atendimentos=2,
        ),
    ]

    return Vendedor(
        vendedor_id="C9000",
        nome="Pessoa Exemplo",
        cargo="vendedor",
        loja_id="L000",
        loja_nome="Loja Exemplo",
        indicadores=indicadores,
        metas={"2026-10": 800.0},
    )


def criar_comparativo_sintetico() -> ComparativoTime:
    """Cria um comparativo fictício com as três métricas do sistema."""
    metricas = (
        MetricaComparada(
            nome="ticket_medio",
            valor=250.0,
            media_time=300.0,
            diferenca_percentual=-1 / 6,
            posicao=2,
            total_vendedores=3,
            situacao="abaixo",
        ),
        MetricaComparada(
            nome="pecas_por_atendimento",
            valor=1.25,
            media_time=1.5,
            diferenca_percentual=-1 / 6,
            posicao=3,
            total_vendedores=3,
            situacao="abaixo",
        ),
        MetricaComparada(
            nome="conversao",
            valor=0.5,
            media_time=0.4,
            diferenca_percentual=0.25,
            posicao=1,
            total_vendedores=3,
            situacao="acima",
        ),
    )

    return ComparativoTime(
        vendedor_id="C9000",
        nome="Pessoa Exemplo",
        metricas=metricas,
        mes=None,
    )


def montar_sintetico(
    anotacoes_do_vendedor=None,
    anotacoes_do_time=None,
    mes_referencia=None,
) -> list[dict]:
    """Chama montar_mensagens com os dados sintéticos, variando as anotações.

    Quando as listas de anotações não são passadas, usa duas da vendedora e
    uma do time para os testes que precisam de conteúdo.
    """
    if anotacoes_do_vendedor is None:
        anotacoes_do_vendedor = [
            Anotacao(
                data=date(2026, 8, 5),
                sobre="Pessoa Exemplo",
                texto="anotação antiga da vendedora",
            ),
            Anotacao(
                data=date(2026, 10, 1),
                sobre="Pessoa Exemplo",
                texto="anotação recente da vendedora",
            ),
        ]
    if anotacoes_do_time is None:
        anotacoes_do_time = [
            Anotacao(
                data=date(2026, 10, 31),
                sobre="(time)",
                texto="anotação sobre o time",
            )
        ]

    return montar_mensagens(
        vendedor=criar_vendedor_sintetico(),
        comparativo=criar_comparativo_sintetico(),
        anotacoes_do_vendedor=anotacoes_do_vendedor,
        anotacoes_do_time=anotacoes_do_time,
        gerente_nome="Gerente Exemplo",
        loja_nome="Loja Exemplo",
        mes_referencia=mes_referencia,
    )


class TestFormatadores(unittest.TestCase):
    """Confere a formatação em pt-BR feita sem depender de locale."""

    def test_moeda(self):
        """Valor em reais usa vírgula decimal e o prefixo R$."""
        self.assertEqual(formatar_moeda(206.311), "R$ 206,31")

    def test_moeda_com_milhar(self):
        """Milhares são separados por ponto, como no Brasil."""
        self.assertEqual(formatar_moeda(1234.5), "R$ 1.234,50")

    def test_percentual(self):
        """Fração de 0 a 1 vira porcentagem com uma casa decimal."""
        self.assertEqual(formatar_percentual(0.5048), "50,5%")

    def test_percentual_com_sinal(self):
        """Diferenças positivas ganham "+" na frente."""
        self.assertEqual(formatar_percentual(0.25, com_sinal=True), "+25,0%")

    def test_numero(self):
        """Números comuns usam duas casas e vírgula decimal."""
        self.assertEqual(formatar_numero(1.224), "1,22")

    def test_none_vira_sem_dados(self):
        """None significa "sem valor" e nunca deve aparecer como "None"."""
        self.assertEqual(formatar_moeda(None), "sem dados")
        self.assertEqual(formatar_percentual(None), "sem dados")
        self.assertEqual(formatar_numero(None), "sem dados")

    def test_mes(self):
        """O mês técnico "AAAA-MM" vira o nome em português."""
        self.assertEqual(formatar_mes("2026-10"), "outubro/2026")
        self.assertEqual(formatar_mes(None), "todo o histórico")


class TestMensagensSinteticas(unittest.TestCase):
    """Testa a estrutura das mensagens com dados inventados."""

    def test_duas_mensagens_com_papeis_corretos(self):
        """A saída tem exatamente sistema + usuário, nesta ordem."""
        mensagens = montar_sintetico()

        self.assertEqual(len(mensagens), 2)
        self.assertEqual(mensagens[0]["role"], "system")
        self.assertEqual(mensagens[1]["role"], "user")
        self.assertEqual(mensagens[0]["content"], SISTEMA_PROMPT)
        self.assertTrue(mensagens[1]["content"].strip())

    def test_mensagem_de_sistema(self):
        """O sistema pede JSON, as 4 chaves e o método SBI."""
        sistema = montar_sintetico()[0]["content"]

        self.assertIn("JSON", sistema)
        self.assertIn("SBI", sistema)
        for chave in (
            "pontos_positivos",
            "pontos_melhoria",
            "possiveis_motivos",
            "roteiro_conversa",
        ):
            with self.subTest(chave=chave):
                self.assertIn(f'"{chave}"', sistema)

    def test_mensagem_de_usuario_tem_os_dados(self):
        """O usuário recebe nome, período, indicadores e comparativo."""
        usuario = montar_sintetico(mes_referencia="2026-10")[1]["content"]

        self.assertIn("Pessoa Exemplo", usuario)
        self.assertIn("outubro/2026", usuario)
        self.assertIn("R$ 800,00", usuario)  # valor vendido em outubro
        self.assertIn("R$ 266,67", usuario)  # ticket médio de outubro
        self.assertIn("1,33", usuario)  # P.A. de outubro
        self.assertIn("100,0%", usuario)  # atingimento da meta
        self.assertIn("média do time", usuario)

    def test_mes_parcial_aparece(self):
        """Novembro/2026 tem um dia e deve ser marcado como parcial."""
        usuario = montar_sintetico()[1]["content"]

        self.assertIn("novembro/2026", usuario)
        self.assertIn("mês parcial (apenas 1 dia com dados)", usuario)

    def test_anotacoes_em_ordem_cronologica(self):
        """As anotações da vendedora aparecem da mais antiga para a recente."""
        usuario = montar_sintetico()[1]["content"]

        posicao_antiga = usuario.index("anotação antiga da vendedora")
        posicao_recente = usuario.index("anotação recente da vendedora")
        self.assertLess(posicao_antiga, posicao_recente)
        self.assertIn("anotação sobre o time", usuario)

    def test_sem_anotacoes(self):
        """Sem anotações, o prompt diz isso em vez de deixar o bloco vazio."""
        usuario = montar_sintetico(
            anotacoes_do_vendedor=[], anotacoes_do_time=[]
        )[1]["content"]

        self.assertEqual(usuario.count("Nenhuma anotação."), 2)

    def test_instrucao_final(self):
        """A última instrução repete o formato JSON pedido ao modelo."""
        usuario = montar_sintetico()[1]["content"]

        self.assertIn("Gere o roteiro em JSON conforme as regras.", usuario)

    def test_sem_meta_no_periodo(self):
        """Sem mês de referência, não inventa meta nem atingimento."""
        usuario = montar_sintetico()[1]["content"]

        self.assertNotIn("Meta do mês:", usuario)
        self.assertNotIn("Atingimento da meta:", usuario)


class TestPromptBiancaComDadosReais(unittest.TestCase):
    """Integração com os CSVs reais: prompt da Bianca (C0031)."""

    @classmethod
    def setUpClass(cls):
        """Carrega os CSVs uma única vez e monta as mensagens."""
        cls.loader = DataLoader(data_dir=DATA_DIR)
        cls.bianca = cls.loader.buscar_vendedor_por_nome("Bianca")
        cls.comparativo = cls.loader.obter_comparativo_time(
            cls.bianca.vendedor_id
        )
        cls.gerente = cls.loader.obter_gerente()
        cls.anotacoes = cls.loader.obter_anotacoes_do_vendedor(
            cls.bianca.vendedor_id
        )
        cls.anotacoes_time = cls.gerente.anotacoes_do_time()
        cls.mensagens = montar_mensagens(
            vendedor=cls.bianca,
            comparativo=cls.comparativo,
            anotacoes_do_vendedor=cls.anotacoes,
            anotacoes_do_time=cls.anotacoes_time,
            gerente_nome=cls.gerente.nome,
            loja_nome=cls.gerente.loja_nome,
        )

    def test_estrutura_das_mensagens(self):
        """São duas mensagens, sistema e usuário, com conteúdo."""
        self.assertEqual([m["role"] for m in self.mensagens], ["system", "user"])
        self.assertTrue(self.mensagens[1]["content"].strip())

    def test_sistema_tem_regras_e_formato(self):
        """O sistema exige JSON, as 4 chaves e o método SBI."""
        sistema = self.mensagens[0]["content"]

        self.assertIn("JSON", sistema)
        self.assertIn("SBI", sistema)
        for chave in (
            "pontos_positivos",
            "pontos_melhoria",
            "possiveis_motivos",
            "roteiro_conversa",
        ):
            with self.subTest(chave=chave):
                self.assertIn(f'"{chave}"', sistema)

    def test_usuario_tem_a_conversao_real(self):
        """A conversão do histórico completo aparece como 50,5%."""
        usuario = self.mensagens[1]["content"]

        self.assertIn("Bianca Rocha", usuario)
        self.assertIn("50,5%", usuario)

    def test_usuario_tem_as_anotacoes_dela_e_do_time(self):
        """As 3 anotações da Bianca e as 2 do time entram no texto."""
        usuario = self.mensagens[1]["content"]

        self.assertEqual(len(self.anotacoes), 3)
        self.assertEqual(len(self.anotacoes_time), 2)
        for anotacao in list(self.anotacoes) + list(self.anotacoes_time):
            with self.subTest(texto=anotacao.texto[:30]):
                self.assertIn(anotacao.texto, usuario)

    def test_usuario_nao_cita_outras_pessoas(self):
        """Nenhum nome de colega aparece: a comparação é só com a média."""
        usuario = self.mensagens[1]["content"]

        for nome in (
            "Sabrina",
            "Kaique",
            "Lucas",
            "Marcelo",
            "Renata",
            "Tatiane",
            "Vanessa",
        ):
            with self.subTest(nome=nome):
                self.assertNotIn(nome, usuario)

    def test_novembro_marcado_como_parcial(self):
        """Novembro/2026 tem só 1 dia de dados e precisa do aviso."""
        usuario = self.mensagens[1]["content"]

        self.assertIn("novembro/2026", usuario)
        self.assertIn("mês parcial (apenas 1 dia com dados)", usuario)


if __name__ == "__main__":
    unittest.main()
