"""Testes da entidade RegistroFeedback.

Verificam a ida e volta para dicionário (preservando o horário com fuso),
a imutabilidade e as recusas de dados inválidos na leitura do registro.
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from domain.registro_feedback import RegistroFeedback


class TestRegistroFeedback(unittest.TestCase):
    """Testes da entidade que guarda um roteiro já gerado."""

    def _criar_valido(self) -> RegistroFeedback:
        """Cria um registro válido para reaproveitar nos testes.

        O horário é 11/11/2026 às 14h em UTC (o "horário universal", igual em
        qualquer país), então o texto ISO deve terminar em "+00:00".
        """
        return RegistroFeedback(
            vendedor_id="C0031",
            vendedor_nome="Bianca Rocha",
            gerado_em=datetime(2026, 11, 11, 14, 0, tzinfo=timezone.utc),
            mes_referencia="2026-10",
            roteiro={
                "pontos_positivos": ["Alta conversão com as clientes"],
                "pontos_melhoria": ["Vender mais de uma peça por atendimento"],
                "possiveis_motivos": ["Muitas clientes ao mesmo tempo"],
                "roteiro_conversa": ["Como foi o sábado mais cheio?"],
            },
        )

    def test_ida_e_volta_preserva_horario_com_fuso(self):
        """para_dict e de_dict devolvem um registro igual, com o mesmo horário.

        A data vira texto no padrão ISO 8601 ("...+00:00") e volta como
        datetime com fuso UTC, sem perder a hora.
        """
        registro = self._criar_valido()

        dicionario = registro.para_dict()
        self.assertEqual(
            dicionario["gerado_em"], "2026-11-11T14:00:00+00:00"
        )

        recriado = RegistroFeedback.de_dict(dicionario)

        self.assertEqual(recriado, registro)
        self.assertEqual(
            recriado.gerado_em,
            datetime(2026, 11, 11, 14, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(recriado.gerado_em.utcoffset().total_seconds(), 0)

    def test_feedback_id_e_gerado_e_unico(self):
        """Sem informar o ID, cada registro recebe um texto único (uuid4).

        Dois registros criados em sequência não podem ter o mesmo ID.
        """
        primeiro = self._criar_valido()
        segundo = self._criar_valido()

        self.assertIsInstance(primeiro.feedback_id, str)
        self.assertTrue(primeiro.feedback_id)
        self.assertNotEqual(primeiro.feedback_id, segundo.feedback_id)

    def test_e_imutavel(self):
        """Depois de criado, o registro não aceita alteração de atributo.

        frozen=True faz o Python levantar FrozenInstanceError ("instância
        congelada") quando tentamos mudar um valor.
        """
        registro = self._criar_valido()

        with self.assertRaises(FrozenInstanceError):
            registro.vendedor_nome = "Outro Nome"

    def test_de_dict_com_campo_faltando_levanta_erro(self):
        """Faltando qualquer campo obrigatório, a leitura falha com ValueError.

        Testamos os cinco campos obrigatórios, um por vez. mes_referencia fica
        de fora porque None é um valor válido para ele.
        """
        dicionario = self._criar_valido().para_dict()

        for campo in (
            "feedback_id",
            "vendedor_id",
            "vendedor_nome",
            "gerado_em",
            "roteiro",
        ):
            # subTest mostra qual campo faltou, sem parar os outros casos.
            with self.subTest(campo=campo):
                incompleto = dict(dicionario)
                del incompleto[campo]

                with self.assertRaises(ValueError):
                    RegistroFeedback.de_dict(incompleto)

    def test_de_dict_com_data_invalida_levanta_erro(self):
        """Texto que não é data (ou data sem fuso) levanta ValueError."""
        dicionario = self._criar_valido().para_dict()

        dicionario["gerado_em"] = "ontem de manhã"
        with self.assertRaises(ValueError):
            RegistroFeedback.de_dict(dicionario)

        # Data válida, mas sem fuso: não sabemos o horário real.
        dicionario["gerado_em"] = "2026-11-11T14:00:00"
        with self.assertRaises(ValueError):
            RegistroFeedback.de_dict(dicionario)

    def test_de_dict_com_tipo_errado_levanta_erro(self):
        """Campos com o tipo errado também são recusados com ValueError."""
        dicionario = self._criar_valido().para_dict()

        # vendedor_id precisa ser texto, não número.
        dicionario["vendedor_id"] = 31
        with self.assertRaises(ValueError):
            RegistroFeedback.de_dict(dicionario)

        # roteiro precisa ser dicionário, não lista.
        dicionario = self._criar_valido().para_dict()
        dicionario["roteiro"] = ["lista solta"]
        with self.assertRaises(ValueError):
            RegistroFeedback.de_dict(dicionario)
