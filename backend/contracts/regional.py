"""Contratos (formatos) da visão executiva da regional.

Estes modelos alimentam a tela em que a gerente regional acompanha o
desempenho da loja mês a mês e vê para quais vendedores já existe um roteiro
de feedback preparado.

Vocabulário: "roteiro preparado" significa que o roteiro foi GERADO pela IA;
o sistema não sabe se a conversa chegou a acontecer. Nada aqui deve ser
chamado de "realizado".

Todas as razões financeiras trafegam como fração de 0 a 1 (0,5 = 50%),
ausências viram null no JSON e valores NaN/infinito são recusados.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

# Situação do acompanhamento: a pessoa já tem roteiro preparado ou não.
SituacaoAcompanhamento = Literal["com_roteiro", "sem_roteiro"]


class ResultadoLojaMesDTO(BaseModel):
    """Resultado da loja em um mês, separando gerente e vendedores.

    A loja vende com o time e também com o próprio gerente, que atende no
    caixa em horário de pico. Aqui os dois números aparecem separados, além
    do total, para a regional entender de onde vem o resultado.
    """

    mes: str = Field(description='Mês no formato "AAAA-MM" (ex.: "2026-10").')
    mes_parcial: bool = Field(
        description=(
            "True quando o mês tem menos de 10 dias com dados "
            "(mês em andamento ou incompleto)."
        )
    )
    dias_com_dados: int = Field(
        description="Quantos dias do mês têm dados registrados."
    )
    meta_loja: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Meta da loja no mês, em reais. None quando não há meta "
            "cadastrada para o mês."
        ),
    )
    vendas_loja: float = Field(
        allow_inf_nan=False,
        description=(
            "Valor vendido pela loja no mês, em reais, INCLUINDO as vendas "
            "do gerente."
        ),
    )
    atingimento_loja: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Valor vendido pela loja dividido pela meta, como fração de 0 a "
            "1 (1,12 = 112% da meta). None quando não há meta no mês."
        ),
    )
    vendas_vendedores: float = Field(
        allow_inf_nan=False,
        description=(
            "Valor vendido pelos vendedores no mês, em reais, SEM contar o "
            "gerente."
        ),
    )
    atingimento_vendedores: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Valor vendido pelos vendedores dividido pela meta da loja, como "
            "fração de 0 a 1. None quando não há meta no mês."
        ),
    )
    vendas_gerente: float = Field(
        allow_inf_nan=False,
        description="Valor vendido pelo gerente no mês, em reais.",
    )
    participacao_gerente: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Fração das vendas da loja que o gerente fez: "
            "vendas do gerente dividido pelas vendas da loja. "
            "None quando a loja não vendeu nada no mês."
        ),
    )


class AcompanhamentoVendedorDTO(BaseModel):
    """Situação de feedback de um vendedor na visão da regional.

    "roteiros_preparados" conta roteiros GERADOS. Não significa que a
    conversa aconteceu.
    """

    vendedor_id: str = Field(description='Código único da pessoa (ex.: "C0031").')
    nome: str = Field(description="Nome completo da pessoa.")
    anotacoes_do_gerente: int = Field(
        description="Quantas anotações do gerente existem sobre esta pessoa."
    )
    ultima_anotacao_em: date | None = Field(
        default=None,
        description=(
            "Data da anotação mais recente sobre a pessoa. None quando não "
            "há anotação."
        ),
    )
    roteiros_preparados: int = Field(
        description=(
            "Quantos roteiros já foram GERADOS para esta pessoa. "
            "Não significa que a conversa aconteceu."
        )
    )
    ultimo_roteiro_em: datetime | None = Field(
        default=None,
        description=(
            "Data e hora do roteiro gerado mais recente (em UTC). None "
            "quando nenhum roteiro foi preparado."
        ),
    )
    situacao: SituacaoAcompanhamento = Field(
        description=(
            "com_roteiro quando já existe pelo menos um roteiro preparado; "
            "sem_roteiro quando nenhum roteiro foi gerado."
        )
    )


class AcompanhamentoFeedbackDTO(BaseModel):
    """Resumo da cobertura de feedbacks preparados na loja.

    Cobertura é a fração de vendedores que já têm ao menos um roteiro
    preparado: vendedores com roteiro dividido pelo total de vendedores.
    """

    total_vendedores: int = Field(
        description="Quantos vendedores existem na loja."
    )
    vendedores_com_roteiro: int = Field(
        description="Quantos vendedores já têm ao menos um roteiro preparado."
    )
    cobertura: float = Field(
        allow_inf_nan=False,
        description=(
            "Fração de vendedores com roteiro preparado, de 0 a 1 "
            "(0,5 = metade do time)."
        ),
    )
    total_roteiros_preparados: int = Field(
        description=(
            "Soma de todos os roteiros GERADOS para o time. "
            "Não significa conversas realizadas."
        )
    )
    vendedores: list[AcompanhamentoVendedorDTO] = Field(
        description="Um item por vendedor, com sua situação de feedback."
    )


class AnotacaoRegionalDTO(BaseModel):
    """Uma anotação escrita pela gerente regional sobre a loja."""

    data: date = Field(description="Dia em que a anotação foi feita.")
    autora: str = Field(description="Quem escreveu a anotação.")
    texto: str = Field(
        description="O que foi escrito, do jeito que foi digitado."
    )


class DesempenhoGerenteResposta(BaseModel):
    """Resposta da visão executiva da regional para um gerente de loja.

    Junta três blocos: o resultado mês a mês, o acompanhamento dos feedbacks
    preparados e as anotações que a própria regional escreveu sobre a loja.
    """

    gerente_id: str = Field(description='Código do gerente (ex.: "C0030").')
    gerente_nome: str = Field(description="Nome completo do gerente.")
    loja_id: str = Field(description='Código da loja (ex.: "L004").')
    loja_nome: str = Field(description="Nome da loja.")
    periodo_inicio: date | None = Field(
        default=None,
        description=(
            "Primeiro dia com dados considerado na análise. None quando o "
            "período não foi limitado."
        ),
    )
    periodo_fim: date | None = Field(
        default=None,
        description=(
            "Último dia com dados considerado na análise. None quando o "
            "período não foi limitado."
        ),
    )
    resultado_loja: list[ResultadoLojaMesDTO] = Field(
        description="Resultado da loja, um item por mês, em ordem cronológica."
    )
    acompanhamento_feedback: AcompanhamentoFeedbackDTO = Field(
        description=(
            "Cobertura e situação dos roteiros preparados para o time."
        )
    )
    anotacoes_regional: list[AnotacaoRegionalDTO] = Field(
        description=(
            "Anotações da regional sobre a loja, em ordem cronológica."
        )
    )
