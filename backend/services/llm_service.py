"""Serviço de integração com a LLM (DeepSeek) para gerar o roteiro de feedback.

Este é o único lugar do backend que fala com a internet. Ele recebe um
vendedor_id, monta as mensagens com dados já calculados (prompt_feedback) e
pede à IA um JSON com o roteiro. A resposta vira um FeedbackRoteiro; qualquer
falha previsível vira uma exceção de domínio com mensagem em português.

Chave da API: fica só no arquivo backend/.env (não versionado) e nunca é
impressa, registrada ou devolvida em mensagens de erro.
"""

import json
import os

import openai
from dotenv import load_dotenv
from openai import OpenAI

from config import (
    ENV_DEEPSEEK_API_KEY,
    ENV_DEEPSEEK_MODEL,
    ENV_DEEPSEEK_THINKING,
    ENV_FILE,
    LLM_BASE_URL,
    LLM_MAX_TENTATIVAS_SDK,
    LLM_MAX_TOKENS,
    LLM_MODELO_PADRAO,
    LLM_TEMPERATURA,
    LLM_THINKING_PADRAO,
    LLM_TIMEOUT_SEGUNDOS,
)
from domain.excecoes import (
    LLMIndisponivelError,
    LLMNaoConfiguradoError,
    LLMRespostaInvalidaError,
)
from domain.feedback_roteiro import FeedbackRoteiro
from services.data_loader import DataLoader
from services.prompt_feedback import montar_mensagens


class LLMService:
    """Pede à IA um roteiro de feedback e devolve um FeedbackRoteiro.

    Recebe:
        data_loader: serviço que lê os CSVs. Se None, cria um DataLoader
            padrão (útil nos testes, em que se pode passar um dublê).
        client: cliente da API já pronto. Se None, o cliente real da SDK
            openai é criado só na primeira chamada (leitura preguiçosa), para
            não exigir chave nem abrir conexão ao apenas construir o serviço.
        modelo: nome do modelo. Quando None, usa DEEPSEEK_MODEL (se não
            estiver vazio) ou LLM_MODELO_PADRAO.
        thinking: "disabled", "enabled" ou "omitir". Quando None, usa
            DEEPSEEK_THINKING (se não estiver vazio) ou LLM_THINKING_PADRAO.
    """

    def __init__(
        self,
        data_loader: DataLoader | None = None,
        client=None,
        modelo: str | None = None,
        thinking: str | None = None,
    ):
        """Guarda as dependências; nada de rede é feito aqui."""
        # Se nenhum DataLoader foi passado, usamos o padrão (CSVs reais).
        self._data_loader = data_loader if data_loader is not None else DataLoader()
        self._client = client
        self._modelo = modelo
        self._thinking = thinking

    def _obter_cliente(self):
        """Cria (uma única vez) o cliente real da API, lendo a chave do .env.

        Cliente de API: objeto que sabe montar a requisição HTTP e interpretar
        a resposta do provedor. A criação é preguiçosa porque construir o
        serviço não deve exigir chave nem internet.

        Levanta LLMNaoConfiguradoError quando a chave não existe ou está vazia.
        """
        # Já temos um cliente (real ou fake)? Então reaproveitamos.
        if self._client is not None:
            return self._client

        # load_dotenv lê o arquivo .env e coloca os valores em variáveis de
        # ambiente. Se o arquivo não existir, nada acontece e não há erro.
        load_dotenv(dotenv_path=ENV_FILE)

        # A chave nunca vai para mensagem de erro: só verificamos se há texto.
        chave = os.environ.get(ENV_DEEPSEEK_API_KEY, "").strip()
        if not chave:
            raise LLMNaoConfiguradoError(
                "A chave da API da DeepSeek não está configurada. Copie "
                "backend/.env.example para backend/.env e preencha "
                "DEEPSEEK_API_KEY antes de gerar o feedback."
            )

        # max_retries: quantos reenvios automáticos a SDK pode fazer.
        # timeout: tempo máximo de espera por uma resposta.
        self._client = OpenAI(
            api_key=chave,
            base_url=LLM_BASE_URL,
            timeout=LLM_TIMEOUT_SEGUNDOS,
            max_retries=LLM_MAX_TENTATIVAS_SDK,
        )
        return self._client

    def _modelo_efetivo(self) -> str:
        """Decide qual modelo usar: argumento > .env > padrão do config."""
        if self._modelo:
            return self._modelo

        # Variável de ambiente é lida na hora da chamada (e não no construtor)
        # para que o .env carregado depois também seja considerado.
        modelo_env = os.environ.get(ENV_DEEPSEEK_MODEL, "").strip()
        if modelo_env:
            return modelo_env
        return LLM_MODELO_PADRAO

    def _thinking_efetivo(self) -> str:
        """Decide o modo de thinking: argumento > .env > padrão do config."""
        if self._thinking:
            return self._thinking

        thinking_env = os.environ.get(ENV_DEEPSEEK_THINKING, "").strip()
        if thinking_env:
            return thinking_env
        return LLM_THINKING_PADRAO

    @staticmethod
    def _remover_cercas_markdown(texto: str) -> str:
        """Remove cercas de código (```json ... ```) em volta do JSON.

        Mesmo pedindo JSON puro, alguns modelos envolvem a resposta em cercas
        de markdown. Removemos a primeira e a última linha quando são cercas.
        """
        linhas = texto.splitlines()

        if linhas and linhas[0].strip().startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip().startswith("```"):
            linhas = linhas[:-1]

        return "\n".join(linhas).strip()

    @classmethod
    def _interpretar_resposta(cls, resposta) -> FeedbackRoteiro:
        """Transforma a resposta da API em FeedbackRoteiro.

        Recebe o objeto devolvido pela SDK (com choices[0].message.content).
        Levanta LLMRespostaInvalidaError quando a resposta foi cortada, veio
        vazia, não é JSON ou não tem o formato esperado.
        """
        # choices é a lista de respostas geradas; usamos a primeira.
        if not resposta.choices:
            raise LLMRespostaInvalidaError(
                "A IA não devolveu nenhuma resposta."
            )

        escolha = resposta.choices[0]

        # finish_reason "length" significa que o limite de tokens acabou e a
        # resposta foi cortada no meio; o JSON certamente está incompleto.
        if escolha.finish_reason == "length":
            raise LLMRespostaInvalidaError(
                "A resposta da IA foi cortada por limite de tamanho. "
                "Aumente LLM_MAX_TOKENS e tente de novo."
            )

        conteudo = escolha.message.content

        # O modo JSON da API às vezes devolve conteúdo vazio; tratamos como
        # resposta inválida para o gerente não receber um roteiro em branco.
        if conteudo is None or not conteudo.strip():
            raise LLMRespostaInvalidaError(
                "A IA devolveu uma resposta vazia. Tente gerar o roteiro "
                "novamente."
            )

        texto = cls._remover_cercas_markdown(conteudo.strip())

        try:
            dados = json.loads(texto)
        except (json.JSONDecodeError, TypeError) as erro:
            # Mostramos no máximo os primeiros 200 caracteres da resposta:
            # o suficiente para diagnosticar sem despejar o texto inteiro.
            trecho = texto[:200]
            raise LLMRespostaInvalidaError(
                "A IA não devolveu um JSON válido. "
                f"Início da resposta: {trecho!r}"
            ) from erro

        if not isinstance(dados, dict):
            raise LLMRespostaInvalidaError(
                "A resposta da IA não é um objeto JSON (esperado algo como "
                "{...}, com as quatro listas do roteiro)."
            )

        try:
            # FeedbackRoteiro.de_dict aceita chaves ausentes (viram listas
            # vazias). A checagem de qualidade do conteúdo será feita numa
            # próxima fatia; aqui garantimos apenas o formato.
            return FeedbackRoteiro.de_dict(dados)
        except ValueError as erro:
            raise LLMRespostaInvalidaError(
                f"A resposta da IA não tem o formato esperado: {erro}"
            ) from erro

    def gerar_roteiro_feedback(
        self, vendedor_id: str, mes_referencia: str | None = None
    ) -> FeedbackRoteiro:
        """Gera o roteiro de feedback de um vendedor com a IA.

        Recebe o código do vendedor ("C0031") e, opcionalmente, o mês de
        referência ("AAAA-MM"; None = todo o histórico).

        Devolve um FeedbackRoteiro com as quatro listas de textos.

        Levanta VendedorNaoEncontradoError se o vendedor não existir,
        LLMNaoConfiguradoError se a chave faltar ou for recusada,
        LLMIndisponivelError em falhas externas e LLMRespostaInvalidaError
        quando a resposta não serve.
        """
        # 1) Busca os dados já calculados. Se o vendedor não existir, a
        # exceção sobe daqui sem chamar a API (economiza tempo e dinheiro).
        vendedor = self._data_loader.obter_vendedor(vendedor_id)
        comparativo = self._data_loader.obter_comparativo_time(
            vendedor_id, mes_referencia
        )
        anotacoes = self._data_loader.obter_anotacoes_do_vendedor(vendedor_id)
        gerente = self._data_loader.obter_gerente()
        anotacoes_do_time = gerente.anotacoes_do_time()

        # 2) Monta as duas mensagens (sistema e usuário) sem tocar em rede.
        mensagens = montar_mensagens(
            vendedor=vendedor,
            comparativo=comparativo,
            anotacoes_do_vendedor=anotacoes,
            anotacoes_do_time=anotacoes_do_time,
            gerente_nome=gerente.nome,
            loja_nome=gerente.loja_nome,
            mes_referencia=mes_referencia,
        )

        modelo = self._modelo_efetivo()
        thinking = self._thinking_efetivo()

        # Parâmetros pedidos à API. response_format "json_object" é o "modo
        # JSON": o provedor se compromete a devolver um JSON válido.
        parametros = {
            "model": modelo,
            "messages": mensagens,
            "response_format": {"type": "json_object"},
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURA,
        }

        # O thinking ("raciocínio interno") vai em extra_body porque é um
        # parâmetro específico do provedor, fora do padrão da SDK.
        # Com thinking ligado, a temperatura não faz efeito; mantemos o valor
        # por simplicidade e documentamos isso aqui.
        # "omitir" não envia o parâmetro e deixa o padrão do provedor.
        if thinking != "omitir":
            parametros["extra_body"] = {"thinking": {"type": thinking}}

        cliente = self._obter_cliente()

        # A ordem dos except importa: as subclasses precisam vir antes das
        # classes pai, senão o erro específico seria capturado pelo genérico.
        # Exemplo: APITimeoutError é filha de APIConnectionError, e
        # RateLimitError é filha de APIStatusError.
        try:
            resposta = cliente.chat.completions.create(**parametros)
        except openai.AuthenticationError as erro:
            # 401: chave inválida ou recusada.
            raise LLMNaoConfiguradoError(
                "A chave da API foi recusada pelo provedor. Confira "
                "DEEPSEEK_API_KEY em backend/.env."
            ) from erro
        except openai.PermissionDeniedError as erro:
            # 403: a chave existe, mas não tem permissão para esta operação.
            raise LLMNaoConfiguradoError(
                "O provedor negou permissão para usar esta chave. Confira "
                "se ela está ativa e correta em backend/.env."
            ) from erro
        except openai.APITimeoutError as erro:
            # Tempo máximo de espera esgotado (vem antes de
            # APIConnectionError, porque é uma subclasse dela).
            raise LLMIndisponivelError(
                "O tempo de espera da IA esgotou. Tente de novo em instantes."
            ) from erro
        except openai.APIConnectionError as erro:
            # Sem conexão com a internet ou provedor fora do ar.
            raise LLMIndisponivelError(
                "Não foi possível conectar ao provedor da IA. Verifique a "
                "conexão e tente de novo."
            ) from erro
        except openai.RateLimitError as erro:
            # 429: limite de uso atingido (vem antes de APIStatusError).
            raise LLMIndisponivelError(
                "Limite de uso da IA atingido. Aguarde um pouco e tente de "
                "novo."
            ) from erro
        except openai.APIStatusError as erro:
            # Demais respostas de erro com status HTTP (402, 5xx, 400, 422...).
            status = erro.status_code

            if status == 402:
                raise LLMIndisponivelError(
                    "Saldo insuficiente no provedor da IA. Confira a conta "
                    "antes de tentar de novo."
                ) from erro
            if 500 <= status <= 599:
                raise LLMIndisponivelError(
                    f"O servidor do provedor da IA falhou (status {status}). "
                    "Tente de novo mais tarde."
                ) from erro
            if status in (400, 422):
                raise LLMIndisponivelError(
                    f"O provedor recusou a requisição (status {status}). "
                    "Confira DEEPSEEK_MODEL e DEEPSEEK_THINKING: o nome do "
                    "modelo ou o modo de thinking pode estar errado."
                ) from erro

            raise LLMIndisponivelError(
                f"O provedor da IA recusou a requisição (status {status})."
            ) from erro
        except openai.OpenAIError as erro:
            # Último recurso: qualquer outro erro da SDK vira indisponibilidade,
            # sempre preservando a causa original com "from erro".
            raise LLMIndisponivelError(
                "Falha inesperada na integração com a IA. Tente de novo mais "
                "tarde."
            ) from erro

        # 5) Converte a resposta em objeto de domínio.
        return self._interpretar_resposta(resposta)
