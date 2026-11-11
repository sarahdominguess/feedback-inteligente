"""Contrato (formato) das respostas de erro da API.

Quando algo dá errado, todas as rotas respondem no mesmo formato:
{"erro": "mensagem em português"}, junto com o código HTTP adequado (404,
422, 503 etc.). Assim o frontend trata qualquer erro de um jeito só.
"""

from pydantic import BaseModel, Field


class ErroResposta(BaseModel):
    """Formato único de erro devolvido pela API.

    Termos:
        Contrato/DTO: o formato exato dos dados que entram e saem da API.
        Pydantic: biblioteca que valida os dados e os converte para JSON.
        BaseModel: a classe "molde" do Pydantic; cada atributo vira um campo
            do JSON de resposta.

    Exemplo: ErroResposta(erro="Vendedor não encontrado.")
    """

    erro: str = Field(
        description=(
            "Mensagem em português, simples, explicando o que deu errado."
        )
    )
