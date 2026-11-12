"""Testes do serviço que grava as anotações novas da regional.

Todos usam um arquivo temporário (tempfile), nunca o arquivo real do projeto:
assim os testes não dependem nem alteram dados de execução. O teste de
integração com o DataLoader usa os CSVs reais apenas para LEITURA.
"""

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from config import ANOTACAO_TEXTO_MAXIMO, DATA_DIR
from domain.excecoes import AnotacaoInvalidaError, DadosIndisponiveisError
from services.data_loader import DataLoader
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)


class TestRegistroAnotacoesRegionalService(unittest.TestCase):
    """Testes de validação, gravação e leitura do arquivo JSON."""

    def setUp(self):
        """Cria uma pasta temporária e um serviço apontando para um arquivo nela."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.diretorio = Path(self._diretorio_temporario.name)
        self.arquivo = self.diretorio / "anotacoes_regional_novas.json"
        self.service = RegistroAnotacoesRegionalService(arquivo=self.arquivo)

    def test_arquivo_inexistente_devolve_lista_vazia(self):
        """Sem arquivo, a leitura devolve [] e não cria nada no disco."""
        self.assertEqual(self.service.listar(), [])
        self.assertFalse(self.arquivo.exists())

    def test_registrar_e_listar(self):
        """A anotação gravada volta com data, autora e texto informados."""
        anotacao = self.service.registrar(
            "conversar sobre a escala de sábado",
            data_anotacao=date(2026, 10, 20),
        )

        self.assertEqual(anotacao.texto, "conversar sobre a escala de sábado")
        self.assertEqual(anotacao.autora, "Patrícia Lemos")
        self.assertEqual(anotacao.data, date(2026, 10, 20))

        # E também aparece na leitura do arquivo.
        anotacoes = self.service.listar()
        self.assertEqual(len(anotacoes), 1)
        self.assertEqual(anotacoes[0].texto, "conversar sobre a escala de sábado")

    def test_persistencia_entre_duas_instancias(self):
        """O segundo serviço lê o que o primeiro gravou (o dado fica no disco)."""
        self.service.registrar("anotação que ficou no arquivo")

        outro_service = RegistroAnotacoesRegionalService(arquivo=self.arquivo)

        self.assertEqual(len(outro_service.listar()), 1)
        self.assertEqual(
            outro_service.listar()[0].texto, "anotação que ficou no arquivo"
        )

    def test_espacos_nas_pontas_saem_do_texto(self):
        """Só as pontas perdem espaço; as quebras de linha do meio ficam."""
        anotacao = self.service.registrar(
            "\n  primeira linha\nsegunda linha  \t\n"
        )

        self.assertEqual(anotacao.texto, "primeira linha\nsegunda linha")

    def test_texto_vazio_e_recusado(self):
        """Texto vazio não vira anotação e nada é gravado no disco."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("")

        self.assertFalse(self.arquivo.exists())

    def test_texto_so_com_espacos_e_recusado(self):
        """Texto só com espaços/quebras de linha é o mesmo que vazio."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("   \n\t  ")

        self.assertFalse(self.arquivo.exists())

    def test_texto_acima_do_limite_e_recusado(self):
        """Uma letra além de ANOTACAO_TEXTO_MAXIMO já é recusada."""
        texto_longo = "a" * (ANOTACAO_TEXTO_MAXIMO + 1)

        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar(texto_longo)

        self.assertFalse(self.arquivo.exists())

    def test_texto_exatamente_no_limite_e_aceito(self):
        """No limite exato ainda vale: o limite é o máximo permitido."""
        anotacao = self.service.registrar("a" * ANOTACAO_TEXTO_MAXIMO)

        self.assertEqual(len(anotacao.texto), ANOTACAO_TEXTO_MAXIMO)

    def test_autora_padrao_e_patricia(self):
        """Sem informar a autora, a anotação é assinada pela Patrícia."""
        anotacao = self.service.registrar("texto qualquer")

        self.assertEqual(anotacao.autora, "Patrícia Lemos")

    def test_arquivo_corrompido_levanta_erro_e_preserva_conteudo(self):
        """JSON inválido dá erro claro e o arquivo não é apagado nem trocado."""
        conteudo_original = "isto não é um JSON!"
        self.arquivo.write_text(conteudo_original, encoding="utf-8")

        with self.assertRaises(DadosIndisponiveisError):
            self.service.listar()

        # Tentar registrar também falha e não sobrescreve o arquivo.
        with self.assertRaises(DadosIndisponiveisError):
            self.service.registrar("texto válido")

        self.assertEqual(
            self.arquivo.read_text(encoding="utf-8"), conteudo_original
        )

    def test_formato_inesperado_levanta_erro(self):
        """JSON válido que não é uma lista (ex.: um objeto) também é recusado."""
        self.arquivo.write_text(
            json.dumps({"anotacoes": []}), encoding="utf-8"
        )

        with self.assertRaises(DadosIndisponiveisError):
            self.service.listar()

    def test_nao_deixa_arquivo_temporario(self):
        """Depois de gravar, sobra só o arquivo oficial na pasta."""
        self.service.registrar("texto")

        self.assertEqual(
            [caminho.name for caminho in self.diretorio.iterdir()],
            ["anotacoes_regional_novas.json"],
        )


class TestDataLoaderComAnotacoesRegionaisNovas(unittest.TestCase):
    """Testes da junção entre o CSV da regional e o serviço de anotações novas."""

    def setUp(self):
        """Serviço temporário + DataLoader apontando para os CSVs reais (leitura)."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.arquivo = (
            Path(self._diretorio_temporario.name)
            / "anotacoes_regional_novas.json"
        )
        self.service = RegistroAnotacoesRegionalService(arquivo=self.arquivo)

    def _loader_com_servico(self) -> DataLoader:
        """DataLoader com o serviço temporário de anotações da regional."""
        return DataLoader(
            data_dir=DATA_DIR,
            registro_anotacoes_regional=self.service,
        )

    def test_sem_servico_o_resultado_e_o_do_csv(self):
        """Sem registro_anotacoes_regional, só as 5 anotações do CSV aparecem."""
        loader = DataLoader(data_dir=DATA_DIR)

        self.assertEqual(len(loader.listar_anotacoes_regional()), 5)

    def test_anotacao_nova_entra_na_lista_do_csv(self):
        """A anotação gravada no serviço aparece somada às 5 do CSV.

        A data usada é posterior às do CSV, então ela entra no fim — e a lista
        continua em ordem cronológica.
        """
        self.service.registrar(
            "anotação de teste da regional", data_anotacao=date(2026, 11, 12)
        )

        anotacoes = self._loader_com_servico().listar_anotacoes_regional()

        self.assertEqual(len(anotacoes), 6)
        self.assertEqual(anotacoes[-1].texto, "anotação de teste da regional")
        self.assertEqual(anotacoes[-1].autora, "Patrícia Lemos")

        # A ordem é cronológica (datas não decrescentes).
        datas = [anotacao.data for anotacao in anotacoes]
        self.assertEqual(datas, sorted(datas))

    def test_anotacao_gravada_depois_do_uso_aparece_na_leitura_seguinte(self):
        """O serviço é relido a cada chamada: nada fica congelado em cache."""
        loader = self._loader_com_servico()

        antes = loader.listar_anotacoes_regional()
        self.assertEqual(len(antes), 5)

        self.service.registrar("escrita depois da primeira leitura")

        depois = loader.listar_anotacoes_regional()
        self.assertEqual(len(depois), 6)


if __name__ == "__main__":
    unittest.main()
