"""Testes do serviço que grava as anotações novas da regional num JSON.

Todos usam um arquivo temporário (tempfile), nunca o arquivo real do projeto:
assim os testes não dependem nem alteram dados de execução.
"""

import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path

from config import ANOTACAO_TEXTO_MAXIMO, REGIONAL_NOME
from domain.excecoes import AnotacaoInvalidaError, DadosIndisponiveisError
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)


class TestRegistroAnotacoesRegionalService(unittest.TestCase):
    """Testes de validação, leitura, gravação e concorrência do serviço."""

    def setUp(self):
        """Cria uma pasta temporária e um serviço apontando para um arquivo nela.

        TemporaryDirectory é apagada pelo próprio Python no fim do teste
        (registramos o cleanup com addCleanup).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.diretorio = Path(self._diretorio_temporario.name)
        self.arquivo = self.diretorio / "anotacoes_regional_novas.json"
        self.service = RegistroAnotacoesRegionalService(arquivo=self.arquivo)

    def test_arquivo_inexistente_devolve_lista_vazia(self):
        """Sem arquivo, a leitura devolve () e não cria nada no disco.

        Arquivo ausente é o estado normal antes da primeira anotação; não é
        erro e nem deve criar um arquivo vazio à toa.
        """
        self.assertEqual(self.service.listar(), ())
        self.assertFalse(self.arquivo.exists())

    def test_registrar_grava_e_listar_devolve(self):
        """A anotação registrada aparece na leitura seguinte, com os dados.

        Lemos de uma instância NOVA para garantir que o dado ficou no disco
        (e não só na memória do primeiro serviço).
        """
        self.service.registrar(
            "visitar a loja na sexta",
            data=date(2026, 11, 12),
        )

        outro_service = RegistroAnotacoesRegionalService(
            arquivo=self.arquivo
        )
        anotacoes = outro_service.listar()

        self.assertEqual(len(anotacoes), 1)
        self.assertEqual(anotacoes[0].texto, "visitar a loja na sexta")
        self.assertEqual(anotacoes[0].autora, REGIONAL_NOME)
        self.assertEqual(anotacoes[0].data, date(2026, 11, 12))

    def test_listar_devolve_na_ordem_em_que_foram_registradas(self):
        """Três anotações saem na mesma ordem da gravação (mais antiga antes)."""
        primeira = self.service.registrar("primeira")
        segunda = self.service.registrar("segunda")
        terceira = self.service.registrar("terceira")

        anotacoes = self.service.listar()

        self.assertEqual(
            [anotacao.texto for anotacao in anotacoes],
            [primeira.texto, segunda.texto, terceira.texto],
        )

    def test_espacos_nas_pontas_saem_do_texto(self):
        """Só as pontas são aparadas; as quebras de linha do meio ficam."""
        anotacao = self.service.registrar(
            "\n\t  primeira linha\nsegunda linha  \t\n"
        )

        self.assertEqual(
            anotacao.texto, "primeira linha\nsegunda linha"
        )

    def test_autora_padrao_e_a_regional(self):
        """Sem informar autora, o registro sai com o nome da regional fixa."""
        anotacao = self.service.registrar("texto válido")

        self.assertEqual(anotacao.autora, REGIONAL_NOME)

    def test_data_de_hoje_e_usada_quando_nao_informada(self):
        """Sem data, vale o dia do relógio do servidor (não o do navegador).

        Comparamos com a data antes e depois da chamada para o teste não
        falhar se ele rodar exatamente na virada da meia-noite.
        """
        antes = date.today()
        anotacao = self.service.registrar("anotação do dia")
        depois = date.today()

        self.assertIn(anotacao.data, (antes, depois))

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
        texto_no_limite = "a" * ANOTACAO_TEXTO_MAXIMO

        anotacao = self.service.registrar(texto_no_limite)

        self.assertEqual(len(anotacao.texto), ANOTACAO_TEXTO_MAXIMO)

    def test_autora_vazia_e_recusada(self):
        """Sem autora, o registro não pode ser gravado."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar("texto válido", autora="   ")

        self.assertFalse(self.arquivo.exists())

    def test_data_com_horario_e_recusada(self):
        """datetime ("dia + hora") é recusado em vez de perder a hora calado."""
        with self.assertRaises(AnotacaoInvalidaError):
            self.service.registrar(
                "texto",
                data=datetime(2026, 11, 12, 14, 30),
            )

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

    def test_duas_threads_gravando_nao_perdem_registros(self):
        """Oito gravações simultâneas: todas aparecem no arquivo.

        Sem o cadeado (lock), duas threads poderiam ler a mesma lista e a
        segunda gravação apagaria a da primeira. A barreira (Barrier) solta
        todas as threads no mesmo instante para forçar essa disputa.
        """
        quantidade = 8
        barreira = threading.Barrier(quantidade)

        def gravar(indice):
            # Cada thread espera as outras chegarem antes de tentar gravar.
            barreira.wait()
            self.service.registrar(f"anotação da thread {indice}")

        with ThreadPoolExecutor(max_workers=quantidade) as executor:
            listas = [
                executor.submit(gravar, indice)
                for indice in range(quantidade)
            ]
            # result() também relança qualquer erro ocorrido dentro da thread.
            for tarefa in listas:
                tarefa.result()

        anotacoes = self.service.listar()
        textos = {anotacao.texto for anotacao in anotacoes}

        self.assertEqual(len(anotacoes), quantidade)
        self.assertEqual(
            textos,
            {f"anotação da thread {indice}" for indice in range(quantidade)},
        )


if __name__ == "__main__":
    unittest.main()
