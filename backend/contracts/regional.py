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

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from config import ANOTACAO_TEXTO_MAXIMO
from contracts.feedback import FeedbackRoteiroDTO

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


# ---------------------------------------------------------------------------
# Contratos das rotas POR LOJA da Etapa 8 (a regional escolhe a loja).
# As descrições usam "preparado" (roteiro GERADO); nada aqui diz "realizado".
# ---------------------------------------------------------------------------


class LojaResumoDTO(BaseModel):
    """Uma loja na lista de lojas da regional.

    Traz só o necessário para o seletor da barra lateral: o código e o nome
    da loja, mais quem é o gerente responsável.
    """

    loja_id: str = Field(description='Código da loja (ex.: "L004").')
    loja_nome: str = Field(description="Nome da loja.")
    gerente_id: str = Field(description='Código do gerente (ex.: "C0030").')
    gerente_nome: str = Field(description="Nome completo do gerente.")


class ListaLojasResposta(BaseModel):
    """Resposta da rota que lista as lojas disponíveis para a regional."""

    lojas: list[LojaResumoDTO] = Field(
        description="Lojas que a regional pode acompanhar."
    )


class FeedbackGerenteGeradoDTO(BaseModel):
    """Um roteiro já PREPARADO para o gerente de uma loja.

    "Preparado" significa que o roteiro foi GERADO pela IA; o sistema não sabe
    se a conversa aconteceu. O conteúdo vai junto para a lista de roteiros
    anteriores poder ser aberta sem uma segunda chamada.
    """

    feedback_id: str = Field(
        description="Identificador único do roteiro preparado."
    )
    mes_referencia: str | None = Field(
        default=None,
        description=(
            'Mês analisado no formato "AAAA-MM". None quando o roteiro '
            "considerou todo o histórico."
        ),
    )
    gerado_em: datetime = Field(
        description="Data e hora em que o roteiro foi preparado (em UTC)."
    )
    roteiro: FeedbackRoteiroDTO = Field(
        description="Conteúdo do roteiro preparado, em quatro listas de textos."
    )


class HistoricoLojaResposta(DesempenhoGerenteResposta):
    """Histórico de uma loja: o consolidado da visão regional + roteiros.

    Herda todos os blocos de DesempenhoGerenteResposta (resultado mês a mês,
    acompanhamento dos vendedores e anotações da regional) e acrescenta os
    roteiros já PREPARADOS para o gerente daquela loja, do mais novo para o
    mais antigo.
    """

    feedbacks_preparados: list[FeedbackGerenteGeradoDTO] = Field(
        description=(
            "Roteiros já preparados para o gerente da loja, do mais novo "
            "para o mais antigo. Preparado = GERADO; não confirma conversa."
        )
    )


class AnotacaoRegionalNovaRequisicao(BaseModel):
    """Dados que a regional envia para gravar uma anotação nova.

    Recebe APENAS o texto. A autora (Patrícia Lemos) e a data (hoje no
    servidor) NÃO vêm do cliente, para ninguém conseguir se passar por outra
    pessoa nem inventar a data.

    Regras: os espaços das pontas saem antes da contagem; texto vazio ou só
    com espaços é recusado; o limite é o MESMO do serviço (config).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    texto: str = Field(
        min_length=1,
        max_length=ANOTACAO_TEXTO_MAXIMO,
        description=(
            "O que a regional escreveu sobre a loja. Até "
            f"{ANOTACAO_TEXTO_MAXIMO} caracteres; não pode ser vazio."
        ),
    )


class FeedbackRegionalGerarRequisicao(BaseModel):
    """Dados que o frontend envia para gerar o roteiro do gerente da loja.

    Recebe:
        loja_id: código da loja; obrigatório, sem espaços nas pontas.
        mes_referencia: mês "AAAA-MM" ou None (todo o histórico).

    Exemplo: FeedbackRegionalGerarRequisicao(
        loja_id=" L004 ", mes_referencia="2026-10"
    )
    """

    # str_strip_whitespace remove os espaços das pontas de todo texto ANTES
    # das outras validações; " L004 " vira "L004" e "   " vira "".
    model_config = ConfigDict(str_strip_whitespace=True)

    loja_id: str = Field(
        min_length=1,
        description='Código da loja (ex.: "L004").',
    )
    mes_referencia: str | None = Field(
        default=None,
        description=(
            'Mês no formato "AAAA-MM" (ex.: "2026-10"). Sem valor, usa todo '
            "o histórico."
        ),
    )

    @field_validator("mes_referencia")
    @classmethod
    def _validar_mes_referencia(cls, valor: str | None) -> str | None:
        """Confere o formato "AAAA-MM", com mês de 01 a 12.

        A regra é a MESMA da geração do vendedor: quatro dígitos, hífen e mês
        entre 01 e 12. Assim "2026-10" passa e "2026-13" é recusado.
        """
        if valor is None:
            return None

        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", valor):
            raise ValueError(
                'O mês deve estar no formato "AAAA-MM" (ex.: "2026-10"), '
                "com o mês entre 01 e 12."
            )
        return valor


class FeedbackRegionalGerarResposta(BaseModel):
    """Resposta da rota que gera o roteiro da regional para o gerente."""

    feedback_id: str = Field(
        description="Identificador único do roteiro preparado."
    )
    loja_id: str = Field(description="Código da loja.")
    loja_nome: str = Field(description="Nome da loja.")
    gerente_id: str = Field(description="Código do gerente avaliado.")
    gerente_nome: str = Field(description="Nome completo do gerente avaliado.")
    mes_referencia: str | None = Field(
        default=None,
        description=(
            'Mês analisado no formato "AAAA-MM". None quando o roteiro '
            "considerou todo o histórico."
        ),
    )
    gerado_em: datetime = Field(
        description="Data e hora em que o roteiro foi preparado (em UTC)."
    )
    roteiro: FeedbackRoteiroDTO = Field(
        description="Conteúdo do roteiro preparado, em quatro listas de textos."
    )
