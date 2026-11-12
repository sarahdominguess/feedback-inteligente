"""Testes da união das anotações da regional (CSV + anotações novas).

O DataLoader passou a aceitar o serviço das anotações novas da regional. Estes
testes garantem três coisas: sem o serviço nada muda, com o serviço a anotação
recém-gravada aparece na hora e a ordem cronológica é estável (no empate de
data, as do CSV vêm antes).
"""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from config import DATA_DIR
from services.data_loader import DataLoader
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)

# --- CSVs sintéticos da regional -------------------------------------------
# As anotações vêm de propósito FORA de ordem cronológica e com duas no mesmo
# dia: assim os testes provam que o DataLoader ordena por data e que, no
# empate, mantém a ordem do CSV.
ANOTACOES_REGIONAL = """\
data,autora,anotacao
2026-10-20,Patrícia Lemos,"conversar sobre a escala de sábado"
2026-09-10,Patrícia Lemos,"elogio ao time pelo atendimento"
2026-10-20,Patrícia Lemos,"segunda anotação do mesmo dia"
"""

METAS_LOJA = """\
mes,meta_valor
2026-10,317200.0
"""


def escrever_arquivos(diretorio: Path, arquivos: dict[str, str]) -> None:
    """Escreve cada texto em um arquivo com o nome indicado, em UTF-8.

    UTF-8: a codificação de texto que preserva acentos e é usada nos CSVs.
    """
    for nome, conteudo in arquivos.items():
        (diretorio / nome).write_text(conteudo, encoding="utf-8")


class TestDataLoaderComAnotacoesNovasDaRegional(unittest.TestCase):
    """Testes da mescla entre o CSV da regional e o serviço de anotações novas."""

    def setUp(self):
        """Cria a pasta temporária, os CSVs e o serviço de anotações novas.

        O arquivo do serviço também fica na pasta temporária: os testes nunca
        tocam no arquivo real de backend/data.
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.data_dir = Path(self._diretorio_temporario.name)
        escrever_arquivos(
            self.data_dir,
            {
                "anotacoes_regional.csv": ANOTACOES_REGIONAL,
                "metas_loja.csv": METAS_LOJA,
            },
        )

        self.arquivo_novas = self.data_dir / "anotacoes_regional_novas.json"
        self.servico = RegistroAnotacoesRegionalService(
            arquivo=self.arquivo_novas
        )
        self.loader = DataLoader(
            data_dir=self.data_dir,
            registro_anotacoes_regional=self.servico,
        )

    def test_servico_novo_inclui_anotacao_registrada(self):
        """Registrar uma anotação nova faz a leitura devolver CSV + nova.

        A nova tem data posterior a todas as do CSV, então deve aparecer no
        fim da lista (ordem cronológica).
        """
        self.servico.registrar(
            "visitar a loja na sexta", data=date(2026, 11, 12)
        )

        anotacoes = self.loader.listar_anotacoes_regional()

        self.assertEqual(len(anotacoes), 4)
        self.assertEqual(anotacoes[-1].texto, "visitar a loja na sexta")
        self.assertEqual(anotacoes[-1].data, date(2026, 11, 12))

    def test_anotacao_nova_anterior_entra_no_inicio(self):
        """Uma anotação com data antiga é encaixada na posição cronológica."""
        self.servico.registrar(
            "anotação antiga", data=date(2026, 1, 5)
        )

        anotacoes = self.loader.listar_anotacoes_regional()

        self.assertEqual(anotacoes[0].texto, "anotação antiga")
        datas = [anotacao.data for anotacao in anotacoes]
        self.assertEqual(datas, sorted(datas))

    def test_empate_de_data_mantem_as_do_csv_primeiro(self):
        """Na mesma data, as anotações do CSV vêm antes das novas.

        A ordenação é estável e recebe primeiro o CSV; por isso a nova fica
        depois das duas do CSV que têm a mesma data.
        """
        self.servico.registrar(
            "anotação nova no mesmo dia", data=date(2026, 10, 20)
        )

        anotacoes = self.loader.listar_anotacoes_regional()
        textos = [anotacao.texto for anotacao in anotacoes]

        self.assertEqual(
            textos,
            [
                "elogio ao time pelo atendimento",
                "conversar sobre a escala de sábado",
                "segunda anotação do mesmo dia",
                "anotação nova no mesmo dia",
            ],
        )

    def test_ordem_entre_as_novas_e_a_de_registro(self):
        """Duas novas com a mesma data saem na ordem em que foram gravadas."""
        self.servico.registrar("primeira nova", data=date(2026, 12, 1))
        self.servico.registrar("segunda nova", data=date(2026, 12, 1))

        anotacoes = self.loader.listar_anotacoes_regional()

        self.assertEqual(
            [anotacao.texto for anotacao in anotacoes][-2:],
            ["primeira nova", "segunda nova"],
        )

    def test_novas_sao_lidas_a_cada_chamada(self):
        """A anotação recém-gravada aparece na chamada seguinte, sem reiniciar.

        O CSV continua em cache; só o serviço é relido. Sem essa exceção ao
        cache, uma anotação nova só apareceria depois de reiniciar o servidor.
        """
        antes = self.loader.listar_anotacoes_regional()
        self.assertEqual(len(antes), 3)

        self.servico.registrar(
            "gravada depois da primeira leitura", data=date(2026, 12, 2)
        )

        depois = self.loader.listar_anotacoes_regional()
        self.assertEqual(len(depois), 4)
        self.assertEqual(
            depois[-1].texto, "gravada depois da primeira leitura"
        )

    def test_as_anotacoes_originais_nao_mudam(self):
        """O serviço só acrescenta: as três do CSV continuam idênticas.

        Comparamos o começo da lista com a leitura de um DataLoader SEM o
        serviço (o comportamento antigo).
        """
        loader_sem_servico = DataLoader(data_dir=self.data_dir)
        originais = loader_sem_servico.listar_anotacoes_regional()

        self.servico.registrar("anotação nova", data=date(2026, 12, 3))
        com_nova = self.loader.listar_anotacoes_regional()

        self.assertEqual(com_nova[: len(originais)], originais)


class TestDataLoaderSemServicoDaRegional(unittest.TestCase):
    """Sem o serviço, o comportamento antigo precisa continuar intacto."""

    def test_dados_reais_continuam_com_cinco_anotacoes(self):
        """O DataLoader sem o serviço vê exatamente as 5 anotações do CSV real."""
        loader = DataLoader(data_dir=DATA_DIR)

        anotacoes = loader.listar_anotacoes_regional()

        self.assertEqual(len(anotacoes), 5)
        self.assertEqual(
            {anotacao.autora for anotacao in anotacoes},
            {"Patrícia Lemos"},
        )

        # A ordem cronológica continua garantida.
        datas = [anotacao.data for anotacao in anotacoes]
        self.assertEqual(datas, sorted(datas))


if __name__ == "__main__":
    unittest.main()
