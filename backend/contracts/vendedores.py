"""Contratos (formatos) das respostas de vendedores e do histórico.

Estes modelos dizem exatamente o que o frontend recebe nas rotas de listagem
de vendedores e de histórico individual. Eles só carregam dados já calculados
no domínio; as descrições em português aparecem no Swagger.

Termos:
    DTO: "objeto de transferência de dados", o formato combinado entre a API
        e quem a consome.
    date/datetime: tipos do Python para dia e para dia com hora. O Pydantic
        os transforma em texto ISO no JSON ("2026-08-06", "...T14:00:00Z").
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from contracts.metricas import (
    MetricaComparadaDTO,
    MetricasDTO,
    ResumoMensalDTO,
)


class AnotacaoDTO(BaseModel):
    """Uma anotação do gerente sobre uma pessoa ou sobre o time."""

    data: date = Field(description="Dia em que a anotação foi feita.")
    sobre: str = Field(
        description=(
            'Nome da pessoa ou "(time)" quando a anotação vale para a '
            "equipe inteira."
        )
    )
    texto: str = Field(
        description="O que o gerente escreveu, do jeito que digitou."
    )
    e_do_time: bool = Field(
        description=(
            "True quando a anotação é sobre o time inteiro e não sobre uma "
            "pessoa específica."
        )
    )


class FeedbackPreparadoDTO(BaseModel):
    """Um roteiro que já foi gerado para a pessoa (resumo, sem o conteúdo).

    Usa "preparado" de propósito: o sistema sabe que o roteiro foi gerado,
    mas não sabe se a conversa chegou a acontecer.
    """

    feedback_id: str = Field(
        description="Identificador único do roteiro gerado."
    )
    mes_referencia: str | None = Field(
        default=None,
        description=(
            'Mês analisado no formato "AAAA-MM". None quando o roteiro '
            "considerou todo o histórico."
        ),
    )
    gerado_em: datetime = Field(
        description="Data e hora em que o roteiro foi gerado (em UTC)."
    )


class VendedorResumoDTO(BaseModel):
    """Um vendedor com as métricas consolidadas e o comparativo do time."""

    vendedor_id: str = Field(description='Código único (ex.: "C0031").')
    nome: str = Field(description="Nome completo da pessoa.")
    cargo: str = Field(description='Cargo da pessoa (ex.: "vendedor").')
    metricas: MetricasDTO = Field(
        description="Indicadores consolidados do período pedido."
    )
    comparativo: list[MetricaComparadaDTO] = Field(
        description=(
            "Cada métrica comparada com a média do time (ticket médio, "
            "peças por venda e conversão)."
        )
    )


class ListaVendedoresResposta(BaseModel):
    """Resposta da rota que lista os vendedores de uma loja."""

    loja_id: str = Field(description='Código da loja (ex.: "L004").')
    loja_nome: str = Field(description="Nome da loja.")
    mes: str | None = Field(
        default=None,
        description=(
            'Mês considerado no formato "AAAA-MM". None quando foram usados '
            "todos os meses do histórico."
        ),
    )
    vendedores: list[VendedorResumoDTO] = Field(
        description="Vendedores da loja, cada um com suas métricas."
    )


class HistoricoVendedorResposta(BaseModel):
    """Resposta da rota com o histórico detalhado de um vendedor."""

    vendedor_id: str = Field(description="Código único da pessoa.")
    nome: str = Field(description="Nome completo da pessoa.")
    cargo: str = Field(description="Cargo da pessoa.")
    loja_id: str = Field(description="Código da loja.")
    loja_nome: str = Field(description="Nome da loja.")
    metricas: MetricasDTO = Field(
        description="Indicadores consolidados de todo o histórico."
    )
    resumo_mensal: list[ResumoMensalDTO] = Field(
        description=(
            "Um item por mês com dados, em ordem cronológica, incluindo o "
            "aviso de mês parcial."
        )
    )
    comparativo: list[MetricaComparadaDTO] = Field(
        description="Métricas comparadas com a média do time."
    )
    anotacoes: list[AnotacaoDTO] = Field(
        description=(
            "Anotações do gerente que falam SOMENTE desta pessoa, em ordem "
            "cronológica."
        )
    )
    anotacoes_do_time: list[AnotacaoDTO] = Field(
        description=(
            "Anotações do gerente sobre o time inteiro, que servem de "
            "contexto para a conversa."
        )
    )
    feedbacks_preparados: list[FeedbackPreparadoDTO] = Field(
        description=(
            "Roteiros já gerados para esta pessoa, do mais novo para o mais "
            "antigo. Não significa que a conversa aconteceu."
        )
    )
