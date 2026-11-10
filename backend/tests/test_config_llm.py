"""Testes das configurações da integração com a DeepSeek (Etapa 2).

Confere as constantes criadas em backend/config.py: endereço do provedor,
nomes das variáveis de ambiente, limites da chamada e o caminho do .env.
Nenhum teste aqui chama a internet.
"""

import unittest
from pathlib import Path

import config


class TestConfigLLM(unittest.TestCase):
    """Cada teste confere um grupo de constantes da integração com a IA."""

    def test_endereco_do_provedor(self):
        """A SDK deve falar com o endereço oficial da DeepSeek.

        Se este valor mudar sem querer, as chamadas passariam a apontar para
        outro lugar e falhariam; por isso o teste fixa o endereço esperado.
        """
        self.assertEqual(config.LLM_BASE_URL, "https://api.deepseek.com")

    def test_nomes_das_variaveis_de_ambiente(self):
        """Os nomes das variáveis são os mesmos usados no .env.example.

        Se um nome divergir, o serviço da LLM procuraria uma variável que
        ninguém preencheu e concluiria (errado) que falta configuração.
        """
        self.assertEqual(config.ENV_DEEPSEEK_API_KEY, "DEEPSEEK_API_KEY")
        self.assertEqual(config.ENV_DEEPSEEK_MODEL, "DEEPSEEK_MODEL")
        self.assertEqual(config.ENV_DEEPSEEK_THINKING, "DEEPSEEK_THINKING")

    def test_modelo_padrao_nao_e_vazio(self):
        """Sempre existe um nome de modelo para usar quando o .env não define.

        strip() remove espaços das pontas; um valor só com espaços contaria
        como vazio e o teste falharia, como deve ser.
        """
        self.assertTrue(config.LLM_MODELO_PADRAO.strip())

    def test_limites_da_chamada(self):
        """Timeout, tokens, temperatura e tentativas têm valores coerentes.

        - tempo de espera de zero ou menos seria uma espera inválida;
        - limite de tokens precisa ser positivo para caber uma resposta;
        - temperatura fica entre 0 e 1 (fora disso não faz sentido);
        - a SDK precisa poder fazer pelo menos uma tentativa.
        """
        self.assertGreater(config.LLM_TIMEOUT_SEGUNDOS, 0)
        self.assertGreater(config.LLM_MAX_TOKENS, 0)
        self.assertGreaterEqual(config.LLM_TEMPERATURA, 0)
        self.assertLessEqual(config.LLM_TEMPERATURA, 1)
        self.assertGreaterEqual(config.LLM_MAX_TENTATIVAS_SDK, 1)

    def test_thinking_padrao_aceito(self):
        """O padrão do thinking é um dos três valores combinados.

        O serviço da LLM só sabe tratar "disabled", "enabled" e "omitir";
        qualquer outro texto seria erro de configuração.
        """
        self.assertIn(
            config.LLM_THINKING_PADRAO, ("disabled", "enabled", "omitir")
        )

    def test_caminho_do_arquivo_env(self):
        """ENV_FILE aponta para backend/.env, de forma absoluta.

        Path: molde do Python para representar caminhos. O teste confere que
        o caminho é absoluto (funciona de qualquer pasta), que o nome do
        arquivo é .env e que ele fica na mesma pasta deste config.py.
        """
        self.assertIsInstance(config.ENV_FILE, Path)
        self.assertTrue(config.ENV_FILE.is_absolute())
        self.assertEqual(config.ENV_FILE.name, ".env")
        self.assertEqual(
            config.ENV_FILE.parent,
            Path(config.__file__).resolve().parent,
        )
