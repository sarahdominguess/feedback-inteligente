"""Testes isolados do validador de qualidade do roteiro de feedback.

Os testes usam um roteiro sintético válido e trocam só a parte que cada regra
verifica. Não leem CSV e não chamam a IA. Comentamos o resultado esperado de
cada caso para deixar claro por que ele é o correto.
"""

import unittest

from domain.feedback_roteiro import FeedbackRoteiro
from services.validador_feedback import validar_roteiro


def criar_roteiro_valido() -> FeedbackRoteiro:
    """Cria um roteiro que passa em todas as regras.

    Tem 2 reconhecimentos, 2 pontos de melhoria, 2 hipóteses e 6 itens de
    conversa, sendo 3 com "?". Todos os textos têm mais de 10 caracteres.
    """
    return FeedbackRoteiro(
        pontos_positivos=[
            "Conversão de 50,5%, a melhor do time, mostra segurança.",
            "Cliente elogiou o atendimento no Google citando seu nome.",
        ],
        pontos_melhoria=[
            "Na situação do salão, o P.A. de 1,22 ficou abaixo da média; "
            "oferecer uma segunda peça amanhã.",
            "Na venda do vestido, repetir a oferta do cinto no caixa para "
            "elevar o P.A.",
        ],
        possiveis_motivos=[
            "Pode ser que o ritmo do salão deixe pouco tempo para oferecer "
            "complementos.",
            "Pode ser que falte segurança para sugerir uma segunda peça.",
        ],
        roteiro_conversa=[
            "Abertura: obrigado por reservar este momento; quero ouvir você.",
            "Reconhecimento: sua conversão de 50,5% é a melhor do time.",
            "Situação: o P.A. ficou em 1,22; como você vê isso?",
            "O que costuma acontecer quando você pensa em oferecer outra peça?",
            "Que apoio você precisaria para testar uma oferta amanhã?",
            "Combinado: amanhã você oferece uma segunda peça e nos falamos "
            "na sexta.",
        ],
    )


def roteiro_com(**campos) -> FeedbackRoteiro:
    """Copia o roteiro válido e troca apenas os campos informados.

    Exemplo: roteiro_com(pontos_positivos=[]) devolve o mesmo roteiro, mas
    sem nenhum ponto positivo, para testar essa regra isoladamente.
    """
    dados = criar_roteiro_valido().para_dict()
    dados.update(campos)
    return FeedbackRoteiro.de_dict(dados)


def problemas_em_texto(problemas: list[str]) -> str:
    """Junta os problemas em um texto só, para facilitar as verificações."""
    return " | ".join(problemas)


class TestRoteiroValido(unittest.TestCase):
    """Um roteiro dentro das regras não deve gerar nenhum problema."""

    def test_roteiro_valido_e_aprovado(self):
        """Lista vazia significa aprovado."""
        self.assertEqual(
            validar_roteiro(
                criar_roteiro_valido(), "Bianca Rocha", ["Sabrina Alves"]
            ),
            [],
        )

    def test_limites_exatos_de_tamanho(self):
        """Item com 10 e com 700 caracteres é aceito (limites inclusivos)."""
        roteiro = roteiro_com(
            pontos_positivos=["1234567890", "x" * 700]
        )

        self.assertEqual(
            validar_roteiro(roteiro, "Bianca Rocha", []), []
        )


class TestQuantidadeETamanho(unittest.TestCase):
    """Confere as quantidades mínimas/máximas e o tamanho dos itens."""

    def test_lista_vazia_e_reprovada(self):
        """Cada lista precisa de pelo menos 1 item (conversa: 4)."""
        problemas = validar_roteiro(
            roteiro_com(pontos_positivos=[]), "Bianca Rocha", []
        )

        texto = problemas_em_texto(problemas)
        self.assertIn("pontos_positivos", texto)
        self.assertIn("mínimo é 1", texto)

    def test_conversa_com_poucos_itens(self):
        """O roteiro da conversa precisa de pelo menos 4 itens."""
        problemas = validar_roteiro(
            roteiro_com(roteiro_conversa=["Abertura acolhedora para a conversa."]),
            "Bianca Rocha",
            [],
        )

        self.assertIn(
            "roteiro_conversa", problemas_em_texto(problemas)
        )

    def test_acima_do_maximo(self):
        """Pontos positivos aceitam no máximo 6 itens."""
        itens = criar_roteiro_valido().pontos_positivos + [
            "Reconhecimento extra com dado real número um.",
            "Reconhecimento extra com dado real número dois.",
            "Reconhecimento extra com dado real número três.",
            "Reconhecimento extra com dado real número quatro.",
            "Reconhecimento extra com dado real número cinco.",
        ]

        problemas = validar_roteiro(
            roteiro_com(pontos_positivos=itens), "Bianca Rocha", []
        )

        self.assertIn("máximo é 6", problemas_em_texto(problemas))

    def test_item_curto(self):
        """Item com menos de 10 caracteres é reprovado e mostra o trecho."""
        problemas = validar_roteiro(
            roteiro_com(
                pontos_positivos=["Curto", "Outro item suficientemente longo."]
            ),
            "Bianca Rocha",
            [],
        )

        texto = problemas_em_texto(problemas)
        self.assertIn("item curto", texto)
        self.assertIn("Curto", texto)

    def test_item_longo(self):
        """Item com mais de 700 caracteres é reprovado."""
        problemas = validar_roteiro(
            roteiro_com(pontos_positivos=["x" * 701, "Item normal e longo."]),
            "Bianca Rocha",
            [],
        )

        self.assertIn("item longo", problemas_em_texto(problemas))


class TestNomesDeColegas(unittest.TestCase):
    """Confere o bloqueio de nomes de colegas, com palavra inteira."""

    def test_nome_completo_do_colega(self):
        """Citar o nome completo de um colega é reprovado."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "A Sabrina Alves ajudou o time no sábado.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        problemas = validar_roteiro(
            roteiro, "Bianca Rocha", ["Sabrina Alves"]
        )

        self.assertIn("Sabrina Alves", problemas_em_texto(problemas))

    def test_primeiro_nome_do_colega(self):
        """Citar só o primeiro nome também é reprovado."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "A Sabrina comentou a meta com o time.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        problemas = validar_roteiro(
            roteiro, "Bianca Rocha", ["Sabrina Alves"]
        )

        self.assertIn("'Sabrina'", problemas_em_texto(problemas))

    def test_nome_da_propria_vendedora_e_permitido(self):
        """O nome da vendedora pode aparecer no roteiro dela."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "A Bianca Rocha é referência de conversão no time.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        self.assertEqual(
            validar_roteiro(roteiro, "Bianca Rocha", ["Sabrina Alves"]), []
        )

    def test_primeiro_nome_ambiguo_e_ignorado(self):
        """Se o primeiro nome é igual ao da vendedora, não dá para acusar."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "A Ana comentou a meta com o time.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        self.assertEqual(
            validar_roteiro(roteiro, "Ana Souza", ["Ana Silva"]), []
        )

    def test_nome_completo_ambiguo_continua_bloqueado(self):
        """Mesmo com primeiro nome igual, o nome completo do colega é barrado."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "A Ana Silva comentou a meta com o time.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        problemas = validar_roteiro(roteiro, "Ana Souza", ["Ana Silva"])

        self.assertIn("Ana Silva", problemas_em_texto(problemas))

    def test_palavra_inteira(self):
        """O nome "Ana" não deve disparar dentro da palavra "plano"."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "O plano de ação para amanhã ficou claro.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        self.assertEqual(
            validar_roteiro(roteiro, "Bianca Rocha", ["Ana"]), []
        )

    def test_nome_com_acento_e_maiuscula(self):
        """A busca ignora acento e caixa: "PATRICIA" encontra "Patrícia"."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "A PATRICIA comentou a meta com o time.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        problemas = validar_roteiro(
            roteiro, "Bianca Rocha", ["Patrícia Lemos"]
        )

        self.assertIn("Patrícia", problemas_em_texto(problemas))


class TestPerguntasAbertas(unittest.TestCase):
    """Confere a exigência de pelo menos três perguntas no roteiro."""

    def test_poucas_perguntas(self):
        """Com menos de 3 itens com "?", o roteiro é reprovado."""
        roteiro = roteiro_com(
            roteiro_conversa=[
                "Abertura: obrigado por reservar este momento.",
                "Reconhecimento: sua conversão é a melhor do time.",
                "Situação: o P.A. ficou em 1,22; como você vê isso?",
                "Que apoio você precisaria para testar uma oferta amanhã?",
            ]
        )

        problemas = validar_roteiro(roteiro, "Bianca Rocha", [])

        self.assertIn("pelo menos 3", problemas_em_texto(problemas))

    def test_tres_perguntas_aprovam(self):
        """Três itens com "?" já atendem à regra."""
        problemas = validar_roteiro(
            criar_roteiro_valido(), "Bianca Rocha", []
        )

        self.assertEqual(problemas, [])


class TestFrasesGenericas(unittest.TestCase):
    """Confere o bloqueio dos clichês de texto de robô."""

    def test_prezado_colaborador(self):
        """O clichê "Prezado colaborador" é reprovado."""
        roteiro = roteiro_com(
            pontos_positivos=[
                "Prezado colaborador, vamos conversar sobre suas metas.",
                "Cliente elogiou o atendimento citando seu nome.",
            ]
        )

        problemas = validar_roteiro(roteiro, "Bianca Rocha", [])

        self.assertIn(
            "prezado colaborador", problemas_em_texto(problemas)
        )

    def test_multiplas_dimensoes_com_acento(self):
        """A comparação ignora acento: "múltiplas dimensões" é detectado."""
        roteiro = roteiro_com(
            possiveis_motivos=[
                "Buscamos múltiplas dimensões de melhoria no atendimento.",
                "Pode ser que falte segurança para sugerir uma peça.",
            ]
        )

        problemas = validar_roteiro(roteiro, "Bianca Rocha", [])

        self.assertIn(
            "multiplas dimensoes", problemas_em_texto(problemas)
        )

    def test_buscar_a_excelencia_em_maiusculas(self):
        """A comparação ignora caixa: "BUSCAR A EXCELÊNCIA" é detectado."""
        roteiro = roteiro_com(
            pontos_melhoria=[
                "É preciso BUSCAR A EXCELÊNCIA em cada atendimento.",
                "Na venda do vestido, repetir a oferta do cinto no caixa.",
            ]
        )

        problemas = validar_roteiro(roteiro, "Bianca Rocha", [])

        self.assertIn(
            "buscar a excelencia", problemas_em_texto(problemas)
        )


if __name__ == "__main__":
    unittest.main()
