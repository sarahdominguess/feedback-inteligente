"""Servidor FastAPI mínimo do FullStore Feedback Inteligente.

Este arquivo é o ponto de entrada do backend: é ele que o Uvicorn executa para
colocar a API no ar. Por enquanto expõe só a rota /health, usada para confirmar
que o servidor está funcionando antes das próximas etapas do projeto.
"""

from dotenv import load_dotenv
from fastapi import FastAPI

# Carrega as variáveis do .env quando o arquivo existir; a ausência dele não é erro.
# Variáveis de ambiente: valores guardados fora do código (como a chave
# DEEPSEEK_API_KEY) para não expor segredos no repositório.
load_dotenv()

# FastAPI: biblioteca Python que cria APIs HTTP de forma simples, recebendo e
# devolvendo JSON (um formato de texto usado para trocar dados). Aqui criamos a
# aplicação com o título que aparece na documentação automática em /docs.
app = FastAPI(title="FullStore Feedback Inteligente")


# @app.get("/health") registra uma rota: quando alguém fizer uma requisição GET
# (pedido de leitura) no caminho /health, a função abaixo é executada.
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
