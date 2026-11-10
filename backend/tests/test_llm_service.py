"""Testes do LLMService com um cliente falso (sem internet).

Cliente fake: um objeto de mentira que imita o cliente da SDK openai. Assim os
testes verificam os parâmetros enviados e o tratamento das respostas/erros sem
gastar dinheiro nem depender de rede. As exceções usadas são as reais da SDK,
construídas com requisição/resposta mínimas (a SDK instalada usa httpx2).
"""

import json
import os
import unittest
from unittest.mock import patch

import httpx2
import openai

from config import (
    LLM_BASE_URL,
    LLM_MAX_TENTATIVAS_SDK,
    LLM_MAX_TOKENS,
    LLM_MODELO_PADRAO,
    LLM_TEMPERATURA,
    LLM_TIMEOUT_SEGUNDOS,
)
from domain.excecoes import (
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
    VendedorNaoEncontradoError,
)
from domain.feedback_roteiro import FeedbackRoteiro
from services import llm_service
from services.data_loader import DataLoader
from services.llm_service import LLMService


# JSON de exemplo com o formato e o conteúdo que o validador aprova.
ROTEIRO_JSON = json.dumps(
    {
        "pontos_positivos": [
            "Conversão de 50,5%, a melhor do time, mostra segurança.",
            "Cliente elogiou o atendimento no Google citando seu nome.",
        ],
        "pontos_melhoria": [
            "Na situação do salão, o P.A. de 1,22 ficou abaixo da média; "
            "oferecer uma segunda peça amanhã.",
            "Na venda do vestido, repetir a oferta do cinto no caixa para "
            "elevar o P.A.",
        ],
        "possiveis_motivos": [
            "Pode ser que o ritmo do salão deixe pouco tempo para oferecer "
            "complementos.",
            "Pode ser que falte segurança para sugerir uma segunda peça.",
        ],
        "roteiro_conversa": [
            "Abertura: obrigado por reservar este momento; quero ouvir você.",
            "Reconhecimento: sua conversão de 50,5% é a melhor do time.",
            "Situação: o P.A. ficou em 1,22; como você vê isso?",
            "O que costuma acontecer quando você pensa em oferecer outra peça?",
            "Que apoio você precisaria para testar uma oferta amanhã?",
            "Combinado: amanhã você oferece uma segunda peça e nos falamos "
            "na sexta.",
        ],
    },
    ensure_ascii=False,
)


def roteiro_json_com_sabrina() -> str:
    """Copia o JSON válido e acrescenta um item que cita uma colega.

    Simula a IA quebrando a regra de justiça (comparação por nome) para
    testar a nova tentativa de correção.
    """
    dados = json.loads(ROTEIRO_JSON)
    dados["pontos_positivos"].append(
        "A Sabrina Alves ajudou o time no sábado."
    )
    return json.dumps(dados, ensure_ascii=False)


class FakeMensagem:
    """Imita message.content da SDK."""

    def __init__(self, content):
        self.content = content


class FakeEscolha:
    """Imita choices[0], com a mensagem e o motivo de término."""

    def __init__(self, content, finish_reason="stop"):
        self.message = FakeMensagem(content)
        self.finish_reason = finish_reason


class FakeResposta:
    """Imita a resposta da API, que tem uma lista de escolhas."""

    def __init__(self, content, finish_reason="stop"):
        self.choices = [FakeEscolha(content, finish_reason)]


class FakeCompletions:
    """Imita chat.completions.create e guarda os parâmetros recebidos."""

    def __init__(self, resposta=None, respostas=None, erro=None):
        self.resposta = resposta
        # respostas: fila de respostas diferentes para chamadas seguidas.
        self.respostas = list(respostas) if respostas is not None else []
        self.erro = erro
        self.chamadas = []

    def create(self, **kwargs):
        """Registra a chamada e devolve a resposta (ou levanta o erro)."""
        self.chamadas.append(kwargs)
        if self.erro is not None:
            raise self.erro
        # Se há uma fila, cada chamada consome a próxima resposta. Quando a
        # fila acaba, repete a resposta padrão (se existir).
        if self.respostas:
            return self.respostas.pop(0)
        return self.resposta


class FakeChat:
    """Imita client.chat, que contém o recurso completions."""

    def __init__(self, completions):
        self.completions = completions


class FakeClient:
    """Imita o cliente da SDK: client.chat.completions.create(...)."""

    def __init__(self, completions):
        self.chat = FakeChat(completions)


def resposta_http(status: int) -> httpx2.Response:
    """Cria uma resposta HTTP mínima, só para montar os erros da SDK.

    Nada é enviado pela rede: Request/Response são apenas objetos de dados.
    """
    requisicao = httpx2.Request(
        "POST", "https://api.deepseek.com/chat/completions"
    )
    return httpx2.Response(
        status,
        request=requisicao,
        json={"error": {"message": "detalhe fictício"}},
    )


def requisicao_http() -> httpx2.Request:
    """Cria uma requisição mínima para os erros de conexão e tempo esgotado."""
    return httpx2.Request(
        "POST", "https://api.deepseek.com/chat/completions"
    )


def casos_de_erro_da_sdk():
    """Monta a tabela de erros da SDK e a exceção de domínio esperada.

    Cada item: (nome, erro da SDK, classe esperada, trecho da mensagem).
    """
    return [
        (
            "autenticacao",
            openai.AuthenticationError(
                "401", response=resposta_http(401), body={}
            ),
            LLMNaoConfiguradoError,
            "recusada",
        ),
        (
            "permissao",
            openai.PermissionDeniedError(
                "403", response=resposta_http(403), body={}
            ),
            LLMNaoConfiguradoError,
            "permissão",
        ),
        (
            "timeout",
            openai.APITimeoutError(request=requisicao_http()),
            LLMIndisponivelError,
            "tempo de espera",
        ),
        (
            "conexao",
            openai.APIConnectionError(request=requisicao_http()),
            LLMIndisponivelError,
            "conectar",
        ),
        (
            "limite",
            openai.RateLimitError("429", response=resposta_http(429), body={}),
            LLMIndisponivelError,
            "Limite de uso",
        ),
        (
            "saldo",
            openai.APIStatusError(
                "402", response=resposta_http(402), body={}
            ),
            LLMIndisponivelError,
            "Saldo insuficiente",
        ),
        (
            "servidor",
            openai.APIStatusError(
                "500", response=resposta_http(500), body={}
            ),
            LLMIndisponivelError,
            "status 500",
        ),
        (
            "requisicao_400",
            openai.BadRequestError(
                "400", response=resposta_http(400), body={}
            ),
            LLMIndisponivelError,
            "DEEPSEEK_MODEL",
        ),
        (
            "requisicao_422",
            openai.UnprocessableEntityError(
                "422", response=resposta_http(422), body={}
            ),
            LLMIndisponivelError,
            "status 422",
        ),
        (
            "generico",
            openai.OpenAIError("falha fictícia"),
            LLMIndisponivelError,
            "inesperada",
        ),
    ]


class TestLLMService(unittest.TestCase):
    """Testa o caminho feliz, os parâmetros enviados e a leitura da resposta."""

    def setUp(self):
        """Prepara um ambiente limpo e o DataLoader real (CSVs do desafio).

        As variáveis DEEPSEEK_MODEL e DEEPSEEK_THINKING são esvaziadas para o
        teste não depender da configuração da máquina.
        """
        ambiente = patch.dict(
            os.environ,
            {"DEEPSEEK_MODEL": "", "DEEPSEEK_THINKING": ""},
        )
        ambiente.start()
        self.addCleanup(ambiente.stop)

        self.loader = DataLoader()

    def criar_servico(
        self, resposta=None, respostas=None, erro=None, **kwargs
    ):
        """Cria o serviço com um FakeClient e devolve (serviço, completions).

        resposta vale para todas as chamadas; respostas é uma fila usada
        para simular a primeira tentativa reprovada e a segunda corrigida.
        """
        completions = FakeCompletions(
            resposta=resposta, respostas=respostas, erro=erro
        )
        client = FakeClient(completions)
        servico = LLMService(
            data_loader=self.loader, client=client, **kwargs
        )
        return servico, completions

    def test_caminho_feliz_vira_feedback_roteiro(self):
        """JSON válido vira FeedbackRoteiro com as quatro listas preenchidas."""
        servico, _ = self.criar_servico(resposta=FakeResposta(ROTEIRO_JSON))

        roteiro = servico.gerar_roteiro_feedback("C0031")

        self.assertIsInstance(roteiro, FeedbackRoteiro)

        esperado = json.loads(ROTEIRO_JSON)
        self.assertEqual(
            roteiro.pontos_positivos, esperado["pontos_positivos"]
        )
        self.assertEqual(
            roteiro.pontos_melhoria, esperado["pontos_melhoria"]
        )
        self.assertEqual(
            roteiro.possiveis_motivos, esperado["possiveis_motivos"]
        )
        self.assertEqual(
            roteiro.roteiro_conversa, esperado["roteiro_conversa"]
        )

    def test_parametros_enviados(self):
        """A chamada leva modelo, modo JSON, limites e thinking desligado."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON)
        )

        servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(len(completions.chamadas), 1)
        chamada = completions.chamadas[0]
        self.assertEqual(chamada["model"], LLM_MODELO_PADRAO)
        self.assertEqual(chamada["response_format"], {"type": "json_object"})
        self.assertEqual(chamada["max_tokens"], LLM_MAX_TOKENS)
        self.assertEqual(chamada["temperature"], LLM_TEMPERATURA)
        self.assertEqual(
            chamada["extra_body"], {"thinking": {"type": "disabled"}}
        )
        self.assertEqual(
            [mensagem["role"] for mensagem in chamada["messages"]],
            ["system", "user"],
        )

    def test_thinking_omitir_nao_envia_extra_body(self):
        """Com thinking "omitir", o parâmetro extra_body nem aparece."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON), thinking="omitir"
        )

        servico.gerar_roteiro_feedback("C0031")

        self.assertNotIn("extra_body", completions.chamadas[0])

    def test_modelo_do_argumento_tem_prioridade(self):
        """O modelo passado no construtor vence o padrão."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON), modelo="modelo-de-teste"
        )

        servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(completions.chamadas[0]["model"], "modelo-de-teste")

    def test_modelo_e_thinking_do_ambiente(self):
        """Sem argumento, valem as variáveis de ambiente quando preenchidas."""
        with patch.dict(
            os.environ,
            {"DEEPSEEK_MODEL": "modelo-do-env", "DEEPSEEK_THINKING": "enabled"},
        ):
            servico, completions = self.criar_servico(
                resposta=FakeResposta(ROTEIRO_JSON)
            )
            servico.gerar_roteiro_feedback("C0031")

        chamada = completions.chamadas[0]
        self.assertEqual(chamada["model"], "modelo-do-env")
        self.assertEqual(
            chamada["extra_body"], {"thinking": {"type": "enabled"}}
        )

    def test_json_dentro_de_cerca_markdown(self):
        """Cercas ```json ... ``` são removidas antes da leitura do JSON."""
        conteudo = f"```json\n{ROTEIRO_JSON}\n```"
        servico, _ = self.criar_servico(resposta=FakeResposta(conteudo))

        roteiro = servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(len(roteiro.pontos_positivos), 2)

    def test_conteudo_vazio(self):
        """Conteúdo None ou só espaços vira LLMRespostaInvalidaError."""
        for conteudo in (None, "   "):
            with self.subTest(conteudo=conteudo):
                servico, _ = self.criar_servico(
                    resposta=FakeResposta(conteudo)
                )
                with self.assertRaises(LLMRespostaInvalidaError):
                    servico.gerar_roteiro_feedback("C0031")

    def test_json_invalido(self):
        """Texto que não é JSON vira LLMRespostaInvalidaError."""
        servico, _ = self.criar_servico(
            resposta=FakeResposta("isto não é json")
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback("C0031")

        self.assertIn("JSON válido", str(contexto.exception))

    def test_json_que_e_lista(self):
        """Um JSON válido, mas que não é objeto, também é recusado."""
        servico, _ = self.criar_servico(resposta=FakeResposta("[]"))

        with self.assertRaises(LLMRespostaInvalidaError):
            servico.gerar_roteiro_feedback("C0031")

    def test_chaves_faltando_disparam_nova_tentativa_e_erro(self):
        """JSON sem as listas agora é reprovado e tenta correção uma vez.

        Antes da validação de qualidade, "{}" virava um roteiro com listas
        vazias. Agora o validador reprova as listas vazias; como a segunda
        resposta é igual, o serviço levanta LLMRespostaInvalidaError após
        exatamente duas chamadas.
        """
        servico, completions = self.criar_servico(
            resposta=FakeResposta("{}")
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(len(completions.chamadas), 2)
        self.assertIn("pontos_positivos", str(contexto.exception))

    def test_resposta_valida_aprova_com_uma_chamada(self):
        """Roteiro aprovado na primeira tentativa não gera segunda chamada."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON)
        )

        servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(len(completions.chamadas), 1)

    def test_resposta_com_colega_e_corrigida_na_segunda(self):
        """1ª cita "Sabrina"; a 2ª corrigida é aprovada, com 2 chamadas."""
        servico, completions = self.criar_servico(
            respostas=[
                FakeResposta(roteiro_json_com_sabrina()),
                FakeResposta(ROTEIRO_JSON),
            ]
        )

        roteiro = servico.gerar_roteiro_feedback("C0031")

        self.assertIsInstance(roteiro, FeedbackRoteiro)
        self.assertEqual(len(completions.chamadas), 2)

        # A segunda chamada reenvia: mensagens originais + resposta anterior
        # (assistant) + pedido de correção (user) com a lista de problemas.
        mensagens = completions.chamadas[1]["messages"]
        self.assertEqual(
            [mensagem["role"] for mensagem in mensagens],
            ["system", "user", "assistant", "user"],
        )
        correcao = mensagens[-1]["content"]
        self.assertIn("Sabrina", correcao)
        self.assertIn("reprovado", correcao)

    def test_duas_respostas_reprovadas_geram_erro(self):
        """Se as duas tentativas citam a colega, o erro lista o problema."""
        servico, completions = self.criar_servico(
            respostas=[
                FakeResposta(roteiro_json_com_sabrina()),
                FakeResposta(roteiro_json_com_sabrina()),
            ]
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(len(completions.chamadas), 2)
        self.assertIn("Sabrina", str(contexto.exception))
        self.assertIn("duas tentativas", str(contexto.exception))

    def test_segunda_resposta_invalida_gera_erro(self):
        """Se a correção não for JSON, o erro também aparece após 2 chamadas."""
        servico, completions = self.criar_servico(
            respostas=[
                FakeResposta(roteiro_json_com_sabrina()),
                FakeResposta("isto não é json"),
            ]
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback("C0031")

        self.assertEqual(len(completions.chamadas), 2)
        self.assertIn("segunda resposta", str(contexto.exception))

    def test_resposta_cortada_por_tamanho(self):
        """finish_reason "length" indica corte e vira resposta inválida."""
        servico, _ = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON, finish_reason="length")
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback("C0031")

        self.assertIn("cortada", str(contexto.exception))

    def test_vendedor_inexistente_nao_chama_a_api(self):
        """Vendedor inexistente sobe o erro de domínio antes de qualquer rede."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON)
        )

        with self.assertRaises(VendedorNaoEncontradoError):
            servico.gerar_roteiro_feedback("C9999")

        self.assertEqual(completions.chamadas, [])


class TestMapeamentoDeErros(unittest.TestCase):
    """Confere que cada erro da SDK vira a exceção de domínio correta."""

    def setUp(self):
        """Usa o DataLoader real e limpa as variáveis de modelo/thinking."""
        ambiente = patch.dict(
            os.environ,
            {"DEEPSEEK_MODEL": "", "DEEPSEEK_THINKING": ""},
        )
        ambiente.start()
        self.addCleanup(ambiente.stop)
        self.loader = DataLoader()

    def test_cada_erro_da_sdk(self):
        """Percorre a tabela de erros e verifica classe e mensagem."""
        for nome, erro, classe_esperada, trecho in casos_de_erro_da_sdk():
            with self.subTest(caso=nome):
                completions = FakeCompletions(erro=erro)
                servico = LLMService(
                    data_loader=self.loader,
                    client=FakeClient(completions),
                )

                with self.assertRaises(classe_esperada) as contexto:
                    servico.gerar_roteiro_feedback("C0031")

                self.assertIn(trecho, str(contexto.exception))
                # A causa original é preservada com "raise ... from erro".
                self.assertIs(contexto.exception.__cause__, erro)


class TestConfiguracaoELazy(unittest.TestCase):
    """Testa a criação preguiçosa do cliente e a falta da chave."""

    def test_cliente_e_criado_so_na_primeira_chamada(self):
        """Construir o serviço não cria cliente; gerar cria, uma única vez."""
        chamadas_do_construtor = []

        class OpenAIFalso:
            """Substitui a classe OpenAI para capturar os argumentos."""

            def __init__(self, **kwargs):
                chamadas_do_construtor.append(kwargs)
                self.chat = FakeChat(FakeCompletions(FakeResposta(ROTEIRO_JSON)))

        with patch.object(llm_service, "OpenAI", OpenAIFalso):
            with patch.object(
                llm_service, "ENV_FILE", llm_service.ENV_FILE.parent / ".env.inexistente"
            ):
                with patch.dict(
                    os.environ,
                    {"DEEPSEEK_API_KEY": "valor-de-teste-nao-e-segredo"},
                ):
                    servico = LLMService(data_loader=DataLoader())

                    # Ainda não criou nada: construção é preguiçosa.
                    self.assertEqual(chamadas_do_construtor, [])

                    roteiro = servico.gerar_roteiro_feedback("C0031")

        self.assertIsInstance(roteiro, FeedbackRoteiro)
        self.assertEqual(len(chamadas_do_construtor), 1)
        argumentos = chamadas_do_construtor[0]
        self.assertEqual(argumentos["api_key"], "valor-de-teste-nao-e-segredo")
        self.assertEqual(argumentos["base_url"], LLM_BASE_URL)
        self.assertEqual(argumentos["timeout"], LLM_TIMEOUT_SEGUNDOS)
        self.assertEqual(argumentos["max_retries"], LLM_MAX_TENTATIVAS_SDK)

    def test_chave_ausente(self):
        """Sem chave no ambiente e com .env inexistente, o erro é claro."""
        with patch.object(
            llm_service, "ENV_FILE", llm_service.ENV_FILE.parent / ".env.inexistente"
        ):
            with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}):
                servico = LLMService(data_loader=DataLoader())

                with self.assertRaises(LLMNaoConfiguradoError) as contexto:
                    servico.gerar_roteiro_feedback("C0031")

        mensagem = str(contexto.exception)
        self.assertIn(".env", mensagem)
        self.assertIn("DEEPSEEK_API_KEY", mensagem)


if __name__ == "__main__":
    unittest.main()
