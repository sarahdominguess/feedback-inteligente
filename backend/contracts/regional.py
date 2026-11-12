"""Contratos (formatos) da visão executiva da regional.

Estes modelos alimentam a tela em que a gerente regional acompanha o
desempenho da loja mês a mês e vê para quais vendedores já existe um roteiro
de feedback preparado.

Vocabulário: "roteiro preparado" significa que o roteiro foi GERADO pela IA;
o sistema não sabe se a conversa chegou a acontecer. Nada aqui deve ser
chamado de "realizado".

Todas as razões financeiras trafegam como fração de 0 a 1 (0,5 = 50%),
ausências viram null no JSON e valores NaN/infinito são recusados.

Este arquivo também guarda os contratos da geração de feedback da regional
PARA o gerente da loja: o pedido (com mês opcional) e a resposta (o roteiro
gerado, mais quem foi avaliado e quando). O formato do roteiro em si é o
mesmo do feedback do vendedor (FeedbackRoteiroDTO), reaproveitado aqui para o
frontend usar os mesmos componentes nos dois casos.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from config import ANOTACAO_TEXTO_MAXIMO
from contracts.feedback import FeedbackRoteiroDTO, validar_formato_mes_referencia
from contracts.vendedores import FeedbackPreparadoDTO

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


class AnotacaoRegionalNovaRequisicao(BaseModel):
    """Dados que o frontend envia para a regional gravar uma anotação nova.

    Recebe APENAS o texto. A data e a autora NÃO vêm do cliente:
    - a data é o dia de hoje no servidor, para ninguém inventar ou adulterar;
    - a autora é a padrão do config (Patrícia Lemos), porque o sistema não
      tem login para descobrir quem está digitando.

    Regras de validação (o FastAPI devolve 400 com {"erro": ...} quando elas
    falham):
    - str_strip_whitespace remove os espaços das pontas ANTES de contar;
    - min_length=1 recusa texto vazio e texto só com espaços (que vira "");
    - max_length usa o MESMO limite do serviço (config), para as duas camadas
      nunca divergirem.

    Exemplo: AnotacaoRegionalNovaRequisicao(texto="  visitar a loja  ")
    vira texto="visitar a loja".
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


class AnotacaoRegionalDTO(BaseModel):
    """Uma anotação escrita pela gerente regional sobre a loja."""

    data: date = Field(description="Dia em que a anotação foi feita.")
    autora: str = Field(description="Quem escreveu a anotação.")
    texto: str = Field(
        description="O que foi escrito, do jeito que foi digitado."
    )


class FeedbackRegionalGerarRequisicao(BaseModel):
    """Dados que o frontend envia para a regional gerar feedback ao gerente.

    Recebe APENAS o mês de referência, e ele é opcional (None = todo o
    histórico). Duas ausências são de propósito:

    - o gerente avaliado NÃO vem do cliente: o servidor usa o gerente da loja
      que a regional está acompanhando. Como o frontend não manda o nome,
      ninguém consegue pedir um roteiro para a pessoa errada;
    - as anotações e os números também não vêm do cliente: o servidor lê dos
      arquivos de dados, para a IA nunca receber números inventados pela tela.

    A validação do mês reaproveita a regra do feedback do vendedor, então
    "2026-10" passa e "2026-13" é recusado do mesmo jeito nos dois contratos.
    """

    # str_strip_whitespace tira os espaços das pontas de todo texto recebido:
    # " 2026-10 " vira "2026-10" antes da checagem do molde do mês.
    model_config = ConfigDict(str_strip_whitespace=True)

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
        """Aplica o mesmo molde de mês usado no feedback do vendedor.

        O @field_validator avisa o Pydantic para chamar este método quando o
        campo "mes_referencia" chegar. A regra mora em
        validar_formato_mes_referencia (contrato do feedback do vendedor),
        para os dois contratos nunca divergirem.
        """
        return validar_formato_mes_referencia(valor)


class FeedbackRegionalGerarResposta(BaseModel):
    """Resposta da rota que gera o roteiro de feedback para o gerente da loja.

    Leva junto quem foi avaliado (o gerente) e de qual loja, porque o roteiro
    é sempre sobre uma dupla loja + gerente. O bloco "roteiro" usa o MESMO
    formato da geração do vendedor (FeedbackRoteiroDTO), então a tela mostra
    os dois com os mesmos componentes.
    """

    feedback_id: str = Field(
        description="Identificador único do roteiro gerado."
    )
    loja_id: str = Field(description='Código da loja (ex.: "L004").')
    loja_nome: str = Field(description="Nome da loja.")
    gerente_id: str = Field(description='Código do gerente (ex.: "C0030").')
    gerente_nome: str = Field(description="Nome completo do gerente avaliado.")
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
    roteiro: FeedbackRoteiroDTO = Field(
        description="Conteúdo do roteiro, em quatro listas de textos."
    )


class DesempenhoGerenteResposta(BaseModel):
    """Resposta da visão executiva da regional para um gerente de loja.

    Junta quatro blocos: o resultado mês a mês, o acompanhamento dos feedbacks
    preparados para o time, as anotações que a própria regional escreveu sobre
    a loja e os roteiros que a regional já gerou PARA o gerente.
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
    # default_factory=list faz o campo valer [] quando o dado não vem: assim
    # uma resposta montada antes deste campo existir continua sendo aceita, e
    # cada resposta ganha a SUA própria lista (nunca uma lista compartilhada).
    feedbacks_preparados: list[FeedbackPreparadoDTO] = Field(
        default_factory=list,
        description=(
            "Roteiros de feedback já gerados pela regional para o gerente da "
            "loja. Não significa que a conversa aconteceu."
        ),
    )
