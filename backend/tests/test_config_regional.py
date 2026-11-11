"""Testes das constantes dos CSVs da regional (Etapa 3).

Este arquivo é novo de propósito: o test_config.py já existente cobre a
configuração antiga e não deve ser alterado. Aqui só confirmamos que os dois
arquivos copiados para backend/data estão realmente no lugar esperado — se
faltarem, a visão executiva da regional quebra só na hora de rodar.
"""

import unittest

from config import (
    ARQUIVO_ANOTACOES_REGIONAL,
    ARQUIVO_METAS_LOJA,
    DATA_DIR,
)


class TestConfigRegional(unittest.TestCase):
    """Testes das constantes e dos arquivos da visão regional."""

    def test_nomes_das_constantes(self):
        """As constantes devem guardar exatamente os nomes dos CSVs.

        O código monta o caminho como DATA_DIR + nome; se o nome tivesse uma
        letra errada, o arquivo não seria encontrado.
        """
        self.assertEqual(ARQUIVO_ANOTACOES_REGIONAL, "anotacoes_regional.csv")
        self.assertEqual(ARQUIVO_METAS_LOJA, "metas_loja.csv")

    def test_arquivos_existem_em_data_dir(self):
        """Os dois CSVs da regional precisam existir dentro de DATA_DIR.

        is_file() devolve True apenas quando o caminho existe E é um arquivo
        (não uma pasta), que é exatamente o que o leitor de CSV precisa.
        """
        for nome_arquivo in (
            ARQUIVO_ANOTACOES_REGIONAL,
            ARQUIVO_METAS_LOJA,
        ):
            # subTest identifica qual arquivo faltou, sem parar no primeiro.
            with self.subTest(arquivo=nome_arquivo):
                caminho = DATA_DIR / nome_arquivo
                self.assertTrue(
                    caminho.is_file(),
                    f"Arquivo esperado não encontrado: {caminho}",
                )
