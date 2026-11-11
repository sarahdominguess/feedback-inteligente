"""Ponto de entrada da API do FullStore Feedback Inteligente.

É este arquivo que o Uvicorn executa para colocar o servidor no ar. Aqui
ficam só as configurações gerais: carregamento do .env, CORS, tratamento
global de erros, aquecimento dos dados e a rota /health. As rotas de negócio
entram em módulos próprios (endpoints/) nas próximas partes.
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ENV_FILE, ENV_FRONTEND_ORIGINS, FRONTEND_ORIGINS_PADRAO
from domain.excecoes import DadosIndisponiveisError
from endpoints.dependencias import obter_data_loader
from endpoints.erros import registrar_tratadores_de_erro
from endpoints.vendedores import router as vendedores_router

# Logger: canal de registro do servidor (mensagens técnicas no log, nunca na
# resposta ao usuário).
logger = logging.getLogger(__name__)

# Carrega as variáveis do backend/.env usando o caminho absoluto do config.
# Carregar pelo caminho evita depender da pasta de onde o servidor foi
# iniciado. A ausência do arquivo não é erro: variáveis do sistema também
# valem.
load_dotenv(ENV_FILE)


def ler_origens_permitidas() -> list[str]:
    """Devolve as origens de navegador autorizadas a chamar a API.

    Lê a variável FRONTEND_ORIGINS, que aceita várias origens separadas por
    vírgula. Espaços em volta são removidos e itens vazios são ignorados.

    Quando a variável não existe ou está vazia, devolve o padrão do config
    (o frontend do Vite em http://localhost:5173 e o equivalente em
    127.0.0.1).

    Exemplo: com FRONTEND_ORIGINS="http://localhost:5173, http://x:5173"
    devolve ["http://localhost:5173", "http://x:5173"].
    """
    valor = os.getenv(ENV_FRONTEND_ORIGINS, "")

    origens = [
        origem.strip()
        for origem in valor.split(",")
        if origem.strip()
    ]

    # Sem configuração válida, usa a lista padrão do config.
    if not origens:
        return list(FRONTEND_ORIGINS_PADRAO)
    return origens


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa o aquecimento na subida do servidor e libera na descida.

    Lifespan: o "ciclo de vida" do servidor. O código antes do yield roda
    quando o servidor sobe; o depois, quando ele é encerrado.

    Aquecimento: lemos os CSVs uma vez já na subida. Sem isso, o primeiro
    pedido do gerente pagaria a leitura dos arquivos e pareceria lento. Se a
    leitura falhar, registramos no log e deixamos o servidor subir mesmo
    assim: as rotas responderão com o erro 500 amigável do tratador global,
    em vez de o processo nem iniciar.
    """
    try:
        obter_data_loader().listar_vendedores()
    except DadosIndisponiveisError:
        logger.exception(
            "Não foi possível carregar os CSVs na subida; o servidor vai "
            "subir e as rotas responderão com erro amigável."
        )

    # Tudo o que precisa ser liberado no encerramento entraria depois do
    # yield. Hoje não há nada para liberar.
    yield


app = FastAPI(
    title="FullStore Feedback Inteligente",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: regra do navegador que decide se uma página de um endereço pode ler
# a resposta de outro endereço. Sem liberar a origem do frontend, o navegador
# bloqueia a resposta mesmo que a API tenha respondido.
# - allow_origins: só as origens configuradas (nunca "*").
# - allow_methods/allow_headers: só o que o frontend realmente usa.
# - sem allow_credentials: não usamos cookies nem sessão, então não expomos
#   esse tipo de credencial.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ler_origens_permitidas(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Tratadores globais: todo erro responde {"erro": "..."} com o status certo.
registrar_tratadores_de_erro(app)

# Rotas de negócio. Cada router cuida de um assunto e é incluído aqui.
app.include_router(vendedores_router)

# routers incluídos nas próximas partes (3.6 a 3.7)


@app.get("/health")
def health() -> dict[str, str]:
    """Confirma que o servidor está no ar.

    Recebe: nada.
    Devolve: um dicionário (conjunto de pares chave/valor) com status "ok".

    Exemplo: ao acessar http://localhost:8000/health, a resposta é
    {"status": "ok"}.
    """
    # Se esta linha for executada, o servidor está no ar e pronto para responder.
    return {"status": "ok"}
