"""Testes das exceções da integração com a IA (Etapa 2).

Confere que os três erros novos herdam de DominioError, guardam a mensagem
recebida e podem ser capturados como erro de domínio. Assim, quem trata
DominioError trata também os problemas da LLM.
"""

import unittest

from domain.excecoes import (
    DominioError,
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
)


class TestExcecoesLLM(unittest.TestCase):
    """Verifica o comportamento das três exceções da integração com a IA."""

    # Pares (classe, mensagem de exemplo) usados em todos os testes.
    # Tupla: uma lista que não muda depois de criada.
    CASOS = (
        (LLMNaoConfiguradoError, "Chave da API ausente."),
        (LLMIndisponivelError, "Tempo de espera esgotado."),
        (LLMRespostaInvalidaError, "A resposta não é um JSON válido."),
    )

    def test_herdam_de_dominio_error(self):
        """As três exceções são filhas de DominioError.

        issubclass confere a herança: se for True, capturar DominioError
        também captura a exceção específica.
        """
        for classe, _ in self.CASOS:
            # subTest roda a mesma verificação para cada caso; se um falhar,
            # a mensagem mostra qual classe deu problema.
            with self.subTest(classe=classe.__name__):
                self.assertTrue(issubclass(classe, DominioError))

    def test_guardam_a_mensagem_recebida(self):
        """A mensagem em português continua disponível em str(erro).

        Uma exceção criada com uma mensagem deve devolver exatamente essa
        mensagem, para o usuário entender o que aconteceu.
        """
        for classe, mensagem in self.CASOS:
            with self.subTest(classe=classe.__name__):
                erro = classe(mensagem)
                self.assertEqual(str(erro), mensagem)

    def test_podem_ser_capturadas_como_dominio_error(self):
        """Quem captura DominioError também captura os erros da LLM.

        É o que permite à camada de cima ter um único tratamento para os
        problemas de negócio, sem precisar conhecer cada exceção específica.
        """
        for classe, mensagem in self.CASOS:
            with self.subTest(classe=classe.__name__):
                with self.assertRaises(DominioError):
                    raise classe(mensagem)

    def test_excecoes_sao_distintas_entre_si(self):
        """Nenhuma das três exceções é filha de outra do mesmo grupo.

        Cada situação tem seu próprio tipo, o que permite reações diferentes:
        configurar a chave, tentar de novo depois ou avisar resposta inválida.
        """
        tipos = [classe for classe, _ in self.CASOS]

        for classe in tipos:
            for outra in tipos:
                if classe is not outra:
                    with self.subTest(classe=classe.__name__, outra=outra.__name__):
                        self.assertFalse(issubclass(classe, outra))
