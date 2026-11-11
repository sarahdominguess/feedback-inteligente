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

## Usar a API

Com o venv ativo e a partir da pasta `backend/`:

```bash
uvicorn main:app --reload --port 8000
```

A documentação interativa (Swagger) fica em http://localhost:8000/docs: lá dá
para ver cada rota, os campos esperados e testar direto pelo navegador.

O arquivo `backend/api.http` tem um exemplo pronto de cada chamada (abre no VS
Code com a extensão REST Client ou no JetBrains com o HTTP Client). As duas
chamadas de `POST /api/feedback/gerar` usam a DeepSeek de verdade: **consomem
créditos** e podem levar de 10 a 60 segundos. As demais são leves.

| Método | Rota | O que faz |
| --- | --- | --- |
| GET | `/health` | Confirma que o servidor está no ar. |
| GET | `/api/vendedores/{loja_id}` | Lista os vendedores da loja com métricas e comparativo. Aceita `?mes=AAAA-MM`. |
| GET | `/api/vendedores/{vendedor_id}/historico` | Histórico de um vendedor: resumo mensal, anotações e roteiros já preparados. |
| POST | `/api/feedback/gerar` | Gera o roteiro com a IA e grava o registro. Corpo: `vendedor_id` e, opcional, `mes_referencia`. |
| GET | `/api/regional/desempenho-gerente` | Visão da regional: resultado da loja mês a mês, cobertura dos roteiros e anotações. |

Os erros seguem sempre o mesmo formato:

```json
{"erro": "mensagem em português"}
```

| Status | Quando acontece |
| --- | --- |
| 400 | Entrada inválida (ex.: mês fora de `AAAA-MM`, campo obrigatório faltando). |
| 404 | Vendedor ou loja não encontrado. |
| 500 | Erro interno do servidor ou serviço de IA não configurado no servidor. |
| 502 | A IA respondeu algo inválido (JSON quebrado ou fora das regras). |
| 503 | Serviço de IA indisponível (sem conexão, tempo esgotado ou sem saldo). |

Opcionalmente, o `backend/.env` pode liberar outras origens do navegador para o
CORS (o frontend do Vite já é liberado por padrão). Separe por vírgula, sem
espaços:

```bash
#FRONTEND_ORIGINS=http://localhost:5173,http://192.168.0.10:5173
```

O arquivo `backend/data/registro_feedbacks.json` é criado sozinho na primeira
geração, **não é versionado** e guarda os roteiros gerados (id, mês, horário e
conteúdo). Vocabulário importante: **roteiro preparado não é feedback
realizado** — o sistema só sabe que o roteiro foi gerado; se a conversa
aconteceu, é o gerente quem sabe.

## Frontend

Em outro terminal, a partir da raiz do repositório:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

O `frontend/.env` também não é versionado; ele apenas guarda a URL da API.

## Frontend: comunicação com a API

O frontend conversa com a API por um cliente HTTP central; nenhuma tela chama
axios diretamente. Para configurar, a partir da pasta `frontend/`:

```bash
cp .env.example .env
```

O `frontend/.env` guarda só `VITE_API_URL` (padrão `http://localhost:8000`) e
não é versionado.

Ordem para subir tudo:

1. Backend (terminal 1), de dentro de `backend/` com o venv ativo:
   `uvicorn main:app --reload --port 8000`.
2. Frontend (terminal 2), de dentro de `frontend/`: `npm run dev`.
3. Abra http://localhost:5173.

O painel temporário de verificação em http://localhost:5173 mostra a URL da API
em uso, a lista dos 8 vendedores da loja, os detalhes do vendedor selecionado, a
geração de feedback e a visão regional — com valores brutos, porque a
formatação final entra na Etapa 5.

Comandos úteis, de dentro de `frontend/`:

```bash
# testes de lógica (sem rede)
npm test

# confere a API no endereço padrão (NÃO chama a IA)
npm run verificar:api

# além de tudo, gera um roteiro real — CONSOME CRÉDITOS da DeepSeek
npm run verificar:api -- --gerar
```

Se aparecer "Não foi possível conectar ao servidor":
- confirme que o backend está rodando na porta 8000;
- confira `VITE_API_URL` no `frontend/.env` (endereço ou porta errados);
- se o navegador bloquear por CORS, ajuste `FRONTEND_ORIGINS` no
  `backend/.env` (o padrão já libera http://localhost:5173).

## URLs esperadas

| O que | URL |
| --- | --- |
| API | http://localhost:8000 |
| Documentação da API (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

## Observações

- O backend deve estar rodando para o frontend consumir dados nas próximas etapas.
- Nenhum arquivo `.env` real vai para o repositório; só os `.env.example`.
