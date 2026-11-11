"""Testes dos contratos de vendedores, histórico e geração de feedback.

Verificam a validação da requisição (código obrigatório e mês no formato
AAAA-MM), a limpeza de espaços e a serialização dos DTOs de resposta.

Também confirmam uma regra importante de arquitetura: os DTOs só aceitam
dados simples (texto, número, data, dicionário) — nunca objetos de domínio
(Vendedor, Anotacao...) nem tabelas do Pandas (DataFrame).
"""

import json
import unittest
from datetime import date, datetime, timezone

import pandas as pd
from pydantic import ValidationError

from contracts.feedback import (
    FeedbackGerarRequisicao,
    FeedbackGerarResposta,
    FeedbackRoteiroDTO,
)
from contracts.metricas import MetricaComparadaDTO, MetricasDTO
from contracts.vendedores import (
    AnotacaoDTO,
    FeedbackPreparadoDTO,
    HistoricoVendedorResposta,
    ListaVendedoresResposta,
    VendedorResumoDTO,
)
from domain.anotacao import Anotacao


def metricas_validas() -> MetricasDTO:
    """Devolve métricas fictícias só para montar os DTOs das respostas."""
    return MetricasDTO(
        valor_vendido=128944.49,
        vendas=625,
        pecas=765,
        atendimentos=1238,
        ticket_medio=206.31,
        pecas_por_atendimento=1.224,
        conversao=0.505,
    )


def comparativo_valido() -> list[MetricaComparadaDTO]:
    """Devolve uma lista com uma métrica comparada, como a API devolve."""
    return [
        MetricaComparadaDTO(
            nome="conversao",
            valor=0.505,
            media_time=0.377,
            diferenca_percentual=0.34,
            posicao=1,
            total_vendedores=8,
            situacao="acima",
        )
    ]


class TestFeedbackGerarRequisicao(unittest.TestCase):
    """Testes da entrada da geração de feedback."""

    def test_requisicao_valida(self):
        """Código e mês válidos são aceitos como vieram."""
        requisicao = FeedbackGerarRequisicao(
            vendedor_id="C0031", mes_referencia="2026-10"
        )

        self.assertEqual(requisicao.vendedor_id, "C0031")
        self.assertEqual(requisicao.mes_referencia, "2026-10")

    def test_espacos_nas_pontas_sao_removidos(self):
        """" C0031 " vira "C0031" e " 2026-10 " vira "2026-10".

        A limpeza acontece antes das outras validações, então quem digita com
        espaço a mais não é prejudicado.
        """
        requisicao = FeedbackGerarRequisicao(
            vendedor_id="  C0031  ", mes_referencia=" 2026-10 "
        )

        self.assertEqual(requisicao.vendedor_id, "C0031")
        self.assertEqual(requisicao.mes_referencia, "2026-10")

    def test_mes_ausente_e_aceito(self):
        """Sem mês, o roteiro considera todo o histórico (None)."""
        requisicao = FeedbackGerarRequisicao(vendedor_id="C0031")

        self.assertIsNone(requisicao.mes_referencia)

    def test_vendedor_id_vazio_ou_so_espacos_e_recusado(self):
        """Código vazio ou só com espaços não identifica ninguém: é erro."""
        for valor in ("", "   "):
            with self.subTest(valor=valor):
                with self.assertRaises(ValidationError):
                    FeedbackGerarRequisicao(vendedor_id=valor)

    def test_formatos_de_mes_invalidos_sao_recusados(self):
        """Mês fora de "AAAA-MM" (ou com mês 13) é recusado com erro.

        Cobre os exemplos do enunciado: "2026-13", "2026/10" e "outubro".
        """
        for valor in ("2026-13", "2026/10", "outubro", "2026-1", "26-10"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValidationError):
                    FeedbackGerarRequisicao(
                        vendedor_id="C0031", mes_referencia=valor
                    )

    def test_limites_de_mes_validos(self):
        """Janeiro (01) e dezembro (12) são aceitos."""
        for valor in ("2026-01", "2026-12"):
            with self.subTest(valor=valor):
                requisicao = FeedbackGerarRequisicao(
                    vendedor_id="C0031", mes_referencia=valor
                )
                self.assertEqual(requisicao.mes_referencia, valor)


class TestSerializacaoDeVendedores(unittest.TestCase):
    """Testes da serialização das respostas de vendedores e do histórico."""

    def test_lista_de_vendedores(self):
        """A lista serializa loja, mês e os vendedores com suas métricas."""
        resposta = ListaVendedoresResposta(
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            mes=None,
            vendedores=[
                VendedorResumoDTO(
                    vendedor_id="C0031",
                    nome="Bianca Rocha",
                    cargo="vendedor",
                    metricas=metricas_validas(),
                    comparativo=comparativo_valido(),
                )
            ],
        )

        dados = json.loads(resposta.model_dump_json())

        self.assertEqual(dados["loja_id"], "L004")
        self.assertIsNone(dados["mes"])
        self.assertEqual(len(dados["vendedores"]), 1)
        self.assertEqual(dados["vendedores"][0]["vendedor_id"], "C0031")
        self.assertEqual(
            dados["vendedores"][0]["comparativo"][0]["situacao"], "acima"
        )

    def test_historico_com_anotacoes_e_feedbacks(self):
        """Datas viram texto ISO e o histórico carrega anotações e feedbacks."""
        resposta = HistoricoVendedorResposta(
            vendedor_id="C0031",
            nome="Bianca Rocha",
            cargo="vendedor",
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            metricas=metricas_validas(),
            resumo_mensal=[],
            comparativo=comparativo_valido(),
            anotacoes=[
                AnotacaoDTO(
                    data=date(2026, 8, 6),
                    sobre="Bianca Rocha",
                    texto="Atendeu bem no sábado.",
                    e_do_time=False,
                )
            ],
            anotacoes_do_time=[
                AnotacaoDTO(
                    data=date(2026, 8, 24),
                    sobre="(time)",
                    texto="Sábado corrido.",
                    e_do_time=True,
                )
            ],
            feedbacks_preparados=[
                FeedbackPreparadoDTO(
                    feedback_id="abc-123",
                    mes_referencia="2026-10",
                    gerado_em=datetime(
                        2026, 11, 11, 14, 0, tzinfo=timezone.utc
                    ),
                )
            ],
        )

        dados = json.loads(resposta.model_dump_json())

        # date vira "AAAA-MM-DD" e datetime vira texto ISO com fuso.
        self.assertEqual(dados["anotacoes"][0]["data"], "2026-08-06")
        self.assertEqual(dados["anotacoes"][0]["e_do_time"], False)
        self.assertEqual(dados["anotacoes_do_time"][0]["sobre"], "(time)")
        self.assertTrue(
            dados["feedbacks_preparados"][0]["gerado_em"].startswith(
                "2026-11-11T14:00:00"
            )
        )

    def test_resposta_de_geracao_de_feedback(self):
        """A resposta da geração traz identidade, horário e as quatro listas."""
        resposta = FeedbackGerarResposta(
            feedback_id="abc-123",
            vendedor_id="C0031",
            vendedor_nome="Bianca Rocha",
            mes_referencia=None,
            gerado_em=datetime(2026, 11, 11, 14, 0, tzinfo=timezone.utc),
            roteiro=FeedbackRoteiroDTO(
                pontos_positivos=["Alta conversão"],
                pontos_melhoria=["Vender mais de uma peça"],
                possiveis_motivos=["Correria no sábado"],
                roteiro_conversa=["Como foi o sábado?"],
            ),
        )

        dados = json.loads(resposta.model_dump_json())

        self.assertEqual(dados["vendedor_id"], "C0031")
        self.assertIsNone(dados["mes_referencia"])
        self.assertEqual(
            dados["roteiro"]["pontos_positivos"], ["Alta conversão"]
        )
        self.assertEqual(len(dados["roteiro"]["roteiro_conversa"]), 1)


class TestDTOsNaoAceitamObjetosDeDominio(unittest.TestCase):
    """Os DTOs recebem dados simples, nunca objetos do domínio ou DataFrames.

    Se um objeto de domínio (ou uma tabela do Pandas) entrasse direto, a API
    ficaria acoplada às classes internas e um DataFrame cheio de NaN poderia
    vazar para o JSON.
    """

    def test_anotacao_de_dominio_e_recusada(self):
        """Passar uma Anotacao no lugar do dia (date) levanta ValidationError."""
        anotacao = Anotacao(
            data=date(2026, 8, 6),
            sobre="Bianca Rocha",
            texto="Atendeu bem no sábado.",
        )

        with self.assertRaises(ValidationError):
            AnotacaoDTO(
                data=anotacao,
                sobre="Bianca Rocha",
                texto="Atendeu bem no sábado.",
                e_do_time=False,
            )

    def test_objeto_de_dominio_dentro_de_lista_e_recusado(self):
        """Uma Anotacao dentro da lista de anotações também não passa."""
        anotacao = Anotacao(
            data=date(2026, 8, 6),
            sobre="Bianca Rocha",
            texto="Atendeu bem no sábado.",
        )

        with self.assertRaises(ValidationError):
            HistoricoVendedorResposta(
                vendedor_id="C0031",
                nome="Bianca Rocha",
                cargo="vendedor",
                loja_id="L004",
                loja_nome="Aurora Shopping Centro",
                metricas=metricas_validas(),
                resumo_mensal=[],
                comparativo=[],
                anotacoes=[anotacao],
                anotacoes_do_time=[],
                feedbacks_preparados=[],
            )

    def test_dataframe_nao_e_aceito_como_metricas(self):
        """Um DataFrame no lugar de MetricasDTO levanta ValidationError."""
        tabela = pd.DataFrame({"valor_vendido": [100.0]})

        with self.assertRaises(ValidationError):
            VendedorResumoDTO(
                vendedor_id="C0031",
                nome="Bianca Rocha",
                cargo="vendedor",
                metricas=tabela,
                comparativo=[],
            )
