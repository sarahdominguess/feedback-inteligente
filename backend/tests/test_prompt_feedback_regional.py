"""Testes do prompt de feedback da regional para o gerente da loja.

Os dados são sintéticos (inventados no próprio teste), sem ler CSV e sem
chamar a internet. O dicionário tem o mesmo formato do devolvido por
ConsolidadoRegional.obter_desempenho_gerente().
"""

import unittest
from datetime import date

from services.prompt_feedback_regional import (
    SISTEMA_PROMPT_REGIONAL,
    montar_mensagens_regional,
)


def criar_desempenho_sintetico() -> dict:
    """Monta um consolidado fictício com dois meses e cinco anotações.

    Outubro tem meta e mês completo; novembro tem um único dia e NÃO tem meta
    (para testar o "sem dado"). As anotações vêm fora de ordem de propósito,
    para provar que o prompt as ordena.
    """
    vendedores = [
        {
            "vendedor_id": "C0031",
            "nome": "Bianca Rocha",
            "anotacoes_do_gerente": 3,
            "ultima_anotacao_em": date(2026, 10, 1),
            "roteiros_preparados": 2,
            "ultimo_roteiro_em": None,
            "situacao": "com_roteiro",
        },
        {
            "vendedor_id": "C0032",
            "nome": "Ana Silva",
            "anotacoes_do_gerente": 0,
            "ultima_anotacao_em": None,
            "roteiros_preparados": 1,
            "ultimo_roteiro_em": None,
            "situacao": "com_roteiro",
        },
    ]

    # Seis vendedores sem roteiro, para fechar os 8 do total.
    for indice in range(6):
        vendedores.append(
            {
                "vendedor_id": f"C004{indice}",
                "nome": f"Vendedor {indice}",
                "anotacoes_do_gerente": 0,
                "ultima_anotacao_em": None,
                "roteiros_preparados": 0,
                "ultimo_roteiro_em": None,
                "situacao": "sem_roteiro",
            }
        )

    return {
        "gerente_id": "C0030",
        "gerente_nome": "Diego Furtado",
        "loja_id": "L004",
        "loja_nome": "Aurora Shopping Centro",
        "periodo_inicio": date(2026, 10, 1),
        "periodo_fim": date(2026, 11, 1),
        "resultado_loja": [
            {
                "mes": "2026-10",
                "mes_parcial": False,
                "dias_com_dados": 27,
                "meta_loja": 317200.0,
                "vendas_loja": 320000.0,
                "atingimento_loja": 1.0,
                "vendas_vendedores": 309084.37,
                "atingimento_vendedores": 0.9,
                "vendas_gerente": 10915.63,
                "participacao_gerente": 0.033,
            },
            {
                "mes": "2026-11",
                "mes_parcial": True,
                "dias_com_dados": 1,
                "meta_loja": None,
                "vendas_loja": 50000.0,
                "atingimento_loja": None,
                "vendas_vendedores": 45000.0,
                "atingimento_vendedores": None,
                "vendas_gerente": 5000.0,
                "participacao_gerente": 0.1,
            },
        ],
        "acompanhamento_feedback": {
            "total_vendedores": 8,
            "vendedores_com_roteiro": 2,
            "cobertura": 0.25,
            "total_roteiros_preparados": 3,
            "vendedores": vendedores,
        },
        "anotacoes_regional": [
            {
                "data": date(2026, 9, 15),
                "autora": "Patrícia Lemos",
                "texto": "A reunião matinal não aconteceu nas duas visitas.",
            },
            {
                "data": date(2026, 8, 18),
                "autora": "Patrícia Lemos",
                "texto": "Loja organizada, vitrine no padrão.",
            },
        ],
    }


class TestMensagensRegionais(unittest.TestCase):
    """Testa a estrutura e o conteúdo das duas mensagens."""

    def test_duas_mensagens_com_papeis_corretos(self):
        """A saída tem exatamente sistema + usuário, nesta ordem."""
        mensagens = montar_mensagens_regional(criar_desempenho_sintetico())

        self.assertEqual(len(mensagens), 2)
        self.assertEqual(mensagens[0]["role"], "system")
        self.assertEqual(mensagens[1]["role"], "user")
        self.assertEqual(mensagens[0]["content"], SISTEMA_PROMPT_REGIONAL)
        self.assertTrue(mensagens[1]["content"].strip())

    def test_sistema_pede_json_sbi_e_as_quatro_chaves(self):
        """O sistema exige JSON, SBI e exatamente as quatro listas."""
        sistema = montar_mensagens_regional(criar_desempenho_sintetico())[0][
            "content"
        ]

        self.assertIn("JSON", sistema)
        self.assertIn("SBI", sistema)
        self.assertIn("3 perguntas abertas", sistema)
        for chave in (
            "pontos_positivos",
            "pontos_melhoria",
            "possiveis_motivos",
            "roteiro_conversa",
        ):
            with self.subTest(chave=chave):
                self.assertIn(f'"{chave}"', sistema)

    def test_sistema_explica_a_meta_da_loja_e_as_vendas_do_gerente(self):
        """O sistema avisa que a meta não inclui o gerente e que ele vende."""
        sistema = montar_mensagens_regional(criar_desempenho_sintetico())[0][
            "content"
        ]

        self.assertIn("NÃO inclui o gerente", sistema)
        self.assertIn("atende no caixa", sistema)
        self.assertIn("Não compare esta loja com outras lojas", sistema)

    def test_usuario_tem_loja_gerente_e_numeros_formatados(self):
        """A mensagem do usuário traz identidade e números em pt-BR."""
        usuario = montar_mensagens_regional(criar_desempenho_sintetico())[1][
            "content"
        ]

        self.assertIn("Aurora Shopping Centro", usuario)
        self.assertIn("L004", usuario)
        self.assertIn("Diego Furtado", usuario)
        self.assertIn("C0030", usuario)
        self.assertIn("R$ 317.200,00", usuario)  # meta de outubro
        self.assertIn("R$ 320.000,00", usuario)  # vendas da loja
        self.assertIn("R$ 10.915,63", usuario)  # vendas do gerente
        self.assertIn("100,0%", usuario)  # atingimento da loja
        self.assertIn("3,3%", usuario)  # participação do gerente

    def test_usuario_tem_acompanhamento_e_a_frase_sobre_preparado(self):
        """Cobertura, total e o lembrete de que preparado não é realizado."""
        usuario = montar_mensagens_regional(criar_desempenho_sintetico())[1][
            "content"
        ]

        self.assertIn("25,0%", usuario)  # cobertura 2 de 8
        self.assertIn("Vendedores ainda sem roteiro preparado: 6", usuario)
        self.assertIn(
            "não confirma que a conversa de feedback aconteceu", usuario
        )
        self.assertNotIn("realizado", usuario)

    def test_usuario_tem_as_anotacoes_em_ordem_cronologica(self):
        """As anotações aparecem da mais antiga para a mais recente, com autora."""
        usuario = montar_mensagens_regional(criar_desempenho_sintetico())[1][
            "content"
        ]

        antiga = usuario.index("Loja organizada, vitrine no padrão.")
        recente = usuario.index("A reunião matinal não aconteceu")
        self.assertLess(antiga, recente)
        self.assertIn("(Patrícia Lemos)", usuario)
        self.assertIn("18/08/2026", usuario)
        self.assertIn("15/09/2026", usuario)

    def test_mes_escolhido_filtra_o_resultado(self):
        """Com um mês, só ele entra no resultado; o outro fica de fora."""
        usuario = montar_mensagens_regional(
            criar_desempenho_sintetico(), "2026-10"
        )[1]["content"]

        self.assertIn("outubro/2026", usuario)
        self.assertIn("R$ 317.200,00", usuario)
        self.assertNotIn("novembro/2026", usuario)
        self.assertNotIn("R$ 50.000,00", usuario)

    def test_valores_none_viram_sem_dado(self):
        """Mês sem meta mostra "sem dado" em vez de "None" ou "nan"."""
        usuario = montar_mensagens_regional(criar_desempenho_sintetico())[1][
            "content"
        ]

        self.assertIn("meta da loja sem dados", usuario)
        self.assertIn("atingimento da loja sem dados", usuario)
        self.assertNotIn("None", usuario)
        self.assertNotIn("nan", usuario)

    def test_mes_parcial_aparece(self):
        """Novembro tem um dia e é sinalizado como parcial."""
        usuario = montar_mensagens_regional(criar_desempenho_sintetico())[1][
            "content"
        ]

        self.assertIn("mês parcial (apenas 1 dia com dados)", usuario)

    def test_nao_cita_vendedores_pelo_nome(self):
        """Nomes de vendedores não entram no prompt (evita exposição)."""
        usuario = montar_mensagens_regional(criar_desempenho_sintetico())[1][
            "content"
        ]

        self.assertNotIn("Bianca Rocha", usuario)
        self.assertNotIn("Ana Silva", usuario)

    def test_mes_inexistente_levanta_erro(self):
        """Mês fora dos dados falha com ValueError citando os disponíveis."""
        with self.assertRaises(ValueError) as contexto:
            montar_mensagens_regional(criar_desempenho_sintetico(), "2025-01")

        mensagem = str(contexto.exception)
        self.assertIn("2025-01", mensagem)
        self.assertIn("2026-10", mensagem)


if __name__ == "__main__":
    unittest.main()
