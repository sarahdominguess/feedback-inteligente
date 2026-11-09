"""Testes do comparativo entre vendedor e média do time (dados sintéticos).

Os CSVs são criados em um diretório temporário para controlar as somas e
conferir as contas à mão: média ponderada por somas, ranking, situação e
tolerância de 5%.
"""

import tempfile
import unittest
from pathlib import Path

from services.data_loader import DataLoader


# Cenário 1: três vendedores, sendo dois com dados.
# Ana (C0031): valor 300, 3 vendas, 3 peças, 6 atendimentos
#   -> ticket 100, P.A. 1,0 e conversão 0,5.
# Bruno (C0032): valor 1000, 2 vendas, 4 peças, 2 atendimentos
#   -> ticket 500, P.A. 2,0 e conversão 1,0.
# Carla (C0033): sem dados.
# Time: valor 1300, 5 vendas, 7 peças, 8 atendimentos.
#   -> ticket 260, P.A. 1,4 e conversão 0,625.
# Repare que a média de ticket NÃO é (100 + 500) ÷ 2 = 300: usamos as somas.
VENDEDORES_PONDERADO = """\
vendedor_id,nome,cargo
C0030,Diego Furtado,gerente
C0031,Ana Equilibrada,vendedor
C0032,Bruno Volume,vendedor
C0033,Carla Sem Dados,vendedor
"""

INDICADORES_PONDERADO = """\
data,vendedor_id,valor_vendido,vendas,pecas,atendimentos
2026-08-01,C0031,300.0,3,3,6
2026-08-01,C0032,1000.0,2,4,2
"""

# Cenário 2: dois vendedores exatamente 5% distantes da média.
# Com 95 e 105 em uma venda cada, a média é 100; as diferenças são -5% e +5%,
# que devem cair dentro da tolerância ("na_media").
VENDEDORES_TOLERANCIA = """\
vendedor_id,nome,cargo
C0030,Diego Furtado,gerente
C0031,Dentro Um,vendedor
C0032,Dentro Dois,vendedor
"""

INDICADORES_TOLERANCIA = """\
data,vendedor_id,valor_vendido,vendas,pecas,atendimentos
2026-08-01,C0031,95.0,1,1,1
2026-08-01,C0032,105.0,1,1,1
"""

# Metas e anotações vazias (só o cabeçalho): o comparativo não depende delas,
# mas o DataLoader exige que os arquivos existam com as colunas obrigatórias.
METAS_VAZIAS = "vendedor_id,mes,meta_valor\n"
ANOTACOES_VAZIAS = "data,sobre,anotacao\n"


def criar_loader(conteudos: dict[str, str]):
    """Cria um diretório temporário com os CSVs e devolve loader + pasta.

    A pasta temporária é devolvida junto (em vez de só o loader) para quem
    chamou guardar a referência e limpar tudo no final do teste.
    """
    temporario = tempfile.TemporaryDirectory()
    diretorio = Path(temporario.name)

    for nome, conteudo in conteudos.items():
        (diretorio / nome).write_text(conteudo, encoding="utf-8")

    loader = DataLoader(
        data_dir=diretorio,
        loja_id="L004",
        loja_nome="Aurora Shopping Centro",
    )
    return loader, temporario


def metricas_por_nome(comparativo) -> dict:
    """Transforma a tupla de métricas num dicionário nome → métrica.

    Facilita achar "conversao" ou "ticket_medio" sem depender da posição.
    """
    return {metrica.nome: metrica for metrica in comparativo.metricas}


class TestComparativoComDadosSinteticos(unittest.TestCase):
    """Testes da média ponderada, do ranking e da situação."""

    def setUp(self):
        """Cria o cenário com Ana, Bruno e Carla (sem dados)."""
        self.loader, self._temporario = criar_loader(
            {
                "vendedores.csv": VENDEDORES_PONDERADO,
                "indicadores_diarios_vendedor.csv": INDICADORES_PONDERADO,
                "metas_vendedor.csv": METAS_VAZIAS,
                "anotacoes_gerente.csv": ANOTACOES_VAZIAS,
            }
        )
        self.addCleanup(self._temporario.cleanup)

    def test_media_do_time_usa_somas_agregadas(self):
        """A média é soma ÷ soma, não a média das razões individuais.

        Ticket do time = 1300 ÷ 5 = 260 (e não (100 + 500) ÷ 2 = 300).
        P.A. do time = 7 ÷ 5 = 1,4.
        Conversão do time = 5 ÷ 8 = 0,625.
        """
        ana = self.loader.obter_comparativo_time("C0031")
        metricas = metricas_por_nome(ana)

        self.assertAlmostEqual(metricas["ticket_medio"].media_time, 260.0)
        self.assertAlmostEqual(
            metricas["pecas_por_atendimento"].media_time, 1.4
        )
        self.assertAlmostEqual(metricas["conversao"].media_time, 0.625)

        # Prova de que não foi usada a média simples das razões.
        self.assertNotAlmostEqual(metricas["ticket_medio"].media_time, 300.0)

    def test_diferenca_percentual(self):
        """A diferença é (valor - média) ÷ média, em fração.

        Ana: ticket (100 - 260) ÷ 260 ≈ -0,615; P.A. (1 - 1,4) ÷ 1,4 ≈
        -0,286; conversão (0,5 - 0,625) ÷ 0,625 = -0,20.
        """
        ana = self.loader.obter_comparativo_time("C0031")
        metricas = metricas_por_nome(ana)

        self.assertAlmostEqual(
            metricas["ticket_medio"].diferenca_percentual, -160 / 260
        )
        self.assertAlmostEqual(
            metricas["pecas_por_atendimento"].diferenca_percentual, -0.4 / 1.4
        )
        self.assertAlmostEqual(
            metricas["conversao"].diferenca_percentual, -0.125 / 0.625
        )

    def test_posicoes_no_ranking(self):
        """1 = melhor valor; Ana fica em 2º e Bruno em 1º nas três métricas."""
        ana = metricas_por_nome(self.loader.obter_comparativo_time("C0031"))
        bruno = metricas_por_nome(self.loader.obter_comparativo_time("C0032"))

        for nome in ("ticket_medio", "pecas_por_atendimento", "conversao"):
            self.assertEqual(ana[nome].posicao, 2, nome)
            self.assertEqual(bruno[nome].posicao, 1, nome)
            self.assertEqual(ana[nome].total_vendedores, 3)

    def test_situacoes_acima_e_abaixo(self):
        """Abaixo de -5% vira "abaixo"; acima de +5% vira "acima"."""
        ana = metricas_por_nome(self.loader.obter_comparativo_time("C0031"))
        bruno = metricas_por_nome(self.loader.obter_comparativo_time("C0032"))

        for nome in ("ticket_medio", "pecas_por_atendimento", "conversao"):
            self.assertEqual(ana[nome].situacao, "abaixo", nome)
            self.assertEqual(bruno[nome].situacao, "acima", nome)

    def test_vendedor_sem_dados_fica_indisponivel(self):
        """Carla não tem registros: valor e posição None e situação indisponível.

        A média do time continua existindo (os colegas têm dados), mas sem
        valor da Carla não há comparação possível.
        """
        carla = self.loader.obter_comparativo_time("C0033")

        self.assertEqual(carla.vendedor_id, "C0033")
        for metrica in carla.metricas:
            self.assertIsNone(metrica.valor)
            self.assertIsNone(metrica.diferenca_percentual)
            self.assertIsNone(metrica.posicao)
            self.assertEqual(metrica.situacao, "indisponivel")
            self.assertEqual(metrica.total_vendedores, 3)
            self.assertIsNotNone(metrica.media_time)

    def test_para_dict(self):
        """O comparativo vira um dicionário com as três métricas completas."""
        dicionario = self.loader.obter_comparativo_time("C0031").para_dict()

        self.assertEqual(dicionario["vendedor_id"], "C0031")
        self.assertEqual(dicionario["nome"], "Ana Equilibrada")
        self.assertIsNone(dicionario["mes"])
        self.assertEqual(len(dicionario["metricas"]), 3)

        campos = {
            "nome",
            "valor",
            "media_time",
            "diferenca_percentual",
            "posicao",
            "total_vendedores",
            "situacao",
        }
        self.assertEqual(set(dicionario["metricas"][0]), campos)


class TestToleranciaDeCincoPorCento(unittest.TestCase):
    """Teste da borda da tolerância: exatamente ±5% conta como "na_media"."""

    def setUp(self):
        """Cria dois vendedores com ticket 95 e 105 (média 100)."""
        self.loader, self._temporario = criar_loader(
            {
                "vendedores.csv": VENDEDORES_TOLERANCIA,
                "indicadores_diarios_vendedor.csv": INDICADORES_TOLERANCIA,
                "metas_vendedor.csv": METAS_VAZIAS,
                "anotacoes_gerente.csv": ANOTACOES_VAZIAS,
            }
        )
        self.addCleanup(self._temporario.cleanup)

    def test_cinco_por_cento_para_mais_e_para_menos_fica_na_media(self):
        """Diferença de -5% ou +5% ainda é considerada dentro da média."""
        for vendedor_id in ("C0031", "C0032"):
            comparativo = self.loader.obter_comparativo_time(vendedor_id)

            for metrica in comparativo.metricas:
                with self.subTest(
                    vendedor=vendedor_id, metrica=metrica.nome
                ):
                    # No ticket a distância é exatamente 5%; nas outras duas
                    # métricas os dois vendedores empatam (diferença 0%).
                    esperado = 0.05 if metrica.nome == "ticket_medio" else 0.0
                    self.assertAlmostEqual(
                        abs(metrica.diferenca_percentual), esperado
                    )
                    self.assertEqual(metrica.situacao, "na_media")
