"""Contratos (formatos) das métricas devolvidas pela API.

Estes modelos definem exatamente quais campos o frontend recebe e quais
descrições aparecem na documentação automática (Swagger). Eles só transportam
números já calculados no domínio; nenhuma conta é feita aqui.

Termos:
    Pydantic: biblioteca que valida os dados e converte objetos para JSON.
    BaseModel: a classe "molde" do Pydantic; cada atributo vira um campo.
    Literal: tipo que aceita apenas uma lista fechada de textos; se vier
        outro valor, a validação falha na hora.
    None: o "sem valor" do Python. Em JSON ele aparece como null.
    NaN: "not a number", um número inválido que às vezes surge em contas
        (ex.: 0 ÷ 0). NaN não existe em JSON e quebraria o frontend.
    Infinito (inf): resultado de uma divisão por zero muito pequena; também
        não existe em JSON.

Sobre allow_inf_nan=False: pedimos ao Pydantic para RECUSAR NaN e infinito
em todo campo float. No Pydantic 2.x (aqui, 2.14.3) essa opção funciona tanto
em float quanto em float | None — conferido antes de escrever o código.
"""

from typing import Literal

from pydantic import BaseModel, Field

# Situação de uma métrica em relação à média do time. A tolerância de 5% em
# torno da média é aplicada no domínio (DataLoader); aqui só fechamos quais
# textos são aceitos, para um valor digitado errado nunca chegar ao frontend.
SituacaoMetrica = Literal["acima", "abaixo", "na_media", "indisponivel"]

# Nome das três métricas comparadas com o time.
NomeMetrica = Literal["ticket_medio", "pecas_por_atendimento", "conversao"]


class MetricasDTO(BaseModel):
    """Indicadores consolidados de um vendedor num período.

    Todos os números vêm prontos do domínio (Vendedor). As métricas que
    dependem de uma divisão vêm como None quando não há base para calcular
    (por exemplo, sem vendas no período), nunca como NaN.

    Exemplo:
    MetricasDTO(
        valor_vendido=128944.49, vendas=625, pecas=765, atendimentos=1238,
        ticket_medio=206.31, pecas_por_atendimento=1.224, conversao=0.505,
    )
    """

    valor_vendido: float = Field(
        allow_inf_nan=False,
        description="Valor total vendido no período, em reais.",
    )
    vendas: int = Field(description="Número de vendas no período.")
    pecas: int = Field(description="Número de peças vendidas no período.")
    atendimentos: int = Field(
        description="Número de clientes atendidos no período."
    )
    ticket_medio: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Valor vendido dividido pelo número de vendas, em reais. "
            "None (null no JSON) quando não há vendas no período."
        ),
    )
    pecas_por_atendimento: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Peças divididas pelo número de vendas (P.A.). "
            "None (null no JSON) quando não há vendas no período."
        ),
    )
    conversao: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Vendas divididas pelos atendimentos, como fração de 0 a 1 "
            "(0,5 = 50%). None (null no JSON) quando não há atendimentos."
        ),
    )


class MetricaComparadaDTO(BaseModel):
    """Uma métrica do vendedor comparada com a média do time.

    Espelha a entidade MetricaComparada do domínio. A média do time é
    calculada com as somas de todos os vendedores, nunca pela média das
    razões individuais.
    """

    nome: NomeMetrica = Field(
        description=(
            "Métrica comparada: ticket_medio, pecas_por_atendimento "
            "ou conversao."
        )
    )
    valor: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Valor do vendedor na métrica. None quando ele não tem dados "
            "no período."
        ),
    )
    media_time: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Média do time no mesmo período. None quando não é possível "
            "calcular (por exemplo, sem vendas no time)."
        ),
    )
    diferenca_percentual: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Diferença em relação à média, como fração: "
            "(valor menos média) dividido pela média. "
            "-0,20 significa 20% abaixo. None quando não dá para comparar."
        ),
    )
    posicao: int | None = Field(
        default=None,
        description=(
            "Posição no ranking dos vendedores (1 = melhor). "
            "None quando o vendedor não entra no ranking por falta de dados."
        ),
    )
    total_vendedores: int = Field(
        description="Quantos vendedores existem no time considerado."
    )
    situacao: SituacaoMetrica = Field(
        description=(
            "Situação em relação à média: acima, abaixo, na_media "
            "(dentro de 5% para mais ou para menos) ou indisponivel."
        )
    )


class ResumoMensalDTO(BaseModel):
    """Métricas de um mês específico do vendedor.

    Espelha um item de Vendedor.resumo_mensal(). O campo mes_parcial avisa
    quando o mês tem poucos dias com dados (por exemplo, novembro com 1 dia),
    para a tela não comparar um mês incompleto com um mês cheio.
    """

    mes: str = Field(description="Mês no formato AAAA-MM (ex.: 2026-10).")
    dias_com_dados: int = Field(
        description="Quantos dias do mês têm dados registrados."
    )
    mes_parcial: bool = Field(
        description=(
            "True quando o mês tem menos de 10 dias com dados "
            "(mês em andamento ou incompleto)."
        )
    )
    valor_vendido: float = Field(
        allow_inf_nan=False,
        description="Valor total vendido no mês, em reais.",
    )
    vendas: int = Field(description="Número de vendas no mês.")
    pecas: int = Field(description="Número de peças vendidas no mês.")
    atendimentos: int = Field(
        description="Número de clientes atendidos no mês."
    )
    ticket_medio: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Valor vendido dividido pelo número de vendas, em reais. "
            "None quando não há vendas no mês."
        ),
    )
    pecas_por_atendimento: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Peças divididas pelo número de vendas (P.A.). "
            "None quando não há vendas no mês."
        ),
    )
    conversao: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Vendas divididas pelos atendimentos, como fração de 0 a 1. "
            "None quando não há atendimentos no mês."
        ),
    )
    meta: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Meta do mês em reais. None quando o mês não tem meta "
            "cadastrada (ou a pessoa não tem meta individual)."
        ),
    )
    atingimento_meta: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Valor vendido dividido pela meta, como fração "
            "(1,12 = 112% da meta). None quando não há meta no mês."
        ),
    )
