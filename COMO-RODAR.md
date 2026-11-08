# Como rodar o projeto

Instruções para subir o backend (FastAPI) e o frontend (React + Vite) da aplicação
**FullStore Feedback Inteligente** em ambiente local.

## Pré-requisitos

- Python 3.10 ou superior
- Node.js 18 ou superior (com npm)

## Backend

A partir da raiz do repositório:

```bash
python -m venv backend/venv
```

Ative o ambiente virtual:

```bash
# Windows (Git Bash)
source backend/venv/Scripts/activate
# Windows (PowerShell)
backend\venv\Scripts\Activate.ps1
# Linux / macOS
source backend/venv/bin/activate
```

Instale as dependências e crie o arquivo de variáveis de ambiente:

```bash
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Abra `backend/.env` e preencha a `DEEPSEEK_API_KEY`. Esse arquivo contém segredo, não é
versionado e nunca deve ser commitado.

Suba o servidor:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

## Frontend

Em outro terminal, a partir da raiz do repositório:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

O `frontend/.env` também não é versionado; ele apenas guarda a URL da API.

## URLs esperadas

| O que | URL |
| --- | --- |
| API | http://localhost:8000 |
| Documentação da API (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

## Observações

- O backend deve estar rodando para o frontend consumir dados nas próximas etapas.
- Nenhum arquivo `.env` real vai para o repositório; só os `.env.example`.
