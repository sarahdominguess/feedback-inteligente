"""Testes da normalização de nomes e da entidade Gerente.

Usam anotações sintéticas (criadas aqui mesmo, sem ler CSV) para conferir a
busca por nome, a separação das anotações do time e a proteção das coleções.
"""

import unittest
from datetime import date

from domain.anotacao import Anotacao
from domain.gerente import Gerente
from domain.texto import normalizar_nome


class TestNormalizarNome(unittest.TestCase):
    """Testes da função que deixa nomes prontos para comparação."""

    def test_remove_acentos_caixa_e_espacos(self):
        """Acento, maiúsculas e espaços extras não devem importar."""
        self.assertEqual(
            normalizar_nome("  Patrícia   Lemos "), "patricia lemos"
        )
        self.assertEqual(normalizar_nome("JOÃO  da Silva"), "joao da silva")
        self.assertEqual(normalizar_nome("BIANCA"), "bianca")

    def test_texto_so_com_espacos_vira_string_vazia(self):
        """Um texto sem nenhuma palavra vira "", e não um erro."""
        self.assertEqual(normalizar_nome("   "), "")


class TestGerente(unittest.TestCase):
    """Testes da identidade, da busca por nome e das anotações do time."""

    def setUp(self):
        """Monta um gerente com anotações fora de ordem de propósito.

        Pessoas nas anotações:
        - Bianca Rocha: 2 anotações (agosto).
        - Lucas Moreira: 2 anotações (agosto e setembro).
        - Ana Silva e Ana Souza: 1 cada, para testar o primeiro nome ambíguo.
        - "(time)": 1 anotação sobre o time inteiro.
        """
        self.lista_original = [
            Anotacao(
                date(2026, 8, 24),
                "(time)",
                "sábado corrido, faltou gente no salão",
            ),
            Anotacao(
                date(2026, 8, 6),
                "Bianca Rocha",
                "atendeu três clientes ao mesmo tempo",
            ),
            Anotacao(date(2026, 9, 20), "Ana Silva", "boa argumentação"),
            Anotacao(
                date(2026, 8, 13),
                "Lucas Moreira",
                "chegou 20 minutos atrasado",
            ),
            Anotacao(
                date(2026, 8, 20),
                "Bianca Rocha",
                "levou só uma peça por cliente",
            ),
            Anotacao(
                date(2026, 9, 21),
                "Ana Souza",
                "precisa treinar objeções",
            ),
            Anotacao(
                date(2026, 9, 15),
                "Lucas Moreira",
                "melhorou o atendimento",
            ),
        ]

        self.gerente = Gerente(
            gerente_id="C0030",
            nome="Diego Furtado",
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            anotacoes=self.lista_original,
        )

    def test_identidade_somente_leitura(self):
        """Os dados de identidade são lidos por propriedades."""
        self.assertEqual(self.gerente.gerente_id, "C0030")
        self.assertEqual(self.gerente.nome, "Diego Furtado")
        self.assertEqual(self.gerente.loja_id, "L004")
        self.assertEqual(self.gerente.loja_nome, "Aurora Shopping Centro")

    def test_todas_as_anotacoes_em_ordem_cronologica(self):
        """anotacoes() devolve uma tupla com as 7 anotações em ordem de data."""
        anotacoes = self.gerente.anotacoes()

        self.assertIsInstance(anotacoes, tuple)
        self.assertEqual(len(anotacoes), 7)
        self.assertEqual(
            [anotacao.data for anotacao in anotacoes],
            [
                date(2026, 8, 6),
                date(2026, 8, 13),
                date(2026, 8, 20),
                date(2026, 8, 24),
                date(2026, 9, 15),
                date(2026, 9, 20),
                date(2026, 9, 21),
            ],
        )

    def test_busca_por_nome_completo(self):
        """O nome completo encontra só as anotações daquela pessoa."""
        anotacoes = self.gerente.anotacoes_sobre("Bianca Rocha")

        self.assertEqual(len(anotacoes), 2)
        self.assertEqual(
            [anotacao.texto for anotacao in anotacoes],
            [
                "atendeu três clientes ao mesmo tempo",
                "levou só uma peça por cliente",
            ],
        )

    def test_busca_por_primeiro_nome(self):
        """Só o primeiro nome também encontra, ignorando caixa e espaços."""
        anotacoes = self.gerente.anotacoes_sobre("  BIANCA ")

        self.assertEqual(len(anotacoes), 2)
        self.assertTrue(
            all(anotacao.sobre == "Bianca Rocha" for anotacao in anotacoes)
        )

    def test_busca_por_nome_inexistente_devolve_vazio(self):
        """Um nome que não aparece nas anotações devolve tupla vazia."""
        self.assertEqual(self.gerente.anotacoes_sobre("Renata Campos"), ())

    def test_primeiro_nome_ambiguo_devolve_vazio(self):
        """"Ana" casa com duas pessoas diferentes; sem nome completo, vazio.

        As anotações falam de "Ana Silva" e "Ana Souza". A busca por "Ana"
        é ambígua, e não existe pessoa chamada exatamente "Ana".
        """
        self.assertEqual(self.gerente.anotacoes_sobre("Ana"), ())

        # Com o nome completo, a busca deixa de ser ambígua.
        anotacoes = self.gerente.anotacoes_sobre("Ana Silva")
        self.assertEqual(len(anotacoes), 1)
        self.assertEqual(anotacoes[0].texto, "boa argumentação")

    def test_anotacoes_do_time_ficam_separadas(self):
        """As anotações "(time)" aparecem só em anotacoes_do_time()."""
        do_time = self.gerente.anotacoes_do_time()

        self.assertEqual(len(do_time), 1)
        self.assertEqual(
            do_time[0].texto, "sábado corrido, faltou gente no salão"
        )

        # Buscar por "(time)" como se fosse uma pessoa não devolve nada.
        self.assertEqual(self.gerente.anotacoes_sobre("(time)"), ())
        self.assertEqual(self.gerente.anotacoes_sobre("time"), ())

        # O total continua contando as anotações do time.
        self.assertEqual(self.gerente.total_anotacoes(), 7)

    def test_lista_original_nao_altera_o_gerente(self):
        """Mexer na lista usada no construtor não muda o objeto."""
        self.lista_original.append(
            Anotacao(date(2026, 10, 1), "Bianca Rocha", "anotação nova")
        )

        self.assertEqual(len(self.gerente.anotacoes()), 7)
        self.assertEqual(len(self.gerente.anotacoes_sobre("Bianca")), 2)

    def test_colecoes_publicas_nao_sao_alteraveis(self):
        """A API pública não permite trocar itens nem mudar a identidade.

        - anotacoes() é uma tupla: trocar um item levanta TypeError.
        - nome é uma propriedade sem "setter": atribuir levanta AttributeError.
        """
        self.assertIsInstance(self.gerente.anotacoes(), tuple)

        with self.assertRaises(TypeError):
            self.gerente.anotacoes()[0] = Anotacao(
                date(2026, 10, 2), "Bianca Rocha", "tentativa de troca"
            )

        with self.assertRaises(AttributeError):
            self.gerente.nome = "Outro Nome"
