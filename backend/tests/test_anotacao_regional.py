"""Testes da entidade AnotacaoRegional.

Verificam que uma anotação da regional guarda os dados recebidos e que, depois
de criada, não pode ser alterada — garantia importante porque ela é um registro
histórico do que foi escrito, não um rascunho.
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from domain.anotacao_regional import AnotacaoRegional


class TestAnotacaoRegional(unittest.TestCase):
    """Testes da entidade que representa uma anotação da gerente regional."""

    def _criar_valida(self) -> AnotacaoRegional:
        """Cria uma anotação válida para reaproveitar nos testes.

        O "_" no começo do nome indica que é um método auxiliar interno,
        usado apenas dentro desta classe de testes.
        """
        return AnotacaoRegional(
            data=date(2026, 10, 20),
            autora="Patrícia Lemos",
            texto="Conversar com o Diego sobre a escala de sábado.",
        )

    def test_cria_anotacao_valida(self):
        """Com dados válidos, o objeto guarda exatamente o que recebeu.

        É o teste mais básico: se a ordem dos campos estivesse trocada, os
        valores apareceriam no campo errado aqui.
        """
        anotacao = self._criar_valida()

        self.assertEqual(anotacao.data, date(2026, 10, 20))
        self.assertEqual(anotacao.autora, "Patrícia Lemos")
        self.assertEqual(
            anotacao.texto,
            "Conversar com o Diego sobre a escala de sábado.",
        )

    def test_e_imutavel(self):
        """Depois de criada, a anotação não aceita alteração de atributo.

        frozen=True faz o Python levantar FrozenInstanceError ("instância
        congelada") quando tentamos mudar um valor.
        """
        anotacao = self._criar_valida()

        with self.assertRaises(FrozenInstanceError):
            anotacao.texto = "Texto trocado depois da criação"
