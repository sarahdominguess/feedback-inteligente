"""Testes da configuração central (backend/config.py).

Estes testes conferem se os arquivos de dados estão no lugar certo e se as
informações da loja estão corretas. Se falharem, é sinal de que o backend não
vai encontrar os CSVs ou de que uma constante mudou sem querer.
"""

import unittest

from config import (
    ANOTACAO_SOBRE_TIME,
    ARQUIVO_ANOTACOES_GERENTE,
    ARQUIVO_INDICADORES_DIARIOS,
    ARQUIVO_METAS_VENDEDOR,
    ARQUIVO_VENDEDORES,
    DATA_DIR,
    LOJA_ID,
    LOJA_NOME,
)


class TestConfig(unittest.TestCase):
    """Confere os caminhos e as constantes que o backend inteiro utiliza."""

    def test_data_dir_existe(self):
        """A pasta backend/data precisa existir para os CSVs serem lidos.

        is_dir() devolve True quando o caminho existe e é uma pasta.
        """
        self.assertTrue(DATA_DIR.is_dir(), f"Pasta não encontrada: {DATA_DIR}")

    def test_arquivos_de_dados_existem(self):
        """Os 4 CSVs copiados do desafio precisam estar dentro de DATA_DIR.

        Para cada nome, montamos o caminho completo juntando a pasta e o nome
        (o operador "/" do Path faz essa junção). is_file() devolve True quando
        existe um arquivo naquele caminho.
        """
        arquivos = (
            ARQUIVO_VENDEDORES,
            ARQUIVO_INDICADORES_DIARIOS,
            ARQUIVO_METAS_VENDEDOR,
            ARQUIVO_ANOTACOES_GERENTE,
        )

        for nome in arquivos:
            # subTest permite verificar os quatro arquivos de uma vez: se um
            # faltar, a mensagem mostra qual, sem interromper os demais.
            with self.subTest(arquivo=nome):
                caminho = DATA_DIR / nome
                self.assertTrue(
                    caminho.is_file(), f"Arquivo não encontrado: {caminho}"
                )

    def test_identificacao_da_loja(self):
        """A loja do desafio é a L004 — Aurora Shopping Centro.

        assertEqual compara o valor recebido com o esperado; se forem
        diferentes, o teste falha e mostra os dois valores.
        """
        self.assertEqual(LOJA_ID, "L004")
        self.assertEqual(LOJA_NOME, "Aurora Shopping Centro")

    def test_texto_de_anotacao_do_time(self):
        """O texto combinado para anotações sobre o time inteiro é "(time)"."""
        self.assertEqual(ANOTACAO_SOBRE_TIME, "(time)")
