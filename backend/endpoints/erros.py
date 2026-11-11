"""Tratamento global de erros da API.

Handler (tratador de exceção): função que o FastAPI chama quando um erro
acontece durante um pedido. Em vez de deixar o erro virar uma página técnica,
o tratador devolve sempre o mesmo corpo JSON: {"erro": "mensagem em português"}.

Status HTTP: o número que acompanha a resposta e diz o que aconteceu, por
exemplo 200 (ok), 400 (pedido inválido), 404 (não encontrado), 502 (o serviço
de IA respondeu algo inválido), 503 (serviço temporariamente indisponível) e
500 (erro interno do servidor).

Tabela exceção -> status:
| Exceção                                  | Status | Mensagem                          |
|------------------------------------------|--------|-----------------------------------|
| VendedorNaoEncontradoError               | 404    | a mensagem da própria exceção     |
| LojaNaoEncontradaError                   | 404    | a mensagem da própria exceção     |
| RequestValidationError                   | 400    | resumo legível de campo/problema  |
| LLMIndisponivelError                     | 503    | a mensagem da própria exceção     |
| LLMRespostaInvalidaError                 | 502    | a mensagem da própria exceção     |
| LLMNaoConfiguradoError                   | 500    | texto fixo (sem chave nem caminho)|
| DadosIndisponiveisError                  | 500    | texto fixo (sem caminho de arquivo)|
| DominioError (qualquer outro)            | 500    | texto fixo                        |
| HTTPException (ex.: 404 de rota, 405)    | mesmo  | texto em português                |
| Exception (qualquer erro inesperado)     | 500    | "Erro interno do servidor."       |
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from domain.excecoes import (
    DadosIndisponiveisError,
    DominioError,
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
    LojaNaoEncontradaError,
    VendedorNaoEncontradoError,
)

# Logger: canal de registro do servidor. O que é registrado aqui fica no log
# do servidor (para o time técnico investigar), nunca na resposta ao usuário.
logger = logging.getLogger(__name__)

# Tradução dos tipos de erro mais comuns do Pydantic, que vêm em inglês.
# "missing", por exemplo, significa que o campo obrigatório não foi enviado.
_TRADUCOES_DE_VALIDACAO = {
    "missing": "campo obrigatório",
    "string_too_short": "texto muito curto",
    # Formato que não casa com o molde (pattern), ex.: mês "2026-13".
    "string_pattern_mismatch": "formato inválido",
    "string_type": "deve ser um texto",
    "int_parsing": "deve ser um número inteiro",
    "int_type": "deve ser um número inteiro",
    "bool_parsing": "deve ser verdadeiro ou falso",
    "bool_type": "deve ser verdadeiro ou falso",
}

# Mensagens em português para os erros HTTP mais comuns que o próprio
# Starlette gera (rota que não existe, método errado).
_MENSAGENS_HTTP = {
    404: "Recurso não encontrado.",
    405: "Método não permitido para esta rota.",
}


def _resposta_erro(status: int, mensagem: str) -> JSONResponse:
    """Monta a resposta de erro no formato único {"erro": "..."}.

    Recebe o status HTTP e a mensagem em português. Todos os tratadores usam
    esta função, garantindo que o formato nunca mude.
    """
    return JSONResponse(status_code=status, content={"erro": mensagem})


def _nome_do_campo(loc: tuple) -> str:
    """Transforma a localização técnica do erro num nome legível de campo.

    O Pydantic informa a localização como uma tupla, por exemplo
    ("body", "mes_referencia"). Ignoramos a primeira parte quando ela é só
    a origem do dado (corpo, query, caminho) e mostramos o nome do campo.
    """
    origens = {"body", "query", "path", "header", "cookie"}
    partes = [str(item) for item in loc if str(item) not in origens]
    return ".".join(partes) if partes else "corpo da requisição"


def _limpar_mensagem(mensagem) -> str:
    """Deixa a mensagem do Pydantic legível e em português quando possível.

    O Pydantic prefixa os erros dos nossos validadores com "Value error, ";
    removemos esse prefixo. Se não houver mensagem, usamos um texto genérico.
    """
    texto = str(mensagem or "").removeprefix("Value error, ").strip()
    return texto or "valor inválido"


def _mensagem_de_validacao(exc: RequestValidationError) -> str:
    """Resume os erros de validação em uma frase legível.

    Em vez de devolver a estrutura técnica do Pydantic (loc/input/ctx), monta
    algo como 'mes_referencia: use o formato AAAA-MM'. Mostramos no máximo
    três problemas para a mensagem não ficar enorme.
    """
    partes = []
    for erro in exc.errors()[:3]:
        campo = _nome_do_campo(erro.get("loc", ()))
        tipo = str(erro.get("type", ""))
        # Preferimos a tradução do tipo; se não houver, limpamos a mensagem.
        mensagem = _TRADUCOES_DE_VALIDACAO.get(tipo) or _limpar_mensagem(
            erro.get("msg")
        )
        partes.append(f"{campo}: {mensagem}")

    if not partes:
        return "Dados inválidos na requisição."
    return "; ".join(partes)


async def _tratar_nao_encontrado(
    request: Request, exc: DominioError
) -> JSONResponse:
    """Responde 404 para vendedor ou loja inexistente.

    A mensagem vem da própria exceção (ex.: "Vendedor com ID 'C9999' não
    encontrado."), que é segura: contém só o identificador que o usuário já
    conhece.
    """
    return _resposta_erro(404, str(exc) or "Não encontrado.")


async def _tratar_requisicao_invalida(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Responde 400 quando o corpo/parâmetros do pedido estão inválidos."""
    return _resposta_erro(400, _mensagem_de_validacao(exc))


async def _tratar_llm_indisponivel(
    request: Request, exc: LLMIndisponivelError
) -> JSONResponse:
    """Responde 503 quando a IA está fora do ar, sem conexão ou sem saldo."""
    return _resposta_erro(503, str(exc) or "Serviço de IA indisponível.")


async def _tratar_llm_resposta_invalida(
    request: Request, exc: LLMRespostaInvalidaError
) -> JSONResponse:
    """Responde 502 quando a IA respondeu algo que não serve (JSON inválido)."""
    return _resposta_erro(502, str(exc) or "A IA devolveu uma resposta inválida.")


async def _tratar_llm_nao_configurado(
    request: Request, exc: LLMNaoConfiguradoError
) -> JSONResponse:
    """Responde 500 quando a integração com a IA não está configurada.

    Usamos um texto FIXO de propósito: a mensagem original pode citar o
    caminho do arquivo .env ou a variável da chave, e nada disso deve sair
    numa resposta da API.
    """
    return _resposta_erro(
        500, "O serviço de IA não está configurado no servidor."
    )


async def _tratar_dados_indisponiveis(
    request: Request, exc: DadosIndisponiveisError
) -> JSONResponse:
    """Responde 500 quando os CSVs/registro não podem ser lidos.

    Também usa texto fixo: a mensagem original pode conter o caminho do
    arquivo no servidor, que não interessa (nem deve ser exposto) ao usuário.
    """
    return _resposta_erro(
        500, "Não foi possível carregar os dados necessários."
    )


async def _tratar_erro_de_dominio(
    request: Request, exc: DominioError
) -> JSONResponse:
    """Responde 500 para qualquer outro erro de negócio não mapeado acima."""
    return _resposta_erro(500, "Não foi possível concluir a operação.")


async def _tratar_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Mantém o status do Starlette e traduz a mensagem para português.

    Cobre a rota que não existe (404) e o método errado (405), que o próprio
    framework detecta antes de chamar qualquer rota nossa.
    """
    mensagem = _MENSAGENS_HTTP.get(exc.status_code)

    if mensagem is None:
        # Para os demais status, usamos o detalhe quando ele for um texto;
        # se não for, devolvemos uma mensagem genérica.
        detalhe = exc.detail
        mensagem = str(detalhe) if detalhe else "Erro na requisição."

    return _resposta_erro(exc.status_code, mensagem)


async def _tratar_erro_inesperado(
    request: Request, exc: Exception
) -> JSONResponse:
    """Responde 500 genérico e registra o traceback apenas no log.

    Traceback: a lista de chamadas que levou ao erro, útil para o time
    técnico. Ela vai para o log do servidor; a resposta ao usuário NUNCA
    contém a mensagem original nem detalhes internos.
    """
    logger.error(
        "Erro interno não tratado na API.", exc_info=exc
    )
    return _resposta_erro(500, "Erro interno do servidor.")


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    """Instala todos os tratadores acima no app do FastAPI.

    Recebe o app e registra cada exceção com o tratador correspondente.
    O FastAPI escolhe o tratador pela classe da exceção, procurando da mais
    específica para a mais genérica (LLMNaoConfiguradoError antes de
    DominioError, por exemplo).

    Exemplo: registrar_tratadores_de_erro(app) logo depois de criar o app.
    """
    # 404
    app.add_exception_handler(
        VendedorNaoEncontradoError, _tratar_nao_encontrado
    )
    app.add_exception_handler(
        LojaNaoEncontradaError, _tratar_nao_encontrado
    )

    # 400
    app.add_exception_handler(
        RequestValidationError, _tratar_requisicao_invalida
    )

    # 502 / 503
    app.add_exception_handler(
        LLMIndisponivelError, _tratar_llm_indisponivel
    )
    app.add_exception_handler(
        LLMRespostaInvalidaError, _tratar_llm_resposta_invalida
    )

    # 500 específicos
    app.add_exception_handler(
        LLMNaoConfiguradoError, _tratar_llm_nao_configurado
    )
    app.add_exception_handler(
        DadosIndisponiveisError, _tratar_dados_indisponiveis
    )
    app.add_exception_handler(DominioError, _tratar_erro_de_dominio)

    # Erros HTTP do próprio framework (rota inexistente, método errado).
    app.add_exception_handler(
        StarletteHTTPException, _tratar_http_exception
    )

    # Qualquer outro erro: 500 sem vazar detalhes.
    app.add_exception_handler(Exception, _tratar_erro_inesperado)
