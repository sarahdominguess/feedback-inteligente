"""Testes do serviço que grava as anotações novas num arquivo JSON.

Todos usam um arquivo temporário (tempfile), nunca o arquivo real do projeto:
assim os testes não dependem nem alteram dados de execução.
"""

import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from config import ANOTACAO_TEXTO_MAXIMO
from domain.excecoes import AnotacaoInvalidaError, DadosIndisponiveisError
from services.registro_anotacoes import RegistroAnotacoesService


class TestRegistroAnotacoesService(unittest.TestCase):
    """Testes de validação, leitura, gravação e persistência do serviço."""

    def setUp(self):
        """Cria uma pasta temporária e um serviço apontando para um arquivo nela.

        TemporaryDirectory é apagada pelo próprio Python no fim do teste
        (registramos o cleanup com addCleanup).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.diretorio = Path(self._diretorio_temporario.name)
        self.arquivo = self.diretorio / "anotacoes_novas.json"
        self.service = RegistroAnotacoesService(arquivo=self.arquivo)

    def test_arquivo_inexistente_devolve_lista_vazia(self):
        """Sem arquivo, a leitura devolve () e não cria nada no disco.

        Arquivo ausente é o estado normal antes da primeira anotação; não é
        erro e nem deve criar um arquivo vazio à toa.
        """
        self.assertEqual(self.service.listar(), ())
        self.assertFalse(self.arquivo.exists())

    def test_registrar_devolve_a_anotacao_gravada(self):
        """registrar devolve a Anotacao com os dados informados.

        A data informada volta igual e o texto aparece como foi gravado.
        """
        anotacao = self.service.registrar(
            "Bianca Rocha",
            "cliente elogiou o atendimento no sábado",
            data=date(2026, 10, 8),
        )

        self.assertEqual(anotacao.sobre, "Bianca Rocha")
        self.assertEqual(
            anotacao.texto, "cliente elogiou o atendimento no sábado"
        )
        self.assertEqual(anotacao.data, date(2026, 10, 8))

    def test_listar_devolve_na_ordem_em_que_foram_registradas(self):
        """Três anotações saem na mesma ordem da gravação (mais antiga antes).

        O serviço não reordena: a ordem de exibição é decisão de quem mostra.
        """
        primeira = self.service.registrar("Bianca Rocha", "primeira")
        segunda = self.service.registrar("Bianca Rocha", "segunda")
        terceira = self.service.registrar("(time)", "terceira")

        anotacoes = self.service.listar()

        self.assertEqual(
            [anotacao.texto for anotacao in anotacoes],
            [primeira.texto, segunda.texto, terceira.texto],
        )

    def test_persistencia_entre_duas_instancias(self):
        """O segundo serviço lê o que o primeiro gravou (o dado fica no disco)."""
        self.service.registrar("Bianca Rocha", "anotação que ficou no arquivo")

        outro_service = RegistroAnotacoesService(arquivo=self.arquivo)

        anotacoes = outro_service.listar()
        self.assertEqual(len(anotacoes), 1)
        self.assertEqual(
            anotacoes[0].texto, "anotação que ficou no arquivo"
        )

    def test_espacos_nas_pontas_saem_do_texto(self):
        """Espaços, tabulações e quebras de linha das pontas são removidos."""
        anotacao = self.service.registrar(
            "  Bianca Rocha  ", "\n\t  texto com espaços nas pontas  \t\n"
        )

        # O texto do meio é preservado; só as pontas perdem espaço.
        self.assertEqual(anotacao.texto, "texto com espaços nas pontas")
        # O "sobre" também perde os espaços das pontas.
        self.assertEqual(anotacao.sobre, "Bianca Rocha")

    def test_texto_vazio_e_recusado(self):
        """Texto vazio não vira anotação e nada é gravado no disco."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("Bianca Rocha", "")

        # O arquivo nem chega a ser criado: a recusa acontece antes da gravação.
        self.assertFalse(self.arquivo.exists())

    def test_texto_so_com_espacos_e_recusado(self):
        """Texto só com espaços/quebras de linha é o mesmo que vazio."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("Bianca Rocha", "   \n\t  ")

        self.assertFalse(self.arquivo.exists())

    def test_texto_acima_do_limite_e_recusado(self):
        """Uma letra além de ANOTACAO_TEXTO_MAXIMO já é recusada."""
        texto_longo = "a" * (ANOTACAO_TEXTO_MAXIMO + 1)

        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("Bianca Rocha", texto_longo)

        self.assertFalse(self.arquivo.exists())

    def test_texto_exatamente_no_limite_e_aceito(self):
        """No limite exato ainda vale: o limite é o máximo permitido."""
        texto_no_limite = "a" * ANOTACAO_TEXTO_MAXIMO

        anotacao = self.service.registrar("Bianca Rocha", texto_no_limite)

        self.assertEqual(len(anotacao.texto), ANOTACAO_TEXTO_MAXIMO)

    def test_sobre_vazio_e_recusado(self):
        """Sem saber de quem é a anotação, nada é gravado."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("   ", "texto válido")

        self.assertFalse(self.arquivo.exists())

    def test_acentos_e_quebras_de_linha_do_meio_sao_preservados(self):
        """O texto é guardado como digitado: acentos e várias linhas.

        Lemos de uma instância nova para garantir que o arquivo (e não a
        memória) devolve exatamente o mesmo texto.
        """
        texto = (
            "Cliente elogiou a Bianca.\n"
            "Pediu o contato da loja.\n"
            "Ótimo atendimento, disse que voltará!"
        )

        self.service.registrar("Bianca Rocha", texto)

        outro_service = RegistroAnotacoesService(arquivo=self.arquivo)
        self.assertEqual(outro_service.listar()[0].texto, texto)

    def test_data_de_hoje_e_usada_quando_nao_informada(self):
        """Sem data, vale o dia do relógio do servidor (não o do navegador).

        Comparamos com a data antes e depois da chamada para o teste não
        falhar se ele rodar exatamente na virada da meia-noite.
        """
        antes = date.today()
        anotacao = self.service.registrar("Bianca Rocha", "anotação do dia")
        depois = date.today()

        self.assertIn(anotacao.data, (antes, depois))

    def test_data_com_horario_e_recusada(self):
        """datetime ("dia + hora") é recusado em vez de perder a hora calado."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar(
                "Bianca Rocha",
                "texto",
                data=datetime(2026, 10, 8, 14, 30),
            )

    def test_arquivo_corrompido_levanta_erro_e_preserva_conteudo(self):
        """JSON inválido dá erro claro e o arquivo não é apagado nem trocado."""
        conteudo_original = "isto não é um JSON!"
        self.arquivo.write_text(conteudo_original, encoding="utf-8")

        with self.assertRaises(DadosIndisponiveisError):
            self.service.listar()

        # Tentar registrar também falha e não sobrescreve o arquivo.
        with self.assertRaises(DadosIndisponiveisError):
            self.service.registrar("Bianca Rocha", "texto válido")

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
        self.service.registrar("Bianca Rocha", "texto")

        self.assertEqual(
            [caminho.name for caminho in self.diretorio.iterdir()],
            ["anotacoes_novas.json"],
        )


if __name__ == "__main__":
    unittest.main()
