"""Servidor FastAPI mínimo do FullStore Feedback Inteligente."""

from dotenv import load_dotenv
from fastapi import FastAPI

# Carrega as variáveis do .env quando o arquivo existir; a ausência dele não é erro.
load_dotenv()

app = FastAPI(title="FullStore Feedback Inteligente")


@app.get("/health")
def health() -> dict[str, str]:
    """Confirma que o servidor está no ar."""
    return {"status": "ok"}
