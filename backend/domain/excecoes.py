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
