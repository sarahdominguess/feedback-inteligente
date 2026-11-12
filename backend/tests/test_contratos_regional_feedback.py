"""Testes dos contratos do feedback que a regional gera PARA o gerente.

Cobrem três pontos:
- o PEDIDO (FeedbackRegionalGerarRequisicao): o mês é opcional e um mês
  inexistente é recusado com a MESMA regra do feedback do vendedor;
- a RESPOSTA (FeedbackRegionalGerarResposta): leva quem foi avaliado e o
  roteiro gerado;
- o campo novo feedbacks_preparados em DesempenhoGerenteResposta: respostas
  montadas sem esse campo continuam válidas e valem lista vazia.

Todos os dados aqui são fictícios e os testes não dependem de arquivos nem de
internet: só montam e desmontam os modelos do Pydantic.
"""

import json
import unittest

from pydantic import ValidationError

from contracts.feedback import FeedbackGerarRequisicao
from contracts.regional import (
    DesempenhoGerenteResposta,
    FeedbackRegionalGerarRequisicao,
    FeedbackRegionalGerarResposta,
)


def roteiro_valido() -> dict:
    """As quatro listas de um roteiro, no formato que a IA devolve."""
    return {
        "pontos_positivos": ["A loja bateu a meta da loja em outubro."],
        "pontos_melhoria": [
            "Situação: pico de sábado. Comportamento: o gerente ficou no "
            "caixa. Impacto: o time ficou sem acompanhamento."
        ],
        "possiveis_motivos": ["Falta de escala para o horário de pico."],
        "roteiro_conversa": ["O que você observa no pico de sábado?"],
    }


def feedback_preparado_valido(**alteracoes) -> dict:
    """Um roteiro JÁ gerado para o gerente, como aparece na lista."""
    dados = {
        "feedback_id": "fb-regional-001",
        "mes_referencia": "2026-10",
        "gerado_em": "2026-11-12T14:00:00+00:00",
        "roteiro": roteiro_valido(),
    }
    dados.update(alteracoes)
    return dados


def desempenho_sem_feedbacks() -> dict:
    """Resposta da regional como era ANTES do campo feedbacks_preparados.

    É um dicionário comum, SEM a chave feedbacks_preparados — do jeito que
    uma versão anterior da API (ou um registro antigo) devolveria. Serve para
    provar que o campo novo não quebra o que já existia.
    """
    return {
        "gerente_id": "C0030",
        "gerente_nome": "Diego Furtado",
        "loja_id": "L004",
        "loja_nome": "Aurora Shopping Centro",
        "resultado_loja": [
            {
                "mes": "2026-10",
                "mes_parcial": False,
                "dias_com_dados": 27,
                "meta_loja": 317200.0,
                "vendas_loja": 326700.0,
                "atingimento_loja": 1.03,
                "vendas_vendedores": 315784.37,
                "atingimento_vendedores": 0.9955,
                "vendas_gerente": 10915.63,
                "participacao_gerente": 0.0334,
            }
        ],
        "acompanhamento_feedback": {
            "total_vendedores": 1,
            "vendedores_com_roteiro": 1,
            "cobertura": 1.0,
            "total_roteiros_preparados": 2,
            "vendedores": [
                {
                    "vendedor_id": "C0031",
                    "nome": "Bianca Rocha",
                    "anotacoes_do_gerente": 3,
                    "ultima_anotacao_em": "2026-10-08",
                    "roteiros_preparados": 2,
                    "ultimo_roteiro_em": "2026-11-11T14:00:00+00:00",
                    "situacao": "com_roteiro",
                }
            ],
        },
        "anotacoes_regional": [
            {
                "data": "2026-09-15",
                "autora": "Patrícia Lemos",
                "texto": (
                    "A reunião matinal não aconteceu nas duas últimas "
                    "visitas."
                ),
            }
        ],
    }


class TestPedidoDeFeedbackDaRegional(unittest.TestCase):
    """Pedido que o frontend manda para gerar o roteiro do gerente."""

    def test_sem_mes_usa_todo_o_historico(self):
        """Um pedido vazio é aceito e o mês fica None (todo o histórico)."""
        requisicao = FeedbackRegionalGerarRequisicao()

        self.assertIsNone(requisicao.mes_referencia)

    def test_mes_valido_e_aceito(self):
        """Meses de janeiro a dezembro passam, incluindo as bordas 01 e 12."""
        for mes in ("2026-01", "2026-10", "2026-12"):
            with self.subTest(mes=mes):
                requisicao = FeedbackRegionalGerarRequisicao(
                    mes_referencia=mes
                )
                self.assertEqual(requisicao.mes_referencia, mes)

    def test_espacos_das_pontas_somem(self):
        """str_strip_whitespace limpa o texto antes da checagem do mês.

        Sem isso, uma resposta colada com espaço (" 2026-10 ") seria recusada
        mesmo sendo um mês válido.
        """
        requisicao = FeedbackRegionalGerarRequisicao(
            mes_referencia=" 2026-10 "
        )

        self.assertEqual(requisicao.mes_referencia, "2026-10")

    def test_mes_13_e_recusado(self):
        """Mês 13 não existe: o Pydantic levanta ValidationError."""
        with self.assertRaises(ValidationError):
            FeedbackRegionalGerarRequisicao(mes_referencia="2026-13")

    def test_texto_fora_do_molde_e_recusado(self):
        """Mês escrito de outro jeito também é recusado."""
        for mes in ("2026/10", "outubro", "26-10"):
            with self.subTest(mes=mes):
                with self.assertRaises(ValidationError):
                    FeedbackRegionalGerarRequisicao(mes_referencia=mes)


class TestRegraDoMesCompartilhada(unittest.TestCase):
    """Os dois contratos com mês usam a mesma regra (sem cópia divergente).

    O feedback do vendedor e o feedback do gerente chamam o mesmo validador
    de mês. Este teste garante que o contrato antigo continua recusando e
    aceitando exatamente o que recusava antes.
    """

    def test_contrato_do_vendedor_continua_com_a_mesma_regra(self):
        """Mês válido passa; mês 13 é recusado nos dois contratos."""
        valido = FeedbackGerarRequisicao(
            vendedor_id="C0031", mes_referencia="2026-10"
        )
        self.assertEqual(valido.mes_referencia, "2026-10")

        with self.assertRaises(ValidationError):
            FeedbackGerarRequisicao(
                vendedor_id="C0031", mes_referencia="2026-13"
            )

        with self.assertRaises(ValidationError):
            FeedbackRegionalGerarRequisicao(mes_referencia="2026-13")


class TestRespostaDeFeedbackDaRegional(unittest.TestCase):
    """Resposta da geração: quem foi avaliado e o roteiro gerado."""

    def _resposta(self, **alteracoes) -> FeedbackRegionalGerarResposta:
        """Monta a resposta completa com dados fictícios."""
        dados = {
            "feedback_id": "fb-regional-001",
            "loja_id": "L004",
            "loja_nome": "Aurora Shopping Centro",
            "gerente_id": "C0030",
            "gerente_nome": "Diego Furtado",
            "mes_referencia": "2026-10",
            "gerado_em": "2026-11-12T14:00:00+00:00",
            "roteiro": roteiro_valido(),
        }
        dados.update(alteracoes)
        return FeedbackRegionalGerarResposta(**dados)

    def test_resposta_completa_e_aceita(self):
        """Todos os campos chegam intactos e o roteiro tem as quatro listas."""
        resposta = self._resposta()

        self.assertEqual(resposta.gerente_nome, "Diego Furtado")
        self.assertEqual(resposta.loja_id, "L004")
        self.assertEqual(len(resposta.roteiro.pontos_positivos), 1)
        self.assertEqual(len(resposta.roteiro.roteiro_conversa), 1)

    def test_roteiro_e_obrigatorio(self):
        """Sem o conteúdo do roteiro a resposta é recusada.

        Um feedback sem conteúdo não teria o que mostrar na tela, então o
        contrato não deixa passar.
        """
        dados = {
            "feedback_id": "fb-regional-001",
            "loja_id": "L004",
            "loja_nome": "Aurora Shopping Centro",
            "gerente_id": "C0030",
            "gerente_nome": "Diego Furtado",
            "gerado_em": "2026-11-12T14:00:00+00:00",
        }

        with self.assertRaises(ValidationError):
            FeedbackRegionalGerarResposta(**dados)

    def test_data_vira_texto_iso_no_json(self):
        """A data/hora sai no padrão ISO, que é o que o frontend entende."""
        dados = json.loads(self._resposta().model_dump_json())

        self.assertTrue(dados["gerado_em"].startswith("2026-11-12T14:00:00"))


class TestDesempenhoGerenteComFeedbacksPreparados(unittest.TestCase):
    """O campo novo feedbacks_preparados na resposta da regional."""

    def test_sem_o_campo_vira_lista_vazia(self):
        """Resposta antiga (sem a chave) continua válida e ganha []."""
        resposta = DesempenhoGerenteResposta(**desempenho_sem_feedbacks())

        self.assertEqual(resposta.feedbacks_preparados, [])

    def test_com_roteiros_preenchidos(self):
        """A lista com itens é aceita e o conteúdo fica acessível."""
        dados = desempenho_sem_feedbacks()
        dados["feedbacks_preparados"] = [
            feedback_preparado_valido(feedback_id="fb-regional-002"),
            feedback_preparado_valido(
                feedback_id="fb-regional-001", mes_referencia=None
            ),
        ]

        resposta = DesempenhoGerenteResposta(**dados)

        self.assertEqual(len(resposta.feedbacks_preparados), 2)
        self.assertEqual(
            resposta.feedbacks_preparados[0].feedback_id, "fb-regional-002"
        )
        self.assertIsNone(resposta.feedbacks_preparados[1].mes_referencia)
        self.assertEqual(
            len(resposta.feedbacks_preparados[0].roteiro.possiveis_motivos), 1
        )

    def test_roteiros_aparecem_no_json(self):
        """O conteúdo do roteiro também sai serializado para o frontend."""
        dados = desempenho_sem_feedbacks()
        dados["feedbacks_preparados"] = [feedback_preparado_valido()]

        json_da_resposta = json.loads(
            DesempenhoGerenteResposta(**dados).model_dump_json()
        )

        self.assertEqual(len(json_da_resposta["feedbacks_preparados"]), 1)
        self.assertIn(
            "roteiro_conversa",
            json_da_resposta["feedbacks_preparados"][0]["roteiro"],
        )

    def test_cada_resposta_tem_a_sua_propria_lista(self):
        """default_factory evita a lista compartilhada entre respostas.

        Se o padrão fosse um [] fixo no código, mexer numa resposta mudaria
        a lista "vazia" das outras — um defeito silencioso e difícil de achar.
        """
        primeira = DesempenhoGerenteResposta(**desempenho_sem_feedbacks())
        segunda = DesempenhoGerenteResposta(**desempenho_sem_feedbacks())

        primeira.feedbacks_preparados.append(
            feedback_preparado_valido()
        )

        self.assertEqual(len(primeira.feedbacks_preparados), 1)
        self.assertEqual(segunda.feedbacks_preparados, [])


if __name__ == "__main__":
    unittest.main()
