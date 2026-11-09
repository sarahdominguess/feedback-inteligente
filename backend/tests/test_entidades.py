"""Testes das entidades básicas do domínio.

Cobrem criação válida, recusa de valores inválidos, imutabilidade e conversão
de/para dicionário. Se algo quebrar aqui, o problema aparece cedo, antes de
chegar às regras de negócio que usam essas entidades.
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from domain.anotacao import Anotacao
from domain.feedback_roteiro import FeedbackRoteiro
from domain.indicador_diario import IndicadorDiario


class TestIndicadorDiario(unittest.TestCase):
    """Testes da entidade que representa um dia de vendas de um vendedor."""

    def _criar_valido(self) -> IndicadorDiario:
        """Cria um IndicadorDiario válido para reaproveitar nos testes.

        O "_" no começo do nome indica que é um método auxiliar interno,
        usado apenas dentro desta classe de testes.
        """
        return IndicadorDiario(
            data=date(2026, 8, 1),
            vendedor_id="C0031",
            valor_vendido=2767.52,
            vendas=13,
            pecas=18,
            atendimentos=19,
        )

    def test_cria_indicador_valido(self):
        """Com números válidos, o objeto guarda exatamente o que recebeu."""
        indicador = self._criar_valido()

        self.assertEqual(indicador.data, date(2026, 8, 1))
        self.assertEqual(indicador.vendedor_id, "C0031")
        self.assertEqual(indicador.valor_vendido, 2767.52)
        self.assertEqual(indicador.vendas, 13)
        self.assertEqual(indicador.pecas, 18)
        self.assertEqual(indicador.atendimentos, 19)

    def test_recusa_valores_negativos(self):
        """Qualquer um dos quatro números negativos deve levantar ValueError.

        O teste troca um campo por vez por -1: valor vendido, vendas, peças e
        atendimentos. Em todos os casos a criação deve falhar.
        """
        dados = {
            "data": date(2026, 8, 1),
            "vendedor_id": "C0031",
            "valor_vendido": 100.0,
            "vendas": 2,
            "pecas": 3,
            "atendimentos": 4,
        }

        for campo in ("valor_vendido", "vendas", "pecas", "atendimentos"):
            # subTest mostra qual campo falhou, sem parar os outros casos.
            with self.subTest(campo=campo):
                dados_invalidos = {**dados, campo: -1}
                with self.assertRaises(ValueError):
                    IndicadorDiario(**dados_invalidos)

    def test_e_imutavel(self):
        """Depois de criado, o objeto não aceita alteração de atributo.

        frozen=True faz o Python levantar FrozenInstanceError (um erro de
        "instância congelada") quando tentamos mudar um valor.
        """
        indicador = self._criar_valido()

        with self.assertRaises(FrozenInstanceError):
            indicador.vendas = 99


class TestAnotacao(unittest.TestCase):
    """Testes da entidade que representa uma anotação do gerente."""

    def test_e_do_time_quando_sobre_e_time(self):
        """A anotação com sobre="(time)" é identificada como do time."""
        anotacao = Anotacao(
            data=date(2026, 10, 31),
            sobre="(time)",
            texto="Batemos a meta de outubro!",
        )

        self.assertTrue(anotacao.e_do_time)

    def test_nao_e_do_time_quando_sobre_e_uma_pessoa(self):
        """A anotação com o nome de uma pessoa não é do time."""
        anotacao = Anotacao(
            data=date(2026, 8, 6),
            sobre="Bianca Rocha",
            texto="Levou só uma peça por cliente.",
        )

        self.assertFalse(anotacao.e_do_time)


class TestFeedbackRoteiro(unittest.TestCase):
    """Testes da estrutura de quatro listas que formará o roteiro."""

    def test_ida_e_volta_para_dict_e_de_dict(self):
        """Converter para dicionário e de volta deve devolver o mesmo roteiro."""
        roteiro = FeedbackRoteiro(
            pontos_positivos=["Ótima relação com as clientes"],
            pontos_melhoria=["Vender mais de uma peça por atendimento"],
            possiveis_motivos=["Muitas clientes ao mesmo tempo no sábado"],
            roteiro_conversa=["Como você se sentiu no último sábado?"],
        )

        dicionario = roteiro.para_dict()

        # O dicionário deve trazer exatamente as quatro listas.
        self.assertEqual(dicionario["pontos_positivos"], roteiro.pontos_positivos)
        self.assertEqual(dicionario["pontos_melhoria"], roteiro.pontos_melhoria)
        self.assertEqual(dicionario["possiveis_motivos"], roteiro.possiveis_motivos)
        self.assertEqual(dicionario["roteiro_conversa"], roteiro.roteiro_conversa)

        # Ao recriar a partir do dicionário, o conteúdo deve ser igual.
        recriado = FeedbackRoteiro.de_dict(dicionario)
        self.assertEqual(recriado, roteiro)

    def test_para_dict_devolve_copias_das_listas(self):
        """Alterar o dicionário devolvido não pode alterar o roteiro original."""
        roteiro = FeedbackRoteiro(pontos_positivos=["Bom atendimento"])
        dicionario = roteiro.para_dict()

        # Mexemos na lista do dicionário de propósito; o roteiro deve continuar
        # com apenas o item original.
        dicionario["pontos_positivos"].append("Item adicionado só no dicionário")

        self.assertEqual(roteiro.pontos_positivos, ["Bom atendimento"])

    def test_chaves_ausentes_viram_listas_vazias(self):
        """Só uma chave enviada: as outras três partes ficam vazias."""
        roteiro = FeedbackRoteiro.de_dict(
            {"pontos_positivos": ["Bom atendimento"]}
        )

        self.assertEqual(roteiro.pontos_positivos, ["Bom atendimento"])
        self.assertEqual(roteiro.pontos_melhoria, [])
        self.assertEqual(roteiro.possiveis_motivos, [])
        self.assertEqual(roteiro.roteiro_conversa, [])

    def test_ignora_chaves_extras(self):
        """Chaves que não fazem parte do roteiro são descartadas sem erro."""
        roteiro = FeedbackRoteiro.de_dict(
            {
                "pontos_positivos": ["Bom atendimento"],
                "chave_desconhecida": "deve ser ignorada",
            }
        )

        self.assertEqual(roteiro.pontos_positivos, ["Bom atendimento"])
        self.assertEqual(roteiro.pontos_melhoria, [])

    def test_valor_invalido_levanta_erro(self):
        """Cada parte precisa ser uma lista de textos; senão, ValueError.

        Testamos três casos inválidos: um texto solto (em vez de lista), uma
        lista com números e uma lista com None (o "sem valor" do Python).
        """
        casos_invalidos = ("não é lista", [1, 2], [None])

        for valor in casos_invalidos:
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    FeedbackRoteiro.de_dict({"pontos_melhoria": valor})
