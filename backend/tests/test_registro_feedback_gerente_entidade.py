"""Testes da entidade RegistroFeedbackGerente.

Verificam a ida e volta para dicionário (preservando o horário com fuso), a
imutabilidade, a cópia defensiva das listas do roteiro e as recusas de dados
inválidos na leitura do registro.
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from domain.registro_feedback_gerente import RegistroFeedbackGerente


class TestRegistroFeedbackGerente(unittest.TestCase):
    """Testes da entidade que guarda um roteiro gerado para o gerente."""

    def _criar_valido(self) -> RegistroFeedbackGerente:
        """Cria um registro válido para reaproveitar nos testes.

        O horário é 12/11/2026 às 14h em UTC (o "horário universal", igual em
        qualquer país), então o texto ISO deve terminar em "+00:00".
        """
        return RegistroFeedbackGerente(
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            gerente_id="C0030",
            gerente_nome="Diego Furtado",
            gerado_em=datetime(2026, 11, 12, 14, 0, tzinfo=timezone.utc),
            mes_referencia="2026-10",
            roteiro={
                "pontos_positivos": ["Loja organizada e time engajado"],
                "pontos_melhoria": ["Delegar mais o caixa no horário de pico"],
                "possiveis_motivos": ["Muita demanda em horário concentrado"],
                "roteiro_conversa": ["Como foi a semana com o time?"],
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
            dicionario["gerado_em"], "2026-11-12T14:00:00+00:00"
        )

        recriado = RegistroFeedbackGerente.de_dict(dicionario)

        self.assertEqual(recriado, registro)
        self.assertEqual(
            recriado.gerado_em,
            datetime(2026, 11, 12, 14, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(recriado.gerado_em.utcoffset().total_seconds(), 0)

    def test_mes_referencia_pode_ser_none(self):
        """Sem mês escolhido, o registro vale para todo o histórico.

        O campo pode faltar no dicionário lido: None é um valor válido, e não
        um dado ausente.
        """
        registro = self._criar_valido()
        dicionario = registro.para_dict()

        dicionario["mes_referencia"] = None
        recriado = RegistroFeedbackGerente.de_dict(dicionario)

        self.assertIsNone(recriado.mes_referencia)

    def test_e_imutavel(self):
        """Depois de criado, o registro não aceita alteração de atributo.

        frozen=True faz o Python levantar FrozenInstanceError ("instância
        congelada") quando tentamos mudar um valor.
        """
        registro = self._criar_valido()

        with self.assertRaises(FrozenInstanceError):
            registro.gerente_nome = "Outro Nome"

    def test_alterar_a_lista_original_nao_muda_o_registro(self):
        """O registro guarda uma CÓPIA das listas recebidas.

        frozen impede trocar o atributo, mas não impediria alterar a lista por
        dentro. A cópia feita no __post_init__ protege o registro: mexer na
        lista de fora não muda o que foi registrado.
        """
        roteiro = {
            "pontos_positivos": ["Time engajado"],
            "pontos_melhoria": ["Delegar o caixa"],
            "possiveis_motivos": ["Pico de movimento"],
            "roteiro_conversa": ["Como foi a semana?"],
        }

        registro = RegistroFeedbackGerente(
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            gerente_id="C0030",
            gerente_nome="Diego Furtado",
            gerado_em=datetime(2026, 11, 12, 14, 0, tzinfo=timezone.utc),
            roteiro=roteiro,
        )

        # Alteramos a lista ORIGINAL, depois de o registro já existir.
        roteiro["pontos_positivos"].append("Item acrescentado depois")

        self.assertEqual(
            registro.roteiro["pontos_positivos"], ["Time engajado"]
        )

    def test_de_dict_com_campo_faltando_levanta_erro(self):
        """Faltando qualquer campo obrigatório, a leitura falha com ValueError.

        Testamos os sete campos obrigatórios, um por vez. mes_referencia fica
        de fora porque None é um valor válido para ele.
        """
        dicionario = self._criar_valido().para_dict()

        for campo in (
            "feedback_id",
            "loja_id",
            "loja_nome",
            "gerente_id",
            "gerente_nome",
            "gerado_em",
            "roteiro",
        ):
            # subTest mostra qual campo faltou, sem parar os outros casos.
            with self.subTest(campo=campo):
                incompleto = dict(dicionario)
                del incompleto[campo]

                with self.assertRaises(ValueError):
                    RegistroFeedbackGerente.de_dict(incompleto)

    def test_de_dict_com_data_invalida_levanta_erro(self):
        """Texto que não é data (ou data sem fuso) levanta ValueError."""
        dicionario = self._criar_valido().para_dict()

        dicionario["gerado_em"] = "ontem de manhã"
        with self.assertRaises(ValueError):
            RegistroFeedbackGerente.de_dict(dicionario)

        # Data válida, mas sem fuso: não sabemos o horário real.
        dicionario["gerado_em"] = "2026-11-12T14:00:00"
        with self.assertRaises(ValueError):
            RegistroFeedbackGerente.de_dict(dicionario)

    def test_de_dict_com_tipo_errado_levanta_erro(self):
        """Campos com o tipo errado também são recusados com ValueError."""
        dicionario = self._criar_valido().para_dict()

        # gerente_id precisa ser texto, não número.
        dicionario["gerente_id"] = 30
        with self.assertRaises(ValueError):
            RegistroFeedbackGerente.de_dict(dicionario)

        # roteiro precisa ser dicionário, não lista.
        dicionario = self._criar_valido().para_dict()
        dicionario["roteiro"] = ["lista solta"]
        with self.assertRaises(ValueError):
            RegistroFeedbackGerente.de_dict(dicionario)


if __name__ == "__main__":
    unittest.main()
