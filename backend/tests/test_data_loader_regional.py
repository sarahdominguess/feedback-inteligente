"""Testes da leitura dos CSVs da regional no DataLoader.

Usam duas estratégias, como o test_data_loader.py: CSVs pequenos em diretório
temporário (para controlar arquivo ausente e coluna faltando) e os CSVs reais
de backend/data (teste de fumaça com os números do desafio).
"""

import tempfile
import unittest
from pathlib import Path

from config import DATA_DIR
from domain.excecoes import DadosIndisponiveisError
from services.data_loader import DataLoader


# --- CSVs sintéticos da regional -------------------------------------------
# As anotações vêm de propósito FORA de ordem cronológica: assim o teste
# consegue provar que o DataLoader ordena por data em vez de confiar no arquivo.
ANOTACOES_REGIONAL = """\
data,autora,anotacao
2026-10-20,Patrícia Lemos,"conversar sobre a escala de sábado"
2026-09-10,Patrícia Lemos,"elogio ao time pelo atendimento"
"""

METAS_LOJA = """\
mes,meta_valor
2026-09,282500.0
2026-10,317200.0
"""


# --- CSVs sintéticos mínimos das vendas ------------------------------------
# Só o suficiente para provar que a leitura da regional é independente: um
# DataLoader com estes arquivos (e SEM os da regional) continua listando
# vendedores normalmente.
VENDEDORES_MIN = """\
vendedor_id,nome,cargo
C0031,Bianca Rocha,vendedor
C0030,Diego Furtado,gerente
"""

INDICADORES_VAZIO = (
    "data,vendedor_id,valor_vendido,vendas,pecas,atendimentos\n"
)
METAS_VENDEDOR_VAZIO = "vendedor_id,mes,meta_valor\n"
ANOTACOES_GERENTE_VAZIO = "data,sobre,anotacao\n"


def escrever_arquivos(diretorio: Path, arquivos: dict[str, str]) -> None:
    """Escreve cada texto em um arquivo com o nome indicado, em UTF-8.

    UTF-8: a codificação de texto que preserva acentos e é usada nos CSVs.
    """
    for nome, conteudo in arquivos.items():
        (diretorio / nome).write_text(conteudo, encoding="utf-8")


def arquivos_da_regional() -> dict[str, str]:
    """Devolve os dois CSVs sintéticos da regional, por nome de arquivo."""
    return {
        "anotacoes_regional.csv": ANOTACOES_REGIONAL,
        "metas_loja.csv": METAS_LOJA,
    }


def arquivos_de_vendas() -> dict[str, str]:
    """Devolve os quatro CSVs sintéticos de vendas (dois deles só com cabeçalho)."""
    return {
        "vendedores.csv": VENDEDORES_MIN,
        "indicadores_diarios_vendedor.csv": INDICADORES_VAZIO,
        "metas_vendedor.csv": METAS_VENDEDOR_VAZIO,
        "anotacoes_gerente.csv": ANOTACOES_GERENTE_VAZIO,
    }


class TestDataLoaderRegionalComDadosSinteticos(unittest.TestCase):
    """Testes da leitura, dos erros e da proteção do cache da regional."""

    def setUp(self):
        """Cria um diretório temporário com os CSVs e um DataLoader nele.

        TemporaryDirectory é uma pasta temporária que o próprio Python apaga
        no final do teste (registramos o cleanup com addCleanup).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.data_dir = Path(self._diretorio_temporario.name)
        escrever_arquivos(self.data_dir, arquivos_da_regional())

        self.loader = DataLoader(data_dir=self.data_dir)

    def test_lista_anotacoes_em_ordem_cronologica(self):
        """As anotações saem ordenadas por data, mesmo com o CSV fora de ordem.

        No CSV sintético, outubro aparece antes de setembro. A ordem correta
        da leitura é setembro (10/09) e depois outubro (20/10).
        """
        anotacoes = self.loader.listar_anotacoes_regional()

        self.assertEqual(len(anotacoes), 2)
        self.assertEqual(
            [anotacao.data.isoformat() for anotacao in anotacoes],
            ["2026-09-10", "2026-10-20"],
        )
        # Data, autora e texto vêm do CSV, sem troca de campo.
        self.assertEqual(anotacoes[0].autora, "Patrícia Lemos")
        self.assertEqual(anotacoes[0].texto, "elogio ao time pelo atendimento")

    def test_obter_meta_loja_existente_e_inexistente(self):
        """Mês cadastrado devolve o valor; mês ausente devolve None.

        None (o "sem valor" do Python) é a resposta certa para um mês que a
        loja não tem meta: não é um erro, é ausência de dado.
        """
        self.assertEqual(self.loader.obter_meta_loja("2026-10"), 317200.0)
        self.assertIsNone(self.loader.obter_meta_loja("2030-01"))

    def test_listar_metas_loja_devolve_copia(self):
        """Alterar o dicionário devolvido não pode mudar o cache do loader.

        Se o método devolvesse o dicionário interno, um chamador distraído
        mudaria as metas para o resto do programa.
        """
        metas = self.loader.listar_metas_loja()
        self.assertEqual(
            metas, {"2026-09": 282500.0, "2026-10": 317200.0}
        )

        # Mexemos na cópia de propósito; o loader deve continuar intacto.
        metas["2026-10"] = 1.0
        del metas["2026-09"]

        self.assertEqual(self.loader.obter_meta_loja("2026-10"), 317200.0)
        self.assertEqual(self.loader.obter_meta_loja("2026-09"), 282500.0)

    def test_arquivo_ausente_levanta_dados_indisponiveis(self):
        """Sem o CSV de metas, o erro aparece na primeira chamada da regional.

        A leitura é preguiçosa: o construtor não falha; o erro só surge
        quando um método realmente precisa do arquivo.
        """
        with tempfile.TemporaryDirectory() as nome_diretorio:
            diretorio = Path(nome_diretorio)
            arquivos = arquivos_da_regional()
            del arquivos["metas_loja.csv"]
            escrever_arquivos(diretorio, arquivos)

            loader = DataLoader(data_dir=diretorio)

            with self.assertRaises(DadosIndisponiveisError) as contexto:
                loader.obter_meta_loja("2026-10")

            # A mensagem precisa dizer qual arquivo faltou.
            self.assertIn("metas_loja.csv", str(contexto.exception))

    def test_coluna_faltando_levanta_dados_indisponiveis(self):
        """CSV da regional sem uma coluna obrigatória gera erro com o nome dela."""
        with tempfile.TemporaryDirectory() as nome_diretorio:
            diretorio = Path(nome_diretorio)
            arquivos = arquivos_da_regional()
            # anotacoes_regional.csv sem a coluna "autora".
            arquivos["anotacoes_regional.csv"] = (
                "data,anotacao\n2026-09-10,\"elogio ao time\"\n"
            )
            escrever_arquivos(diretorio, arquivos)

            loader = DataLoader(data_dir=diretorio)

            with self.assertRaises(DadosIndisponiveisError) as contexto:
                loader.listar_anotacoes_regional()

            mensagem = str(contexto.exception)
            self.assertIn("anotacoes_regional.csv", mensagem)
            self.assertIn("autora", mensagem)

    def test_vendas_funcionam_sem_os_arquivos_da_regional(self):
        """Sem os CSVs da regional, a leitura de vendas continua funcionando.

        É a garantia de que a regional tem cache próprio: quem só precisa do
        feedback individual não passa a depender destes dois arquivos.
        """
        with tempfile.TemporaryDirectory() as nome_diretorio:
            diretorio = Path(nome_diretorio)
            escrever_arquivos(diretorio, arquivos_de_vendas())

            loader = DataLoader(data_dir=diretorio)

            # A venda carrega normalmente...
            vendedores = loader.listar_vendedores()
            self.assertEqual(
                [vendedor.vendedor_id for vendedor in vendedores], ["C0031"]
            )

            # ...e só a visão regional reclama do arquivo ausente.
            with self.assertRaises(DadosIndisponiveisError):
                loader.listar_anotacoes_regional()


class TestDataLoaderRegionalComDadosReais(unittest.TestCase):
    """Teste de fumaça contra os CSVs reais da regional em backend/data."""

    @classmethod
    def setUpClass(cls):
        """Cria um único DataLoader para todos os testes da classe."""
        cls.loader = DataLoader(data_dir=DATA_DIR)

    def test_cinco_anotacoes_da_patricia_em_ordem(self):
        """O arquivo real tem 5 anotações, todas da Patrícia, em ordem de data."""
        anotacoes = self.loader.listar_anotacoes_regional()

        self.assertEqual(len(anotacoes), 5)
        self.assertEqual(
            {anotacao.autora for anotacao in anotacoes},
            {"Patrícia Lemos"},
        )

        # As datas devem estar em ordem crescente (comparar a lista com ela
        # mesma ordenada é a forma mais direta de checar isso).
        datas = [anotacao.data for anotacao in anotacoes]
        self.assertEqual(datas, sorted(datas))

    def test_meta_da_loja_de_outubro(self):
        """Outubro/2026 tem meta de 317200 reais; 2030-01 não tem meta."""
        self.assertEqual(self.loader.obter_meta_loja("2026-10"), 317200.0)
        self.assertIsNone(self.loader.obter_meta_loja("2030-01"))

    def test_alterar_metas_devolvidas_nao_muda_o_loader(self):
        """A cópia devolvida por listar_metas_loja() protege o loader real."""
        metas = self.loader.listar_metas_loja()
        metas["2026-10"] = 0.0

        self.assertEqual(self.loader.obter_meta_loja("2026-10"), 317200.0)
