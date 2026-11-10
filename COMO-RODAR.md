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

## Testar a integração com a IA (DeepSeek)

O backend fala com a API da DeepSeek. Preencha o arquivo `backend/.env` (criado
a partir de `backend/.env.example`):

```bash
DEEPSEEK_API_KEY=sua-chave-aqui
# Opcionais (vazio = usa o padrão definido em config.py)
#DEEPSEEK_MODEL=
#DEEPSEEK_THINKING=
```

`DEEPSEEK_THINKING` aceita `disabled`, `enabled` ou `omitir`.

Com o venv ativo e a partir da pasta `backend/`:

```bash
# 1) Só mostra o prompt (não usa rede nem a chave)
python -m scripts.testar_deepseek --mostrar-prompt

# 2) Lista os modelos disponíveis na conta (exige chave)
python -m scripts.testar_deepseek --listar-modelos

# 3) Gera o roteiro de verdade (consome créditos)
python -m scripts.testar_deepseek --vendedor Bianca
```

Para outro mês, acrescente `--mes 2026-10`. Também é possível usar o ID:
`--vendedor C0031`.

Se aparecer "modelo não encontrado" (ou erro 400/422), rode
`--listar-modelos`, copie o id desejado para `DEEPSEEK_MODEL` no `backend/.env`
e tente de novo. Confira a documentação oficial em
[api-docs.deepseek.com](https://api-docs.deepseek.com).

**Atenção:** as opções 2 e 3 fazem chamadas reais e consomem créditos da conta.
A opção 1 é gratuita e serve para revisar o texto enviado.

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
