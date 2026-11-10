"""Exceções do domínio do FullStore Feedback Inteligente.

Exceção: um tipo especial de erro em Python. Aqui ficam os erros que sabemos
explicar em português e que o restante do backend pode capturar para responder
ao usuário de forma amigável, em vez de mostrar um erro técnico.
"""


class DominioError(Exception):
    """Erro base dos problemas de negócio do nosso domínio.

    Recebe uma mensagem em português explicando o que deu errado.
    As outras exceções deste arquivo herdam dela, então quem capturar
    DominioError também captura os erros mais específicos.

    Exemplo: raise DominioError("Não foi possível preparar o feedback.")
    """


class DadosIndisponiveisError(DominioError):
    """Erro para quando os dados necessários não podem ser usados.

    Acontece, por exemplo, quando um arquivo CSV não existe, quando falta uma
    coluna esperada ou quando o arquivo está ilegível (corrompido).
    """


class VendedorNaoEncontradoError(DominioError):
    """Erro para quando um vendedor não é encontrado de forma única.

    Acontece quando o ID ou o nome informado não existe na base ou quando o
    nome é ambíguo (mais de um vendedor com o mesmo nome).
    """


class LLMNaoConfiguradoError(DominioError):
    """Erro para quando a integração com a IA não está configurada.

    Acontece quando a chave da API (DEEPSEEK_API_KEY) está ausente ou vazia,
    ou quando o provedor recusa a chave enviada (erro de autenticação).
    Sem chave válida não há como pedir o roteiro de feedback à IA.
    """


class LLMIndisponivelError(DominioError):
    """Erro para quando a IA não consegue responder por um problema externo.

    Acontece em falha de conexão, tempo de espera esgotado (timeout), limite
    de uso atingido, saldo insuficiente ou erro no servidor do provedor.
    Em geral é temporário: vale tentar de novo mais tarde.
    """


class LLMRespostaInvalidaError(DominioError):
    """Erro para quando a IA responde, mas a resposta não serve para uso.

    Acontece quando o texto vem vazio, cortado (por falta de tokens), não é
    um JSON válido ou não passou nas validações de qualidade do roteiro.
    """
