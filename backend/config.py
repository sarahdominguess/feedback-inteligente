"""Configuração central do backend: caminhos e informações fixas do desafio.

Este arquivo reúne num só lugar onde ficam os arquivos de dados e os dados
fixos da loja (L004). O resto do código importa estas constantes em vez de
repetir caminhos e nomes soltos, o que evita erros de digitação e facilita
mudanças futuras.
"""

from pathlib import Path

# Path: o "molde" (classe) do Python para representar caminhos de arquivos e
# pastas. __file__ é o caminho deste próprio arquivo (config.py). .resolve()
# devolve o caminho absoluto (completo, desde a raiz do disco) e .parent pega a
# pasta que contém o arquivo (backend/). Assim, DATA_DIR aponta sempre para
# backend/data, não importa de qual pasta o projeto seja executado.
DATA_DIR = Path(__file__).resolve().parent / "data"

# Nomes dos arquivos CSV que vivem dentro de DATA_DIR. São só os nomes (sem
# caminho); quem for ler o arquivo junta DATA_DIR + nome.
ARQUIVO_VENDEDORES = "vendedores.csv"
ARQUIVO_INDICADORES_DIARIOS = "indicadores_diarios_vendedor.csv"
ARQUIVO_METAS_VENDEDOR = "metas_vendedor.csv"
ARQUIVO_ANOTACOES_GERENTE = "anotacoes_gerente.csv"

# Arquivos usados pela visão da regional (Etapa 3). Ficam separados dos quatro
# acima porque ainda não são lidos pelo DataLoader: são a base da visão
# executiva, não do feedback individual.
ARQUIVO_ANOTACOES_REGIONAL = "anotacoes_regional.csv"
ARQUIVO_METAS_LOJA = "metas_loja.csv"

# Arquivo local onde ficam registrados os roteiros já gerados (visão da
# regional). Diferente dos CSVs, ele é criado sozinho pelo programa na
# primeira gravação e NÃO vai para o git (é dado de execução, não código).
REGISTRO_FEEDBACKS_ARQUIVO = DATA_DIR / "registro_feedbacks.json"

# Identificação da loja do desafio. O arquivo vendedores.csv não tem coluna de
# loja, então esse dado vem do LEIAME do desafio. Todos os funcionários do CSV
# pertencem a esta loja.
LOJA_ID = "L004"
LOJA_NOME = "Aurora Shopping Centro"

# Texto que aparece na coluna "sobre" das anotações quando o gerente escreve
# sobre o time inteiro, e não sobre uma pessoa específica.
ANOTACAO_SOBRE_TIME = "(time)"

# Abaixo deste número de dias com dados, o mês é tratado como parcial (por
# exemplo, novembro com 1 dia). A regra é usada no prompt enviado à IA e nos
# contratos da API, por isso mora aqui, num lugar só, para não divergir.
DIAS_MINIMOS_MES_COMPLETO = 10


# ---------------------------------------------------------------------------
# Integração com a LLM (DeepSeek) — usada a partir da Etapa 2.
# LLM: "Large Language Model", o modelo de linguagem que gera o texto.
# ---------------------------------------------------------------------------

# Endereço do provedor da IA. A SDK openai conversa com este endereço.
LLM_BASE_URL = "https://api.deepseek.com"

# Nomes das variáveis de ambiente lidas pelo serviço da LLM.
# Variável de ambiente: valor guardado fora do código (no arquivo backend/.env,
# que não é versionado), ideal para segredos como a chave da API.
ENV_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
ENV_DEEPSEEK_MODEL = "DEEPSEEK_MODEL"
ENV_DEEPSEEK_THINKING = "DEEPSEEK_THINKING"

# Modelo usado quando a variável DEEPSEEK_MODEL não estiver definida.
# Atenção: os nomes de modelo da DeepSeek mudam com o tempo. Confira o nome
# atual na documentação oficial ou rode client.models.list() com a sua chave.
LLM_MODELO_PADRAO = "deepseek-flash"

# Tempo máximo de espera (timeout, em segundos) por uma resposta da IA.
LLM_TIMEOUT_SEGUNDOS = 60

# Limite de tokens da resposta. Token: pedacinho de texto que o modelo lê e
# escreve; limitar evita resposta cortada e custo inesperado.
LLM_MAX_TOKENS = 3000

# Temperatura: o quanto a resposta pode variar. Valores baixos deixam o texto
# mais previsível e estável, o que é bom para um roteiro de feedback.
LLM_TEMPERATURA = 0.4

# Quantas vezes a SDK pode reenviar sozinha uma chamada que falhou na rede.
# 1 significa "não reenviar": quem decide tentar de novo é o nosso código.
LLM_MAX_TENTATIVAS_SDK = 1

# "Thinking" é o raciocínio interno de alguns modelos: melhora respostas
# difíceis, mas deixa a chamada mais lenta e cara. Nos modelos V4 ele vem
# ligado por padrão; para esta tarefa desligamos explicitamente.
# Valores aceitos: "disabled" (desligado), "enabled" (ligado) ou "omitir"
# (não enviar o parâmetro e deixar o padrão do provedor).
LLM_THINKING_PADRAO = "disabled"

# Caminho absoluto do arquivo backend/.env, calculado a partir deste arquivo,
# para o carregamento funcionar de qualquer pasta de execução.
ENV_FILE = Path(__file__).resolve().parent / ".env"


# ---------------------------------------------------------------------------
# CORS — quais sites do navegador podem chamar esta API.
# CORS ("Cross-Origin Resource Sharing"): regra do navegador que decide se uma
# página de um endereço pode pedir dados a outro endereço. Sem liberar a
# origem do frontend, o navegador bloqueia a resposta.
# ---------------------------------------------------------------------------

# Nome da variável de ambiente que pode substituir a lista de origens.
# Ela aceita várias origens separadas por vírgula, por exemplo:
# FRONTEND_ORIGINS=http://localhost:5173,http://192.168.0.10:5173
ENV_FRONTEND_ORIGINS = "FRONTEND_ORIGINS"

# Origens liberadas quando a variável não está definida. O Vite (servidor de
# desenvolvimento do frontend React) serve a página na porta 5173; incluímos
# também 127.0.0.1 porque o navegador trata localhost e 127.0.0.1 como
# endereços diferentes.
FRONTEND_ORIGINS_PADRAO = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
