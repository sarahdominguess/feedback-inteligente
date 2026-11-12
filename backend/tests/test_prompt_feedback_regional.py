"""Testes do construtor de prompt do feedback da regional ao gerente.

O consolidado usado aqui é um "retrato" fixo dos CSVs reais (mesmos valores de
agosto a novembro de 2026 e as mesmas 5 anotações da regional). Fixar os dados
deixa os testes independentes: nada é lido de arquivo e nenhum valor muda se
alguém gerar um roteiro novo pela interface.

Também confirmamos que `validar_roteiro` serve para o roteiro do GERENTE,
passando o nome dele como `vendedor_nome` e `nomes_colegas=()`.
"""

import unittest
from datetime import date

from domain.feedback_roteiro import FeedbackRoteiro
from services.prompt_feedback_regional import (
    SISTEMA_PROMPT_REGIONAL,
    montar_prompt_feedback_regional,
)
from services.validador_feedback import validar_roteiro


def _consolidado() -> dict:
    """Devolve um retrato fixo do consolidado real da loja L004.

    Os números são os mesmos calculados pelo ConsolidadoRegional com os CSVs do
    projeto; as anotações são as 5 visitas da regional. A data das anotações é
    objeto date, como o consolidado devolve.
    """
    return {
        "gerente_id": "C0030",
        "gerente_nome": "Diego Furtado",
        "loja_id": "L004",
        "loja_nome": "Aurora Shopping Centro",
        "periodo_inicio": date(2026, 8, 1),
        "periodo_fim": date(2026, 11, 12),
        "resultado_loja": [
            {
                "mes": "2026-08",
                "mes_parcial": False,
                "dias_com_dados": 27,
                "meta_loja": 297800.0,
                "vendas_loja": 271003.58,
                "atingimento_loja": 0.910018737407656,
                "vendas_vendedores": 264711.33,
                "atingimento_vendedores": 0.8888896239086634,
                "vendas_gerente": 6292.25,
                "participacao_gerente": 0.023218327964523576,
            },
            {
                "mes": "2026-09",
                "mes_parcial": False,
                "dias_com_dados": 26,
                "meta_loja": 282500.0,
                "vendas_loja": 276828.0,
                "atingimento_loja": 0.9799221238938053,
                "vendas_vendedores": 267594.52,
                "atingimento_vendedores": 0.9472372389380531,
                "vendas_gerente": 9233.48,
                "participacao_gerente": 0.033354573959281576,
            },
            {
                "mes": "2026-10",
                "mes_parcial": False,
                "dias_com_dados": 27,
                "meta_loja": 317200.0,
                "vendas_loja": 326697.48,
                "atingimento_loja": 1.0299416141235815,
                "vendas_vendedores": 315781.85,
                "atingimento_vendedores": 0.9955291614123583,
                "vendas_gerente": 10915.63,
                "participacao_gerente": 0.03341204223552627,
            },
            {
                "mes": "2026-11",
                "mes_parcial": True,
                "dias_com_dados": 1,
                "meta_loja": 346000.0,
                "vendas_loja": 8753.24,
                "atingimento_loja": 0.025298381502890172,
                "vendas_vendedores": 8753.24,
                "atingimento_vendedores": 0.025298381502890172,
                "vendas_gerente": 0.0,
                "participacao_gerente": 0.0,
            },
        ],
        "acompanhamento_feedback": {
            "total_vendedores": 8,
            "vendedores_com_roteiro": 2,
            "cobertura": 0.25,
            "total_roteiros_preparados": 4,
            "vendedores": [],
        },
        "anotacoes_regional": [
            {
                "data": date(2026, 8, 18),
                "autora": "Patrícia Lemos",
                "texto": (
                    "Loja organizada, vitrine no padrão. O Diego ainda faz "
                    "muita coisa sozinho e fica no caixa no horário de pico."
                ),
            },
            {
                "data": date(2026, 9, 15),
                "autora": "Patrícia Lemos",
                "texto": (
                    "A reunião matinal não aconteceu nas duas últimas "
                    "visitas. O time não sabia a meta do dia."
                ),
            },
            {
                "data": date(2026, 9, 29),
                "autora": "Patrícia Lemos",
                "texto": (
                    "O Diego pediu ajuda com a escala de sábado. "
                    "Combinamos de rever juntos."
                ),
            },
            {
                "data": date(2026, 10, 20),
                "autora": "Patrícia Lemos",
                "texto": (
                    "Clima do time bom, mas há atrito entre Renata e Marcelo "
                    "por causa da lista da vez. O Diego disse que vai "
                    "conversar."
                ),
            },
            {
                "data": date(2026, 10, 27),
                "autora": "Patrícia Lemos",
                "texto": (
                    "Outubro deve fechar acima da meta. A escala de sábado "
                    "continua com buraco no fim da tarde."
                ),
            },
        ],
    }


class TestPromptFeedbackRegional(unittest.TestCase):
    """Testes do texto enviado à IA no feedback da regional para o gerente."""

    def test_historico_completo_inclui_tudo(self):
        """Sem mês escolhido, o prompt traz todos os meses, o time e as visitas."""
        sistema, usuario = montar_prompt_feedback_regional(_consolidado())

        # A mensagem de sistema é a constante do módulo, sem cópia.
        self.assertIs(sistema, SISTEMA_PROMPT_REGIONAL)

        # Identidade e período.
        self.assertIn("Diego Furtado", usuario)
        self.assertIn("Aurora Shopping Centro (L004)", usuario)
        self.assertIn("Período analisado: todo o histórico", usuario)

        # Todos os meses aparecem, em ordem cronológica.
        for mes in (
            "agosto/2026",
            "setembro/2026",
            "outubro/2026",
            "novembro/2026",
        ):
            self.assertIn(mes, usuario)

        # Números de outubro formatados em reais e percentual.
        for trecho in (
            "meta da loja R$ 317.200,00",
            "vendas da loja R$ 326.697,48",
            "atingimento da loja 103,0%",
            "vendas dos vendedores R$ 315.781,85",
            "atingimento dos vendedores 99,6%",
            "vendas do gerente no caixa R$ 10.915,63",
            "participação do gerente 3,3%",
        ):
            self.assertIn(trecho, usuario)

        # Liderança e cobertura de feedbacks do time.
        self.assertIn("Vendedores na loja: 8", usuario)
        self.assertIn(
            "Vendedores com pelo menos um roteiro preparado: 2", usuario
        )
        self.assertIn("Cobertura de feedbacks preparados no time: 25,0%", usuario)
        self.assertIn("Total de roteiros preparados para o time: 4", usuario)
        self.assertIn("não significa que a conversa", usuario)

        # Todas as anotações da regional, com a data formatada.
        for trecho in (
            "18/08/2026: Loja organizada",
            "15/09/2026: A reunião matinal",
            "29/09/2026: O Diego pediu ajuda",
            "20/10/2026: Clima do time bom",
            "27/10/2026: Outubro deve fechar acima da meta",
        ):
            self.assertIn(trecho, usuario)

        # A mensagem de sistema fixa método, limite e formato JSON.
        self.assertIn("MÉTODO SBI", sistema)
        self.assertIn("outros gerentes", sistema)
        self.assertIn('"pontos_positivos"', sistema)
        self.assertIn('"roteiro_conversa"', sistema)

    def test_mes_de_outubro_fica_em_destaque_e_os_outros_como_contexto(self):
        """Com mês escolhido, outubro vem primeiro e os demais servem de contexto."""
        _, usuario = montar_prompt_feedback_regional(
            _consolidado(), "2026-10"
        )

        self.assertIn("Período analisado: outubro/2026", usuario)
        self.assertIn(
            "RESULTADO DA LOJA NO MÊS DE REFERÊNCIA (outubro/2026)", usuario
        )
        self.assertIn("atingimento da loja 103,0%", usuario)

        # O mês escolhido aparece ANTES do bloco de contexto.
        self.assertLess(
            usuario.index("NO MÊS DE REFERÊNCIA"),
            usuario.index("CONTEXTO DOS DEMAIS MESES"),
        )

        # O bloco de contexto lista os outros três meses.
        inicio_contexto = usuario.index("CONTEXTO DOS DEMAIS MESES")
        contexto = usuario[inicio_contexto:]
        for mes in ("agosto/2026", "setembro/2026", "novembro/2026"):
            self.assertIn(mes, contexto)

    def test_mes_parcial_de_novembro_avisa(self):
        """Novembro tem 1 dia com dados: o prompt precisa avisar do mês parcial."""
        _, usuario = montar_prompt_feedback_regional(
            _consolidado(), "2026-11"
        )

        self.assertIn("Período analisado: novembro/2026", usuario)
        self.assertIn(
            "novembro/2026: meta da loja R$ 346.000,00", usuario
        )
        self.assertIn("mês parcial (apenas 1 dia com dados)", usuario)

    def test_mes_inexistente_levanta_value_error(self):
        """Mês fora do resultado_loja falha com mensagem clara em português."""
        with self.assertRaises(ValueError) as contexto:
            montar_prompt_feedback_regional(_consolidado(), "2025-01")

        mensagem = str(contexto.exception)
        self.assertIn("2025-01", mensagem)
        # A mensagem lista os meses que existem, para orientar quem chamou.
        self.assertIn("2026-08", mensagem)

    def test_validador_aprova_roteiro_do_gerente(self):
        """O validador do vendedor serve para o gerente, com nomes_colegas=().

        O nome do próprio avaliado é permitido; a lista vazia de colegas
        desliga só a checagem de nomes de terceiros.
        """
        roteiro = FeedbackRoteiro(
            pontos_positivos=[
                "A loja bateu 103,0% da meta em outubro, com o gerente no "
                "caixa no horário de pico.",
                "O time tem 25,0% de cobertura de roteiros preparados.",
            ],
            pontos_melhoria=[
                "Na visita de 15/09/2026, a reunião matinal não aconteceu e o "
                "time ficou sem a meta do dia; combine uma rotina de 5 "
                "minutos para amanhã.",
                "Na visita de 27/10/2026, a escala de sábado seguia com "
                "buraco no fim da tarde; monte a escala da próxima semana "
                "já amanhã.",
            ],
            possiveis_motivos=[
                "Pode ser que a correria do caixa esteja consumindo o tempo "
                "de gestão.",
                "Pode ser que a rotina matinal ainda não esteja combinada "
                "com clareza.",
            ],
            roteiro_conversa=[
                "Abrir agradecendo a dedicação do Diego Furtado e o "
                "resultado de outubro.",
                "Como você vê o resultado de 103,0% da meta em outubro?",
                "O que mais pesou na rotina da loja nas últimas semanas?",
                "Quando a reunião matinal não acontece, o que muda no dia "
                "do time?",
                "Fechar combinando uma ação pequena para amanhã: qual "
                "rotina você vai testar?",
                "Marcar o acompanhamento na próxima visita e registrar a "
                "data.",
            ],
        )

        problemas = validar_roteiro(roteiro, "Diego Furtado", ())

        self.assertEqual(problemas, [])


if __name__ == "__main__":
    unittest.main()
