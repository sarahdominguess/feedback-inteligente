"""Contratos (formatos) de entrada e saída da geração de feedback.

A entrada traz apenas quem deve ser avaliado e, se a pessoa quiser, um mês
específico. A saída devolve o roteiro em quatro listas, com o identificador e
o horário do registro.

Termos:
    Pydantic: biblioteca que valida dados e converte objetos para JSON.
    Validador: função que confere uma regra antes do dado ser aceito.
"""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Molde (regex) do mês de referência: quatro dígitos, um hífen e um mês de 01
# a 12. Fica em UMA constante porque o mesmo campo "mes_referencia" existe em
# mais de um contrato (feedback do vendedor e feedback do gerente da loja).
# Com uma constante só, os dois aceitam e recusam exatamente as mesmas coisas.
MES_REFERENCIA_REGEX = re.compile(r"\d{4}-(0[1-9]|1[0-2])")


def validar_formato_mes_referencia(valor: str | None) -> str | None:
    """Confere se o mês está no formato "AAAA-MM" com mês de 01 a 12.

    Uma expressão regular (regex) é um "molde" de texto: aqui \d{4} significa
    "quatro dígitos" e (0[1-9]|1[0-2]) significa "01 a 09 ou 10 a 12". Assim
    "2026-10" passa, e "2026-13", "2026/10" ou "outubro" são recusados com um
    erro claro em português.

    None continua sendo aceito: significa "todo o histórico", ou seja, o
    usuário não escolheu um mês.

    Esta função é pública e sem estado de propósito, para que qualquer
    contrato com mês de referência chame a MESMA regra em vez de copiar a
    regex (cópia é defeito: um dia as duas cópias divergem).
    """
    if valor is None:
        return None

    if not MES_REFERENCIA_REGEX.fullmatch(valor):
        raise ValueError(
            'O mês deve estar no formato "AAAA-MM" (ex.: "2026-10"), '
            "com o mês entre 01 e 12."
        )
    return valor


class FeedbackGerarRequisicao(BaseModel):
    """Dados que o frontend envia para pedir um roteiro de feedback.

    Recebe:
        vendedor_id: código da pessoa; obrigatório, sem espaços nas pontas.
        mes_referencia: mês no formato "AAAA-MM" ou None (todo o histórico).

    Exemplo: FeedbackGerarRequisicao(vendedor_id=" C0031 ", mes_referencia="2026-10")
    """

    # str_strip_whitespace remove espaços do começo e do fim de TODO texto
    # recebido. Assim " C0031 " vira "C0031" antes das outras validações — e
    # um texto só com espaços vira "", que falha no min_length abaixo.
    model_config = ConfigDict(str_strip_whitespace=True)

    vendedor_id: str = Field(
        min_length=1,
        description='Código do vendedor (ex.: "C0031").',
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
        """Aplica a regra do mês na hora de montar o pedido de feedback.

        O @field_validator diz ao Pydantic para chamar este método quando o
        campo "mes_referencia" chegar. A regra em si (regex e mensagem de
        erro) mora em validar_formato_mes_referencia, para os outros
        contratos que aceitam mês usarem exatamente a mesma checagem.
        """
        return validar_formato_mes_referencia(valor)


class FeedbackRoteiroDTO(BaseModel):
    """As quatro listas que formam o roteiro de feedback."""

    pontos_positivos: list[str] = Field(
        default_factory=list,
        description="O que a pessoa faz bem, sempre ligado a um dado real.",
    )
    pontos_melhoria: list[str] = Field(
        default_factory=list,
        description=(
            "O que pode melhorar, no formato Situação-Comportamento-Impacto."
        ),
    )
    possiveis_motivos: list[str] = Field(
        default_factory=list,
        description=(
            "Hipóteses a confirmar com a pessoa; não são fatos."
        ),
    )
    roteiro_conversa: list[str] = Field(
        default_factory=list,
        description="Itens da conversa, com perguntas abertas."
    )


class FeedbackGerarResposta(BaseModel):
    """Resposta da rota que gera o roteiro de feedback."""

    feedback_id: str = Field(
        description="Identificador único do roteiro gerado."
    )
    vendedor_id: str = Field(description="Código da pessoa avaliada.")
    vendedor_nome: str = Field(description="Nome completo da pessoa avaliada.")
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
