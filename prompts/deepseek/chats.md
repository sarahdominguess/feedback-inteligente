## 2026-11-08

### Prompt 1
CONTEXTO DO PROJETO (somente leitura, NÃO modifique, crie, apague ou renomeie nenhum arquivo, e não execute comandos que alterem o repositório ou o sistema, como instalar pacotes, criar pastas, rodar git commit/add/checkout).

Vou te passar uma sequência de prompts, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar. Não comece a implementar nada por conta própria.

Tarefa agora:
1. Leia, sem alterar: README.md, BRIEFING.md (seção "Desafio 3 — O feedback que ninguém dá"), AI-AGENTS.md, CLAUDE.md, AGENTS.md, DIARIO.md, .gitignore e dados/desafio-3-feedback/LEIAME.md. Veja também os cabeçalhos dos CSVs em dados/desafio-3-feedback/.
2. Responda apenas com um resumo curto (máx. 15 linhas) do que entendeu e liste dúvidas, se houver. Não escreva código nem crie arquivos.

O que estamos construindo: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um co-piloto que ajuda o gerente Diego (loja L004, Aurora Shopping Centro) a preparar o feedback da vendedora Bianca Rocha com base em indicadores de vendas e nas anotações dele. A gerente regional Patrícia Lemos acompanha, numa visão executiva, se os feedbacks estão sendo feitos.

Stack e arquitetura:
- Backend: Python + FastAPI + Uvicorn + Pandas, SDK `openai` apontando para a API do DeepSeek (base_url https://api.deepseek.com), chave DEEPSEEK_API_KEY via .env (python-dotenv).
- Frontend: React + Vite (JavaScript), Axios para HTTP, lucide-react para ícones.
- Pastas planejadas na raiz do repositório:
  backend/ { data/, domain/, services/, endpoints/, contracts/ }
  frontend/src/ { pages/, components/, services/, context/ }

Convenções que valem para TODOS os prompts seguintes:
- O feedback gerado pela IA deve seguir o padrão SBI (Situação, Comportamento, Impacto) e sugerir perguntas abertas empáticas.
- Separação de responsabilidades: nenhuma regra de cruzamento de dados de vendas e nenhuma chamada à LLM no frontend. O frontend só consome contratos REST do backend.
- Métricas (Ticket Médio = valor vendido ÷ vendas; P.A. = peças ÷ vendas; Conversão = vendas ÷ atendimentos) são calculadas só no backend, agregando os registros históricos dos CSVs.
- Regras do repositório: faça mudanças pequenas e coesas; NÃO faça git commit/push/amend/reset (o commit é feito por mim); nunca coloque chaves/segredos em arquivos versionados (use .env, que já está no .gitignore); não modifique nada em dados/, prompts/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md nem .claude/ a menos que o prompt peça explicitamente.
- Comunicação e comentários de código em português (pt-BR); identificadores de código seguem o idioma já usado no projeto.
- Ao fim de cada prompt, informe: arquivos criados/alterados, comandos de validação executados e o resultado real. Não declare algo validado sem ter executado.

Estado atual: o repositório ainda NÃO tem backend/ nem frontend/. Vamos começar pela "Etapa 0 – Estrutura do repositório e ambiente base", dividida em 4 fatias. Aguarde o primeiro prompt. Confirme só com o resumo e as dúvidas, sem modificar nada.

### Prompt 2
FATIA 0.1 — Estrutura de pastas (Etapa 0)

Objetivo: criar apenas o esqueleto de diretórios do backend e do frontend na raiz do repositório. Nada de código ainda.

Antes de criar, confirme que backend/ e frontend/ não existem. Se existirem, pare e me avise.

Crie esta estrutura (na raiz do repo, sem pasta extra por cima):

backend/
├── data/
├── domain/
├── services/
├── endpoints/
└── contracts/
frontend/   (NÃO crie agora: será gerado pelo Vite na fatia 0.3)

Regras:
- Em backend/domain, backend/services, backend/endpoints e backend/contracts crie um `__init__.py` vazio (para virarem pacotes Python).
- Em backend/data crie um `.gitkeep` vazio (a pasta receberá os CSVs na Etapa 1; NÃO copie CSVs agora).
- Não crie venv, requirements.txt, main.py nem nada fora do que está listado.
- Não altere nenhum arquivo existente.

Validação: rode `find backend -print | sort` (ou equivalente) e mostre a árvore resultante. Confirme com `git status --short` que só aparecem itens novos dentro de backend/.

Não faça commit. Ao final, liste os arquivos criados. Mensagem de commit sugerida para eu usar: "Cria estrutura de pastas do backend".

### Prompt 3
FATIA 0.2 — Ambiente Python e servidor FastAPI mínimo (Etapa 0)

Pré-requisito: a estrutura backend/ da fatia 0.1 existe.

Objetivo: preparar o ambiente virtual, as dependências e um servidor FastAPI mínimo que sobe sem erros.

Tarefas:
1. Crie o ambiente virtual em backend/venv (`python3 -m venv backend/venv`; se python3 não existir, use `python`). O .gitignore já ignora venv/.
2. Crie backend/requirements.txt contendo exatamente estas dependências, uma por linha, sem versões fixadas: fastapi, uvicorn, pandas, openai, python-dotenv.
3. Instale com o pip do venv (`backend/venv/bin/pip install -r backend/requirements.txt`; no Windows `backend\venv\Scripts\pip`).
4. Crie backend/main.py mínimo:
   - `app = FastAPI(title="FullStore Feedback Inteligente")`;
   - carrega variáveis do .env com python-dotenv (`load_dotenv()`), sem exigir que o .env exista;
   - uma única rota `GET /health` retornando `{"status": "ok"}`;
   - NÃO adicione CORS, endpoints de negócio, tratamento global de erros nem leitura de CSV: isso é de etapas futuras.
5. Crie backend/.env.example com as linhas: `DEEPSEEK_API_KEY=` (vazia) e um comentário em português explicando que o arquivo real deve se chamar `.env` e nunca ser commitado. Não crie o `.env` real.

Validação (execute de verdade):
- A partir de backend/, suba `venv/bin/uvicorn main:app --port 8000` em background, chame `curl http://127.0.0.1:8000/health` e confirme `{"status":"ok"}`; confirme também que `http://127.0.0.1:8000/docs` responde 200. Depois encerre o servidor.
- Mostre `git status --short` e confirme que backend/venv NÃO aparece (ignorado).

Não faça commit. Liste arquivos criados e a saída real dos testes. Mensagem de commit sugerida: "Configura ambiente Python e servidor FastAPI mínimo".

### Prompt 4
FATIA 0.3 — Frontend React + Vite (Etapa 0)

Pré-requisito: backend/ existe; frontend/ ainda NÃO existe (se existir, pare e me avise).

Objetivo: gerar a aplicação React com Vite, instalar as dependências e deixar a página inicial limpa, sem erros no console.

Tarefas:
1. Na raiz do repo, gere o projeto: `npm create vite@latest frontend -- --template react` (JavaScript, não TypeScript). Se o assistente interativo perguntar algo, escolha React + JavaScript e não inicie o servidor automaticamente.
2. Dentro de frontend/, rode `npm install` e depois `npm install axios lucide-react`. Não instale outras dependências (sem react-router, sem Tailwind, sem bibliotecas de UI).
3. Crie as pastas vazias em frontend/src/: pages/, components/, services/, context/, cada uma com um `.gitkeep` vazio.
4. Limpe o template padrão do Vite:
   - Reescreva src/App.jsx para renderizar só um título "Feedback Inteligente" e um subtítulo curto "Co-piloto de feedback para a liderança da Rede Aurora".
   - Esvazie/simplifique src/App.css e src/index.css (apenas um reset mínimo: margin 0, font-family do sistema, box-sizing border-box).
   - Remova do template o que ficar sem uso (ex.: src/assets/react.svg, o contador e imports de logos), sem apagar o que o Vite exige (index.html, main.jsx, vite.config.js, package.json).
   - Ajuste o <title> de index.html para "Feedback Inteligente".
5. Não crie services, contexto, páginas nem componentes reais: só as pastas vazias.

Validação (execute de verdade):
- `npm run build` dentro de frontend/ deve terminar sem erros.
- `npm run lint` deve passar, se o script existir no template.
- Suba `npm run dev` em background, confirme que responde em http://localhost:5173 (curl com status 200 e o título no HTML), depois encerre o processo.
- `git status --short` não pode listar node_modules/ nem dist/.

Não faça commit. Liste arquivos criados/removidos e a saída real dos comandos. Mensagem de commit sugerida: "Cria frontend React com Vite e dependências base".

### Prompt 5
FATIA 0.4 — Variável de ambiente do frontend e verificação final da Etapa 0

Pré-requisito: fatias 0.1, 0.2 e 0.3 concluídas.

Objetivo: documentar/preparar a URL da API no frontend e confirmar que backend e frontend sobem juntos, fechando a Etapa 0.

Tarefas:
1. Crie frontend/.env.example com `VITE_API_URL=http://localhost:8000`, mais um comentário em português explicando que o arquivo real é `frontend/.env` (não versionado). Não crie o frontend/.env real e não escreva código que use essa variável ainda (o cliente Axios é da Etapa 4).
2. Verifique o .gitignore da raiz: ele já ignora `.env`, `.env.*` e libera `!.env.example`. Confirme com `git check-ignore -v` que backend/.env.example e frontend/.env.example NÃO são ignorados, e que backend/venv e frontend/node_modules são. Só altere o .gitignore se algo estiver errado (me avise antes).
3. Crie backend/README.md curto e frontend/README.md só se o Vite ainda não gerou um útil; em vez disso, prefira um único bloco de instruções em um novo arquivo `COMO-RODAR.md` na raiz, em português, com: pré-requisitos (Python 3, Node 18+), como criar e ativar o venv e instalar o requirements, como copiar .env.example para .env, como subir o backend (`uvicorn main:app --reload --port 8000` dentro de backend/), como instalar e subir o frontend (`npm install` e `npm run dev` dentro de frontend/), e as URLs esperadas (API em :8000, docs em :8000/docs, frontend em :5173). Não altere o README.md existente.

Validação final da Etapa 0 (execute de verdade e mostre as saídas):
- Backend: sobe na porta 8000, `/health` retorna ok e `/docs` responde 200.
- Frontend: `npm run build` sem erros e `npm run dev` servindo em :5173 com a página limpa.
- Checklist de estrutura: mostre a árvore de backend/ e frontend/src/ (sem venv e node_modules) e confirme que corresponde a: backend/{data,domain,services,endpoints,contracts} e frontend/src/{pages,components,services,context}.
- `git status --short`: confirme que não há segredos, venv, node_modules nem dist para versionar.

Não faça commit. Ao final, diga claramente se a Etapa 0 está concluída ("pronta quando: FastAPI sobe na porta local e Vite serve a página inicial limpa sem erros") e liste qualquer pendência real. Mensagem de commit sugerida: "Documenta variáveis de ambiente e como rodar o projeto". Lembre-me de registrar no DIARIO.md o que decidi e aprendi, sem escrever por mim.
