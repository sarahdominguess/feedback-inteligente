"""Testes do serviço DataLoader (leitura dos CSVs com Pandas).

Usam duas estratégias: CSVs mínimos em diretório temporário (para controlar
cenários como arquivo ausente e coluna faltando) e os CSVs reais do projeto
(um teste de fumaça que confirma a carga dos dados do desafio).
"""

import tempfile
import unittest
from pathlib import Path

from config import DATA_DIR
from domain.excecoes import DadosIndisponiveisError, VendedorNaoEncontradoError
from services.data_loader import DataLoader


# Conteúdo dos CSVs sintéticos. O gerente também aparece em vendedores.csv,
# como nos dados reais; ferias_no_periodo fica vazio para provar que uma
# célula vazia não vira NaN dentro do domínio.
VENDEDORES = """\
vendedor_id,nome,cargo,ferias_no_periodo
C0030,Diego Furtado,gerente,
C0031,Bianca Rocha,vendedor,
C0032,Ana Silva,vendedor,
C0033,Ana Souza,vendedor,
"""

INDICADORES = """\
data,vendedor_id,valor_vendido,vendas,pecas,atendimentos
2026-08-01,C0030,100.0,1,1,2
2026-08-01,C0031,300.0,2,3,4
2026-08-02,C0031,100.0,1,1,4
2026-09-01,C0032,500.0,2,2,5
"""

METAS = """\
vendedor_id,mes,meta_valor
C0031,2026-08,200.0
C0032,2026-08,1000.0
"""

ANOTACOES = """\
data,sobre,anotacao
2026-08-06,Bianca Rocha,"atendeu bem no sábado"
2026-08-24,(time),"sábado corrido"
2026-09-01,Ana Silva,"boa argumentação"
"""


def arquivos_padrao() -> dict[str, str]:
    """Devolve os quatro CSVs sintéticos completos, por nome de arquivo."""
    return {
        "vendedores.csv": VENDEDORES,
        "indicadores_diarios_vendedor.csv": INDICADORES,
        "metas_vendedor.csv": METAS,
        "anotacoes_gerente.csv": ANOTACOES,
    }


def escrever_arquivos(diretorio: Path, arquivos: dict[str, str]) -> None:
    """Escreve cada texto em um arquivo com o nome indicado, em UTF-8.

    UTF-8: a codificação de texto que preserva acentos e é usada nos CSVs.
    """
    for nome, conteudo in arquivos.items():
        (diretorio / nome).write_text(conteudo, encoding="utf-8")


class TestDataLoaderComDadosSinteticos(unittest.TestCase):
    """Testes da carga, do cruzamento por ID e dos erros de dados."""

    def setUp(self):
        """Cria um diretório temporário com os CSVs e um DataLoader apontando nele.

        TemporaryDirectory é uma pasta temporária que o próprio Python apaga
        no final do teste (registramos o cleanup com addCleanup).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.data_dir = Path(self._diretorio_temporario.name)
        escrever_arquivos(self.data_dir, arquivos_padrao())

        self.loader = DataLoader(
            data_dir=self.data_dir,
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
        )

    def test_lista_vendedores_na_ordem_do_csv(self):
        """Só o cargo "vendedor" entra, na ordem em que aparece no arquivo."""
        vendedores = self.loader.listar_vendedores()

        self.assertEqual(
            [vendedor.vendedor_id for vendedor in vendedores],
            ["C0031", "C0032", "C0033"],
        )
        self.assertTrue(
            all(vendedor.cargo == "vendedor" for vendedor in vendedores)
        )

        # O gerente não aparece na lista de vendedores.
        self.assertNotIn("C0030", [v.vendedor_id for v in vendedores])

    def test_cruzamento_de_indicadores_e_metas_por_id(self):
        """Cada vendedor recebe os indicadores e as metas do seu ID.

        Bianca (C0031) tem dois dias em agosto: 300 + 100 = 400 de valor,
        2 + 1 = 3 vendas, 3 + 1 = 4 peças e 4 + 4 = 8 atendimentos.
        A meta dela em agosto é 200.
        """
        bianca = self.loader.obter_vendedor("C0031")

        self.assertEqual(len(bianca.indicadores), 2)
        self.assertEqual(bianca.valor_vendido("2026-08"), 400.0)
        self.assertEqual(bianca.vendas("2026-08"), 3)
        self.assertEqual(bianca.pecas("2026-08"), 4)
        self.assertEqual(bianca.atendimentos("2026-08"), 8)
        self.assertAlmostEqual(bianca.ticket_medio("2026-08"), 400 / 3)
        self.assertEqual(bianca.meta_do_mes("2026-08"), 200.0)

        # Ana Silva (C0032) tem um dia em setembro e meta de 1000 em agosto.
        ana_silva = self.loader.obter_vendedor("C0032")
        self.assertEqual(ana_silva.valor_vendido("2026-09"), 500.0)
        self.assertEqual(ana_silva.meta_do_mes("2026-08"), 1000.0)

        # Ana Souza (C0033) não tem indicadores nem metas.
        ana_souza = self.loader.obter_vendedor("C0033")
        self.assertEqual(ana_souza.indicadores, ())
        self.assertEqual(ana_souza.metas, {})
        self.assertEqual(ana_souza.meses_com_dados(), ())

    def test_dados_da_loja_vem_do_construtor(self):
        """Todos os funcionários recebem a loja configurada no DataLoader."""
        gerente = self.loader.obter_gerente()
        bianca = self.loader.obter_vendedor("C0031")

        self.assertEqual(gerente.loja_id, "L004")
        self.assertEqual(gerente.loja_nome, "Aurora Shopping Centro")
        self.assertEqual(bianca.loja_id, "L004")
        self.assertEqual(bianca.loja_nome, "Aurora Shopping Centro")

    def test_obter_gerente_com_todas_as_anotacoes(self):
        """O gerente é a linha com cargo "gerente" e recebe todas as anotações."""
        gerente = self.loader.obter_gerente()

        self.assertEqual(gerente.gerente_id, "C0030")
        self.assertEqual(gerente.nome, "Diego Furtado")
        self.assertEqual(gerente.total_anotacoes(), 3)
        self.assertEqual(len(gerente.anotacoes_do_time()), 1)

    def test_anotacoes_do_vendedor_excluem_as_do_time(self):
        """A busca usa o nome do vendedor e não inclui anotações "(time)"."""
        anotacoes = self.loader.obter_anotacoes_do_vendedor("C0031")

        self.assertEqual(len(anotacoes), 1)
        self.assertEqual(anotacoes[0].texto, "atendeu bem no sábado")

        # Vendedor sem anotação devolve tupla vazia.
        self.assertEqual(self.loader.obter_anotacoes_do_vendedor("C0033"), ())

    def test_obter_vendedor_inexistente_levanta_erro(self):
        """ID desconhecido ou que pertence ao gerente não é vendedor."""
        with self.assertRaises(VendedorNaoEncontradoError):
            self.loader.obter_vendedor("C9999")

        with self.assertRaises(VendedorNaoEncontradoError):
            self.loader.obter_vendedor("C0030")

    def test_busca_por_nome_completo_e_primeiro_nome(self):
        """A busca aceita nome completo ou primeiro nome, sem caixa/acento."""
        self.assertEqual(
            self.loader.buscar_vendedor_por_nome("Bianca").vendedor_id,
            "C0031",
        )
        self.assertEqual(
            self.loader.buscar_vendedor_por_nome("  BIANCA ").vendedor_id,
            "C0031",
        )
        self.assertEqual(
            self.loader.buscar_vendedor_por_nome("Ana Silva").vendedor_id,
            "C0032",
        )

    def test_busca_por_nome_inexistente_ou_ambiguo(self):
        """Nome inexistente e primeiro nome repetido levantam o mesmo erro."""
        with self.assertRaises(VendedorNaoEncontradoError):
            self.loader.buscar_vendedor_por_nome("Renata")

        # "Ana" casa com "Ana Silva" e "Ana Souza": a busca é ambígua.
        with self.assertRaises(VendedorNaoEncontradoError):
            self.loader.buscar_vendedor_por_nome("Ana")

    def test_arquivo_ausente_levanta_dados_indisponiveis(self):
        """O construtor não lê nada; o erro aparece na primeira chamada."""
        with tempfile.TemporaryDirectory() as nome_diretorio:
            diretorio = Path(nome_diretorio)
            arquivos = arquivos_padrao()
            del arquivos["anotacoes_gerente.csv"]
            escrever_arquivos(diretorio, arquivos)

            loader = DataLoader(data_dir=diretorio)

            # A leitura é preguiçosa: o construtor acima não falhou. O erro
            # só surge quando um método público precisa dos dados.
            with self.assertRaises(DadosIndisponiveisError) as contexto:
                loader.listar_vendedores()

            mensagem = str(contexto.exception)
            self.assertIn("anotacoes_gerente.csv", mensagem)

    def test_coluna_faltando_levanta_dados_indisponiveis(self):
        """Arquivo sem uma coluna obrigatória gera mensagem com o nome dela."""
        with tempfile.TemporaryDirectory() as nome_diretorio:
            diretorio = Path(nome_diretorio)
            arquivos = arquivos_padrao()
            # vendedores.csv sem a coluna "cargo".
            arquivos["vendedores.csv"] = (
                "vendedor_id,nome\nC0031,Bianca Rocha\n"
            )
            escrever_arquivos(diretorio, arquivos)

            loader = DataLoader(data_dir=diretorio)

            with self.assertRaises(DadosIndisponiveisError) as contexto:
                loader.listar_vendedores()

            mensagem = str(contexto.exception)
            self.assertIn("vendedores.csv", mensagem)
            self.assertIn("cargo", mensagem)


class TestDataLoaderComDadosReais(unittest.TestCase):
    """Teste de fumaça contra os CSVs reais de backend/data.

    "Fumaça" é uma verificação rápida para ver se o caminho principal funciona
    com os dados de verdade, sem montar cenários artificiais.
    """

    @classmethod
    def setUpClass(cls):
        """Cria um único DataLoader para todos os testes da classe."""
        cls.loader = DataLoader(data_dir=DATA_DIR)

    def test_lista_tem_8_vendedores(self):
        """Os dados reais têm 8 vendedores (e o gerente Diego fica de fora)."""
        vendedores = self.loader.listar_vendedores()

        self.assertEqual(len(vendedores), 8)
        self.assertTrue(
            all(vendedor.cargo == "vendedor" for vendedor in vendedores)
        )
        self.assertNotIn("C0030", [v.vendedor_id for v in vendedores])

    def test_gerente_real_tem_21_anotacoes(self):
        """O gerente real é Diego Furtado e o CSV tem 21 anotações."""
        gerente = self.loader.obter_gerente()

        self.assertEqual(gerente.nome, "Diego Furtado")
        self.assertEqual(gerente.total_anotacoes(), 21)

    def test_bianca_tem_quatro_meses_de_dados(self):
        """Bianca (C0031) tem dados de agosto a novembro de 2026."""
        bianca = self.loader.buscar_vendedor_por_nome("Bianca")

        self.assertEqual(bianca.vendedor_id, "C0031")
        self.assertEqual(
            bianca.meses_com_dados(),
            ("2026-08", "2026-09", "2026-10", "2026-11"),
        )
