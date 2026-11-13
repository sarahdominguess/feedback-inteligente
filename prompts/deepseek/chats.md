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


## 2026-11-09

### Prompt 1
CONTEXTO DO PROJETO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de pip/npm install, criar pastas, git add/commit/checkout etc.).

Vou te passar uma sequência de prompts, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar. Não implemente nada por conta própria.

Tarefa agora:
1. Leia, sem alterar: README.md, BRIEFING.md (seção "Desafio 3 — O feedback que ninguém dá"), AI-AGENTS.md, COMO-RODAR.md, DIARIO.md, .gitignore, dados/desafio-3-feedback/LEIAME.md, backend/main.py, backend/requirements.txt, backend/.env.example, frontend/package.json e frontend/src/App.jsx. Liste a árvore de backend/ e frontend/src/ e veja os cabeçalhos e as primeiras linhas dos CSVs em dados/desafio-3-feedback/.
2. Responda só com um resumo curto (máx. 15 linhas) do que entendeu, do estado atual do código e das dúvidas que tiver. Não escreva código e não crie arquivos.

O que estamos construindo: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um co-piloto que ajuda o gerente Diego Furtado (loja L004, Aurora Shopping Centro) a preparar o feedback da vendedora Bianca Rocha com base em indicadores de vendas e nas anotações dele. A gerente regional Patrícia Lemos acompanha numa visão executiva. A IA (DeepSeek, via SDK openai) será integrada em etapa futura.

Estado atual: a estrutura base já existe e está pronta.
- backend/: FastAPI mínimo (main.py com GET /health), requirements.txt (fastapi, uvicorn, pandas, openai, python-dotenv), pastas data/, domain/, services/, endpoints/, contracts/ (com __init__.py vazios) e .env.example. Ainda NÃO há código de domínio, serviços, CSVs em backend/data/ nem testes.
- frontend/: React + Vite (JavaScript) com axios e lucide-react, pastas pages/, components/, services/ e context/ vazias, página inicial limpa.
Vamos agora fazer a "Etapa 1 – Modelagem do domínio e leitura dos dados (CSV + Pandas)", dividida em 6 fatias.

Convenções que valem para TODOS os prompts seguintes:
- Separação de responsabilidades: nenhuma regra de cruzamento de dados de vendas e nenhuma chamada à LLM no frontend. O frontend só consome contratos REST do backend.
- Métricas calculadas só no backend, agregando os registros históricos dos CSVs: Ticket Médio = valor vendido ÷ vendas; P.A. = peças ÷ vendas; Conversão = vendas ÷ atendimentos. Sempre dividir somas agregadas, nunca tirar média de razões diárias.
- O feedback gerado pela IA (etapas futuras) seguirá o padrão SBI (Situação, Comportamento, Impacto) com perguntas abertas empáticas.
- Imports do backend são absolutos a partir da pasta backend/ (ex.: `from domain.vendedor import Vendedor`), pois o servidor sobe de dentro de backend/.
- Testes com `unittest` da biblioteca padrão (sem dependências novas), em backend/tests/, rodados de dentro de backend/ com o python do venv: `python -m unittest discover -s tests -t .` (no Windows: backend/venv/Scripts/python; no Linux/macOS: backend/venv/bin/python).
- Regras do repositório: mudanças pequenas e coesas; NÃO faça git commit/add/push/amend/reset (o commit é feito por mim); nunca coloque chaves ou segredos em arquivos versionados; não modifique dados/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md, .claude/, nem o frontend, a menos que o prompt peça explicitamente. O registro dos prompts em prompts/ é feito por mim/pela ferramenta: não edite essa pasta.
- Não invente dados nem fatos do repositório; verifique no código e nos CSVs.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: todo código que você escrever (backend, testes e, nas etapas futuras, frontend) deve ser bem comentado, em português (pt-BR) e em linguagem simples, para que qualquer pessoa, mesmo sem conhecer a linguagem, entenda o que acontece em cada parte. Siga estas regras:
  1. Todo arquivo começa com um comentário/docstring de 2 a 4 linhas dizendo, em palavras simples, para que serve o arquivo e como ele se encaixa no projeto.
  2. Toda classe e toda função tem docstring explicando: o que faz, o que recebe, o que devolve e, quando ajudar, um exemplo curto (ex.: "Se a Bianca vendeu 10 vezes e 12 peças, o P.A. é 1,2").
  3. Dentro das funções, comente cada bloco lógico (cada passo) explicando o que está sendo feito e POR QUÊ, não apenas repetindo o código. Evite comentários óbvios linha a linha, como "soma 1 ao contador"; prefira explicar a intenção.
  4. Explique termos técnicos na primeira vez em que aparecerem no arquivo, com palavras do dia a dia (ex.: "dataclass: um molde de objeto que guarda dados", "frozen: depois de criado, o objeto não pode ser alterado", "DataFrame: uma tabela do Pandas", "None: significa 'sem valor'", "NaN: célula vazia no Pandas", "cache: guardar o resultado para não recalcular").
  5. Explique os cálculos de negócio com a fórmula escrita em palavras, como em "Ticket médio = valor vendido ÷ número de vendas".
  6. Nos testes, comente o que cada teste verifica e por que aquele resultado é o esperado.
  7. Comentários devem ser corretos e estar sempre atualizados com o código; se alterar o código, atualize o comentário. Não escreva comentários em inglês, nem jargão sem explicação, nem textos longos demais: frases curtas e diretas.
  8. Não altere código de fatias anteriores só para adicionar comentários, a não ser que o prompt peça.
- Ao fim de cada prompt, informe: arquivos criados/alterados, comandos de validação executados e o resultado REAL. Não declare algo validado sem ter executado.

Aguarde o primeiro prompt. Agora responda só com o resumo e as dúvidas, sem modificar nada.

### Prompt 2
FATIA EXTRA — Comentar o código existente da Etapa 0

Objetivo: apenas adicionar comentários didáticos, SEM mudar nenhum comportamento.

Arquivos: backend/main.py e frontend/src/App.jsx (e frontend/src/main.jsx, se tiver pouco ou nenhum comentário).

Siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto: cabeçalho do arquivo, explicação em linguagem simples de cada trecho (o que é FastAPI, o que faz load_dotenv, o que é a rota /health, o que é um componente React, o que é JSX, por que existe o main.jsx) e termos técnicos explicados. Não altere nenhuma linha de código, só comentários.

Validação: confirme com `git diff` que as únicas mudanças são linhas de comentário; rode `npm run build` no frontend e suba o uvicorn rapidamente para chamar GET /health e confirmar que continua funcionando.

Não faça commit. Mensagem de commit sugerida: "Adiciona comentários didáticos ao código da Etapa 0".

### Prompt 3
FATIA 1.1 — Dados em backend/data e configuração central (Etapa 1)

Objetivo: disponibilizar os CSVs ao backend e centralizar caminhos e constantes da loja. Sem lógica de negócio ainda.

Tarefas:
1. COPIE (não mova; dados/ não pode ser alterado) de dados/desafio-3-feedback/ para backend/data/ exatamente estes 4 arquivos: vendedores.csv, indicadores_diarios_vendedor.csv, metas_vendedor.csv, anotacoes_gerente.csv. Não copie os demais. Mantenha o .gitkeep.
2. Confirme que o .gitignore não ignora esses CSVs (`git check-ignore -v backend/data/*.csv` não deve listar nada).
3. Crie backend/config.py com:
   - DATA_DIR: Path absoluto para a pasta backend/data, calculado a partir de __file__ (funcionar de qualquer diretório de execução);
   - constantes com os nomes dos 4 arquivos;
   - LOJA_ID = "L004" e LOJA_NOME = "Aurora Shopping Centro" (o vendedores.csv não tem coluna de loja; essa informação vem do LEIAME do desafio, e todos os funcionários do arquivo pertencem a essa loja);
   - uma constante com o texto usado para anotações sobre o time inteiro no CSV: "(time)".
4. Crie backend/tests/__init__.py (vazio) e backend/tests/test_config.py com um teste unittest que verifica: DATA_DIR existe, os 4 arquivos existem dentro dele, e LOJA_ID/LOJA_NOME têm os valores acima.

Validação (execute de verdade):
- `diff` (ou comparação de hash) entre cada CSV copiado e o original: devem ser idênticos.
- Rode a suíte de testes de dentro de backend/ e mostre a saída.
- `git status --short` deve listar só: 4 CSVs novos, backend/config.py e backend/tests/.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto em TODO arquivo criado nesta fatia (código e testes): cabeçalho explicando o arquivo, docstring em toda classe e função, comentário em cada passo explicando o porquê, termos técnicos explicados em linguagem simples e fórmulas escritas em palavras. Antes de terminar, releia os arquivos que você criou e confirme que uma pessoa que não conhece Python conseguiria entender o que cada parte faz.

Não faça commit. Mensagem de commit sugerida: "Adiciona CSVs do desafio 3 ao backend e configuração central".

### Prompt 4
FATIA 1.2 — Exceções de domínio e entidades simples (Etapa 1)

Pré-requisito: fatia 1.1 concluída.

Objetivo: criar os blocos básicos do domínio, imutáveis e sem dependência de Pandas.

Crie em backend/domain/:

1. excecoes.py:
   - DominioError(Exception): base para erros tratados do domínio;
   - DadosIndisponiveisError(DominioError): arquivo ausente, coluna faltando ou CSV ilegível;
   - VendedorNaoEncontradoError(DominioError): ID ou nome inexistente ou ambíguo.
   Todas aceitam mensagem em português. (As exceções de LLM virão numa etapa futura.)

2. indicador_diario.py: `IndicadorDiario`, dataclass(frozen=True) com: data (datetime.date), vendedor_id (str), valor_vendido (float), vendas (int), pecas (int), atendimentos (int). Valide no __post_init__ que valor, vendas, pecas e atendimentos não são negativos (ValueError em português). NÃO exija vendas <= atendimentos nem pecas >= vendas sem antes checar nos dados reais; se checar e os dados respeitarem, pode documentar, mas não valide além do pedido.

3. anotacao.py: `Anotacao`, dataclass(frozen=True) com: data (date), sobre (str, nome da pessoa ou "(time)"), texto (str). Propriedade `e_do_time` que retorna True quando `sobre` é igual à constante de config para "(time)".

4. feedback_roteiro.py: `FeedbackRoteiro`, dataclass com 4 listas de str: pontos_positivos, pontos_melhoria, possiveis_motivos, roteiro_conversa (default lista vazia via field(default_factory=list)). Método `para_dict()` devolvendo um dict com essas 4 chaves (cópias das listas) e `@classmethod de_dict(cls, dados)` que ignora chaves extras e aceita chaves ausentes (vira lista vazia), lançando ValueError se algum valor não for lista de strings. Essa classe será usada pela integração com a LLM na etapa seguinte; por ora só estrutura.

5. backend/tests/test_entidades.py com testes unittest: criação válida de IndicadorDiario; erro com valores negativos; imutabilidade (tentar alterar atributo levanta FrozenInstanceError); Anotacao.e_do_time para "(time)" e para um nome; FeedbackRoteiro ida e volta (para_dict/de_dict), chaves ausentes e valor inválido.

Não leia CSVs aqui e não crie Vendedor/Gerente (próximas fatias).

Validação: rode a suíte completa a partir de backend/ e mostre a saída real.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto em TODO arquivo criado nesta fatia (código e testes): cabeçalho explicando o arquivo, docstring em toda classe e função, comentário em cada passo explicando o porquê, termos técnicos explicados em linguagem simples e fórmulas escritas em palavras. Antes de terminar, releia os arquivos que você criou e confirme que uma pessoa que não conhece Python conseguiria entender o que cada parte faz.

Não faça commit. Mensagem sugerida: "Cria exceções de domínio e entidades IndicadorDiario, Anotacao e FeedbackRoteiro".

### Prompt 5
FATIA 1.3 — Entidade Vendedor com métricas (Etapa 1)

Pré-requisito: fatia 1.2 concluída (IndicadorDiario existe).

Objetivo: criar `Vendedor` em backend/domain/vendedor.py, que encapsula identidade, histórico de indicadores e metas e calcula as métricas.

Construtor: Vendedor(vendedor_id: str, nome: str, cargo: str, loja_id: str, loja_nome: str, indicadores: Iterable[IndicadorDiario], metas: Mapping[str, float] | None = None), onde as chaves de `metas` são meses "AAAA-MM" e o valor é a meta em R$.

Regras de encapsulamento:
- Guarde indicadores como tupla privada (`_indicadores`) ordenada por data, e as metas como dict privado copiado (`_metas`). Nada de expor a coleção mutável: forneça propriedades somente leitura e métodos que devolvam cópias/tuplas.
- Atributos de identidade (vendedor_id, nome, cargo, loja_id, loja_nome) como propriedades somente leitura.

Métodos (todos aceitam `mes: str | None = None` no formato "AAAA-MM"; None = todo o histórico):
- valor_vendido(mes), vendas(mes), pecas(mes), atendimentos(mes): somas.
- ticket_medio(mes) = valor_vendido / vendas.
- pecas_por_atendimento(mes) = pecas / vendas (P.A.).
- conversao(mes) = vendas / atendimentos, como fração de 0 a 1 (a formatação em % fica para as camadas de cima).
- Se o denominador for zero (ou não houver registros), retorne None. Nunca levante ZeroDivisionError e nunca retorne NaN.
- Sempre divida somas agregadas; nunca faça média de razões diárias.
- meta_do_mes(mes) -> float | None.
- atingimento_meta(mes) -> float | None: valor_vendido(mes) / meta; None se não houver meta ou for zero. Fração (1.12 = 112%).
- meses_com_dados() -> tuple[str, ...] ordenada.
- dias_com_dados(mes) -> int (quantidade de registros do mês), para sinalizar mês parcial (novembro/2026 tem só 1 dia nos dados).
- resumo_mensal() -> list[dict], um dict por mês com: mes, dias_com_dados, valor_vendido, vendas, pecas, atendimentos, ticket_medio, pecas_por_atendimento, conversao, meta, atingimento_meta.

Observações importantes de dados: o gerente (Diego, cargo "gerente") também terá indicadores mas NÃO tem meta individual (metas vazio deve funcionar); o Lucas Moreira só começa em 2026-09 (sem registros de agosto); a Renata Campos tem férias em setembro. Nada disso pode causar exceção.

Crie backend/tests/test_vendedor.py com dados sintéticos pequenos (sem ler CSV): conferência manual das 3 métricas; filtro por mês; denominador zero retorna None; sem meta retorna None; atingimento correto; resumo_mensal; imutabilidade (alterar a lista original passada ao construtor não muda o Vendedor; não há como alterar `_indicadores` pela API pública).

Validação: rode a suíte completa a partir de backend/ e mostre a saída real.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto em TODO arquivo criado nesta fatia (código e testes): cabeçalho explicando o arquivo, docstring em toda classe e função, comentário em cada passo explicando o porquê, termos técnicos explicados em linguagem simples e fórmulas escritas em palavras. Antes de terminar, releia os arquivos que você criou e confirme que uma pessoa que não conhece Python conseguiria entender o que cada parte faz.

Não faça commit. Mensagem sugerida: "Cria entidade Vendedor com ticket médio, P.A., conversão e atingimento de meta".

### Prompt 6
FATIA 1.4 — Entidade Gerente e busca de anotações por nome (Etapa 1)

Pré-requisito: fatias 1.2 e 1.3 concluídas.

Objetivo: criar `Gerente` com suas anotações e uma função utilitária para comparar nomes de forma robusta.

1. backend/domain/texto.py: função `normalizar_nome(texto: str) -> str` que remove espaços nas pontas e duplicados, remove acentos (unicodedata) e converte para minúsculas (casefold). Ex.: "  Patrícia   Lemos " -> "patricia lemos".

2. backend/domain/gerente.py: `Gerente`:
   - construtor: Gerente(gerente_id: str, nome: str, loja_id: str, loja_nome: str, anotacoes: Iterable[Anotacao]);
   - identidade como propriedades somente leitura;
   - anotações guardadas em tupla privada ordenada por data; nunca exponha a coleção mutável;
   - `anotacoes()` -> tuple[Anotacao, ...] com todas;
   - `anotacoes_sobre(nome: str)` -> tuple[Anotacao, ...]: casa pelo nome normalizado; aceita nome completo OU primeiro nome ("Bianca" encontra "Bianca Rocha"); ordem cronológica; se o termo bater com mais de uma pessoa distinta, considere só correspondência exata do nome completo e, se não houver, retorne vazio. Não deve incluir anotações "(time)";
   - `anotacoes_do_time()` -> tuple[Anotacao, ...] com as anotações cujo `e_do_time` é True;
   - `total_anotacoes()` -> int.

3. backend/tests/test_gerente.py com dados sintéticos: normalizar_nome com acento, caixa e espaços; anotacoes_sobre por nome completo e por primeiro nome; nome inexistente retorna vazio; anotações do time separadas; ordem cronológica; imutabilidade.

Não leia CSVs nesta fatia.

Validação: rode a suíte completa a partir de backend/ e mostre a saída real.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto em TODO arquivo criado nesta fatia (código e testes): cabeçalho explicando o arquivo, docstring em toda classe e função, comentário em cada passo explicando o porquê, termos técnicos explicados em linguagem simples e fórmulas escritas em palavras. Antes de terminar, releia os arquivos que você criou e confirme que uma pessoa que não conhece Python conseguiria entender o que cada parte faz.

Não faça commit. Mensagem sugerida: "Cria entidade Gerente e normalização de nomes".

### Prompt 7
FATIA 1.5 — Serviço de carga de dados com Pandas (Etapa 1)

Pré-requisito: fatias 1.1 a 1.4 concluídas.

Objetivo: criar backend/services/data_loader.py com a classe `DataLoader`, que lê os 4 CSVs de backend/data/ e devolve objetos de domínio. É a única camada que conhece Pandas: as entidades de domínio não recebem DataFrame nem NaN.

Requisitos:
- Construtor: DataLoader(data_dir: Path = DATA_DIR, loja_id: str = LOJA_ID, loja_nome: str = LOJA_NOME). Leitura PREGUIÇOSA e uma única vez (cache interno), na primeira chamada de método público.
- Os DataFrames e coleções ficam privados (`_vendedores_df`, etc.); a API pública só devolve objetos de domínio (ou tuplas/listas deles).
- Leitura com pandas.read_csv, encoding utf-8, IDs sempre como str (dtype), `data` convertida para date. Células vazias (ex.: ferias_no_periodo) não podem virar NaN dentro do domínio.
- Validação: se um arquivo não existir, não conseguir ser lido, ou faltar coluna obrigatória, levante DadosIndisponiveisError com mensagem em português dizendo qual arquivo/coluna. Colunas obrigatórias: vendedores.csv (vendedor_id, nome, cargo); indicadores_diarios_vendedor.csv (data, vendedor_id, valor_vendido, vendas, pecas, atendimentos); metas_vendedor.csv (vendedor_id, mes, meta_valor); anotacoes_gerente.csv (data, sobre, anotacao).
- Todos os funcionários de vendedores.csv pertencem à loja configurada (o CSV não tem coluna de loja).

Métodos públicos:
- obter_gerente() -> Gerente: a linha de vendedores.csv com cargo "gerente" (Diego Furtado, C0030), com todas as anotações do anotacoes_gerente.csv.
- listar_vendedores() -> list[Vendedor]: só cargo "vendedor" (8 pessoas), cada um com seus IndicadorDiario e metas (dict mes -> meta_valor) cruzados por vendedor_id. Ordem do CSV.
- obter_vendedor(vendedor_id: str) -> Vendedor: levanta VendedorNaoEncontradoError se o ID não existir ou não for cargo "vendedor".
- buscar_vendedor_por_nome(nome: str) -> Vendedor: usa normalizar_nome; aceita primeiro nome ("Bianca"); se não achar ou houver mais de um, levanta VendedorNaoEncontradoError com mensagem clara.
- obter_anotacoes_do_vendedor(vendedor_id: str) -> tuple[Anotacao, ...]: usa o Gerente e o nome do vendedor.
- obter_gerente_loja_info não é necessário; não crie métodos além dos listados.

Observações sobre os dados reais: o gerente Diego tem indicadores no CSV mas não faz parte da lista de vendedores; o anotacoes_gerente.csv tem linhas com sobre="(time)"; Lucas Moreira não tem registros de agosto; ferias_no_periodo é texto livre vazio na maioria.

Teste: backend/tests/test_data_loader.py usando um diretório temporário (tempfile) com CSVs mínimos sintéticos para: leitura correta, cruzamento por ID, arquivo ausente, coluna faltando, vendedor inexistente, busca por primeiro nome, nome ambíguo. Adicione também um teste de fumaça contra os CSVs reais: listar_vendedores retorna 8 vendedores, obter_gerente retorna Diego Furtado com 21 anotações, buscar_vendedor_por_nome("Bianca") retorna C0031 com 4 meses de dados (2026-08 a 2026-11).

Validação: rode a suíte completa a partir de backend/ e mostre a saída real.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto em TODO arquivo criado nesta fatia (código e testes): cabeçalho explicando o arquivo, docstring em toda classe e função, comentário em cada passo explicando o porquê, termos técnicos explicados em linguagem simples e fórmulas escritas em palavras. Antes de terminar, releia os arquivos que você criou e confirme que uma pessoa que não conhece Python conseguiria entender o que cada parte faz.

Não faça commit. Mensagem sugerida: "Cria DataLoader que lê os CSVs e monta Vendedor e Gerente".

### Prompt 8
FATIA 1.6 — Comparativo com o time e fechamento da Etapa 1

Pré-requisito: fatia 1.5 concluída.

Objetivo: permitir identificar objetivamente o perfil da Bianca (alta conversão, P.A. baixo) comparando-a com o time. IMPORTANTE: os CSVs NÃO têm meta de P.A. nem de conversão (metas_vendedor.csv só tem meta em R$). Portanto a referência para "acima/abaixo" é a MÉDIA DO TIME, calculada agregando as somas de todos os vendedores (cargo "vendedor", 8 pessoas, sem o gerente), nunca a média de razões individuais.

1. Crie backend/domain/comparativo_time.py:
   - `MetricaComparada`, dataclass(frozen=True): nome (str: "ticket_medio", "pecas_por_atendimento" ou "conversao"), valor (float | None), media_time (float | None), diferenca_percentual (float | None; (valor - media)/media), posicao (int | None; 1 = melhor entre os vendedores), total_vendedores (int), situacao (str: "acima", "abaixo" ou "na_media" com tolerância de 5% em torno da média; "indisponivel" se algum valor for None).
   - `ComparativoTime`, dataclass(frozen=True): vendedor_id, nome, metricas (tuple de MetricaComparada), mes (str | None). Método `para_dict()`.

2. Em DataLoader adicione `obter_comparativo_time(vendedor_id: str, mes: str | None = None) -> ComparativoTime`. A média do time e o ranking consideram os 8 vendedores no mesmo período (`mes` ou histórico todo). Vendedor sem dados no período entra como valor None e fora do ranking. Reaproveite os métodos de Vendedor; não duplique fórmulas.

3. Testes em backend/tests/test_comparativo_time.py com dados sintéticos (média ponderada por somas, posição, situação, tolerância de 5%, vendedor sem dados).

4. Teste de integração com os CSVs reais em backend/tests/test_integracao_bianca.py, com tolerância (assertAlmostEqual / delta) e estes valores esperados para o histórico completo da Bianca (C0031):
   - conversão ≈ 0,505, posição 1 de 8, situação "acima";
   - P.A. ≈ 1,224, posição 8 de 8, situação "abaixo" (média do time ≈ 1,755);
   - ticket médio ≈ R$ 206,3, posição 8 de 8, situação "abaixo" (média do time ≈ R$ 303,8);
   - atingimento da meta em 2026-10 ≈ 1,124.
   Se algum valor real divergir, NÃO ajuste o teste para passar: investigue, explique a divergência e me avise.

5. Validação final da Etapa 1 (execute e mostre as saídas reais):
   - suíte completa de testes passando, a partir de backend/;
   - um comando `python -c` que instancie DataLoader, busque "Bianca", imprima resumo_mensal() e o comparativo com o time, e imprima as anotações da Bianca. O resultado deve evidenciar alta conversão e P.A. abaixo do time, sem erros;
   - `GET /health` continua funcionando (suba uvicorn rapidamente a partir de backend/ e chame; depois encerre);
   - `git status --short`: só arquivos de backend/ (código, testes e CSVs); nenhum .env, venv ou __pycache__.

Ao final, diga claramente se a Etapa 1 está concluída ("pronta quando: o serviço lê os CSVs e retorna o Vendedor com métricas consolidadas, identificando a alta conversão e o P.A. abaixo do time da Bianca") e liste pendências reais.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS da mensagem de contexto em TODO arquivo criado nesta fatia (código e testes): cabeçalho explicando o arquivo, docstring em toda classe e função, comentário em cada passo explicando o porquê, termos técnicos explicados em linguagem simples e fórmulas escritas em palavras. Antes de terminar, releia os arquivos que você criou e confirme que uma pessoa que não conhece Python conseguiria entender o que cada parte faz.

Não faça commit. Mensagem sugerida: "Adiciona comparativo com o time e testes de integração da Bianca". Lembre-me de registrar no DIARIO.md o que decidi e aprendi, sem escrever por mim.

### Prompt 9
CONTEXTO DO PROJETO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de pip/npm install, criar pastas, git add/commit/checkout etc.).

Vou te passar uma sequência de prompts, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar. Não implemente nada por conta própria.

Tarefa agora:
1. Leia, sem alterar: README.md, BRIEFING.md (seção "Desafio 3 — O feedback que ninguém dá"), AI-AGENTS.md, COMO-RODAR.md, DIARIO.md, .gitignore, dados/desafio-3-feedback/LEIAME.md e dados/desafio-3-feedback/exemplos_feedbacks_ruins.md.
2. Leia o backend inteiro: backend/config.py, backend/main.py, backend/requirements.txt, backend/.env.example, tudo em backend/domain/, backend/services/data_loader.py e os testes em backend/tests/ (só para entender o estilo). Veja as primeiras linhas dos CSVs em backend/data/.
3. Responda só com um resumo curto (máx. 15 linhas) do que entendeu, do estado atual do código e das dúvidas que tiver. Não escreva código e não crie arquivos.

O que estamos construindo: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um co-piloto que ajuda o gerente Diego Furtado (loja L004, Aurora Shopping Centro) a preparar o feedback da vendedora Bianca Rocha (C0031) com base em indicadores de vendas e nas anotações dele. A gerente regional Patrícia Lemos acompanha numa visão executiva. O gerente continua dono da conversa: a IA entrega um rascunho de roteiro, não uma sentença.

Estado atual:
- Etapas 0 e 1 prontas: backend FastAPI mínimo (main.py com GET /health), CSVs em backend/data/, entidades de domínio (Vendedor, Gerente, Anotacao, IndicadorDiario, FeedbackRoteiro, ComparativoTime), exceções de domínio base e o serviço DataLoader (com obter_comparativo_time), cobertos por testes unittest. Frontend React + Vite com a página inicial limpa.
- Ainda NÃO existem: services/llm_service.py, exceções de LLM, endpoints, contratos nem código de frontend além da página inicial.
- Vamos agora fazer a "Etapa 2 – Serviço de integração com a LLM (DeepSeek)", dividida em 5 fatias.

Fatos importantes sobre a Etapa 2:
- A integração usa a SDK `openai` (já está no requirements.txt) apontando para base_url "https://api.deepseek.com", com a chave em DEEPSEEK_API_KEY (variável de ambiente / arquivo backend/.env, que nunca é versionado). Você NUNCA deve pedir, ler, imprimir, registrar em log ou escrever a chave em qualquer arquivo. Os testes automáticos não podem fazer chamadas de rede: use um cliente falso (fake). A chamada real ao DeepSeek será feita por mim, rodando um script que você vai criar.
- Os nomes de modelo da DeepSeek mudam (os antigos "deepseek-chat" e "deepseek-reasoner" foram aposentados). Por isso o nome do modelo deve vir de configuração (variável DEEPSEEK_MODEL) e NÃO deve ficar fixo no meio do código. Não presuma o nome correto: use o padrão indicado no prompt e deixe fácil de trocar.
- O modo JSON da API exige a palavra "json" no prompt e um exemplo do formato esperado, e é recomendável definir max_tokens para a resposta não ser cortada.
- A resposta do modelo deve ser um JSON com exatamente 4 chaves, cada uma uma lista de textos: pontos_positivos, pontos_melhoria, possiveis_motivos, roteiro_conversa. Esse JSON vira o objeto de domínio FeedbackRoteiro.
- O feedback deve seguir o padrão SBI (Situação, Comportamento, Impacto) e sugerir perguntas abertas empáticas.

Convenções que valem para TODOS os prompts seguintes:
- Separação de responsabilidades: nenhuma chamada à LLM nem regra de cruzamento de dados no frontend. O frontend só consome contratos REST do backend.
- Métricas (Ticket Médio = valor vendido ÷ vendas; P.A. = peças ÷ vendas; Conversão = vendas ÷ atendimentos) são calculadas só no backend, com somas agregadas, e já existem em Vendedor/DataLoader: REAPROVEITE, não recalcule nem duplique fórmulas. Os CSVs não têm meta de P.A. nem de conversão: a referência é a média do time.
- Imports do backend são absolutos a partir da pasta backend/ (ex.: `from domain.vendedor import Vendedor`).
- Testes com `unittest` da biblioteca padrão, em backend/tests/, rodados de dentro de backend/ com o python do venv: `python -m unittest discover -s tests -t .` (Windows: backend/venv/Scripts/python; Linux/macOS: backend/venv/bin/python). A suíte atual (60 testes) deve continuar passando.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: todo código que você escrever (backend, testes e, nas etapas futuras, frontend) deve ser bem comentado, em português (pt-BR) e em linguagem simples, para que qualquer pessoa, mesmo sem conhecer a linguagem, entenda o que acontece em cada parte. Siga estas regras:
  1. Todo arquivo começa com um comentário/docstring de 2 a 4 linhas dizendo, em palavras simples, para que serve o arquivo e como ele se encaixa no projeto.
  2. Toda classe e toda função tem docstring explicando: o que faz, o que recebe, o que devolve e, quando ajudar, um exemplo curto.
  3. Dentro das funções, comente cada bloco lógico (cada passo) explicando o que está sendo feito e POR QUÊ, não apenas repetindo o código. Evite comentários óbvios linha a linha; prefira explicar a intenção.
  4. Explique termos técnicos na primeira vez em que aparecerem no arquivo, com palavras do dia a dia (ex.: "timeout: tempo máximo de espera por uma resposta", "JSON: texto organizado em pares nome/valor", "cliente fake: um objeto de mentira usado nos testes para não chamar a internet de verdade").
  5. Explique cálculos e regras de negócio com a fórmula escrita em palavras.
  6. Nos testes, comente o que cada teste verifica e por que aquele resultado é o esperado.
  7. Comentários devem ser corretos e estar sempre atualizados com o código. Nada de comentários em inglês, jargão sem explicação ou textos longos demais: frases curtas e diretas.
  8. Não altere código de fatias anteriores só para adicionar comentários, a não ser que o prompt peça.
- Regras do repositório: mudanças pequenas e coesas; NÃO faça git commit/add/push/amend/reset (o commit é feito por mim); nunca coloque chaves ou segredos em arquivos versionados; só dados fictícios; não modifique dados/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md, .claude/, prompts/, nem o frontend, a menos que o prompt peça explicitamente.
- Não invente fatos sobre o repositório: verifique no código e nos CSVs. Se algo do prompt contradisser o código real, pare e me avise antes de seguir.
- Ao fim de cada prompt, informe: arquivos criados/alterados, comandos de validação executados e o resultado REAL. Não declare algo validado sem ter executado.

Aguarde o primeiro prompt. Agora responda só com o resumo e as dúvidas, sem modificar nada.

### Prompt 10
FATIA 2.1 — Exceções de LLM e configuração da integração (Etapa 2)

Objetivo: preparar o terreno (erros tratados e configurações) sem ainda falar com a API.

1. Em backend/domain/excecoes.py ADICIONE (sem alterar as existentes) estas classes, todas herdando de DominioError, com docstring didática explicando quando cada uma acontece:
   - LLMNaoConfiguradoError: chave da API ausente, vazia ou recusada pelo provedor (erro de autenticação);
   - LLMIndisponivelError: falha de conexão, tempo esgotado (timeout), limite de uso, saldo insuficiente ou erro do servidor do provedor;
   - LLMRespostaInvalidaError: a IA respondeu, mas a resposta é vazia, cortada, não é JSON válido ou não passou nas validações de qualidade.

2. Em backend/config.py ADICIONE (sem alterar o que existe):
   - LLM_BASE_URL = "https://api.deepseek.com";
   - nomes das variáveis de ambiente como constantes: ENV_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY", ENV_DEEPSEEK_MODEL = "DEEPSEEK_MODEL", ENV_DEEPSEEK_THINKING = "DEEPSEEK_THINKING";
   - padrões: LLM_MODELO_PADRAO = "deepseek-flash" (comente que os nomes de modelo da DeepSeek mudam e que o valor deve ser conferido na documentação oficial ou com `client.models.list()`); LLM_TIMEOUT_SEGUNDOS = 60; LLM_MAX_TOKENS = 3000; LLM_TEMPERATURA = 0.4; LLM_MAX_TENTATIVAS_SDK = 1 (reenvios automáticos da SDK em falha de rede);
   - LLM_THINKING_PADRAO = "disabled" (comente: os modelos V4 vêm com "thinking" — raciocínio interno — ligado por padrão, o que deixa a resposta mais lenta e cara; para esta tarefa desligamos explicitamente; valores aceitos: "disabled", "enabled" ou "omitir" para não enviar o parâmetro);
   - ENV_FILE = caminho absoluto de backend/.env calculado a partir de __file__.

3. Atualize backend/.env.example (é versionado, sem segredos): mantenha DEEPSEEK_API_KEY= vazio e acrescente, comentadas e em português, as opções DEEPSEEK_MODEL= (ex.: deixe vazio para usar o padrão) e DEEPSEEK_THINKING= (disabled/enabled/omitir).

4. Em backend/tests/ crie test_excecoes_llm.py: verifica que as 3 novas exceções herdam de DominioError, carregam a mensagem e podem ser capturadas como DominioError. Se já existir teste de exceções, acrescente um arquivo novo em vez de editar o existente. Crie também um teste simples em test_config.py? NÃO edite o existente: se quiser testar as novas constantes, faça em arquivo novo test_config_llm.py (ex.: LLM_BASE_URL correto, timeout > 0, ENV_FILE termina em ".env").

Não instale nada, não faça chamada de rede.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em TODO código criado ou alterado nesta fatia. Antes de terminar, releia o que escreveu e confirme que alguém que não conhece Python entenderia cada parte.

Validação: rode a suíte completa a partir de backend/ e mostre a saída real (deve incluir os 60 testes anteriores). Não faça commit. Mensagem sugerida: "Adiciona exceções de LLM e configuração da integração com DeepSeek".

### Prompt 11
FATIA 2.2 — Construção do prompt (mensagem de sistema + dados do vendedor) — Etapa 2

Pré-requisito: fatia 2.1 concluída.

Objetivo: criar backend/services/prompt_feedback.py, um módulo PURO (sem rede, sem openai, sem ler CSV) que transforma os dados já calculados em duas mensagens de texto: a de sistema (regras e papel) e a de usuário (dados da vendedora). A qualidade do feedback depende daqui, então siga o conteúdo abaixo com cuidado.

API do módulo:
- `montar_mensagens(vendedor: Vendedor, comparativo: ComparativoTime, anotacoes_do_vendedor: Sequence[Anotacao], anotacoes_do_time: Sequence[Anotacao], gerente_nome: str, loja_nome: str, mes_referencia: str | None = None) -> list[dict]` devolvendo `[{"role": "system", "content": ...}, {"role": "user", "content": ...}]`.
- Constante `SISTEMA_PROMPT` (ou função) com a mensagem de sistema.
- Funções de formatação em pt-BR, com None virando "sem dados": moeda ("R$ 206,31"), percentual ("50,5%"), número com 2 casas ("1,22"), mês ("outubro/2026"). Não use locale do sistema (varia entre máquinas); formate manualmente.

MENSAGEM DE SISTEMA (em português) deve conter, nesta ordem:
1. Papel: "Você é o Co-piloto de Liderança e Feedback no Varejo", apoiando o gerente de loja; o gerente é o dono da conversa e vai revisar e adaptar o seu rascunho; a conversa é individual e privada.
2. Método SBI: explique Situação (quando/onde e qual dado), Comportamento (o que a pessoa faz, observável, sem rótulo de personalidade) e Impacto (efeito no resultado, no cliente ou no time). O feedback de melhoria deve seguir S-B-I e terminar em uma ação concreta e pequena para fazer "amanhã" (feedback vago não muda nada).
3. Regras de honestidade: use APENAS os números e anotações fornecidos; não invente fatos, datas, clientes, valores nem motivos como se fossem certos; se faltar dado, diga isso. Não faça contas novas: use os números já calculados. Os motivos em "possiveis_motivos" são HIPÓTESES a confirmar ouvindo a pessoa, e devem ser escritos como hipótese ("pode ser que...").
4. Regras de justiça e cuidado: nunca compare com colegas pelo nome (a única comparação permitida é com "a média do time"); não cite assuntos pessoais de ninguém; não use rótulos ("você é desorganizada"), ameaça, ironia nem "mas" que anule o elogio; comece reconhecendo o que é bom com base em fatos; respeite o contexto dos dados (mês parcial, férias, meta); não faça diagnóstico psicológico.
5. Tom: caloroso, direto, linguagem de loja (não de RH); proibido texto genérico de robô do tipo "Prezado colaborador", "oportunidades de melhoria em múltiplas dimensões", "buscar a excelência". Cada item deve ser específico para ESTA pessoa e ligado a um dado ou anotação.
6. Saída: responder SOMENTE com um objeto JSON válido (a palavra "JSON" deve aparecer), sem markdown, sem texto antes ou depois, com exatamente estas 4 chaves, cada uma uma lista de textos em português:
   - "pontos_positivos": 2 a 4 reconhecimentos baseados em dados reais ou anotações;
   - "pontos_melhoria": 2 a 3 alavancas de desenvolvimento, cada uma no formato SBI em uma ou duas frases (ex.: venda agregada / cross-selling quando o P.A. está abaixo da média);
   - "possiveis_motivos": 2 a 3 hipóteses comportamentais ou de contexto;
   - "roteiro_conversa": 6 a 9 itens, em ordem de conversa: abertura acolhedora, reconhecimento, Situação-Comportamento-Impacto, perguntas abertas empáticas (pelo menos 3, que não possam ser respondidas com sim/não e que convidem a pessoa a falar primeiro), combinado de uma ação para amanhã e fechamento com data de acompanhamento.
   Inclua no prompt um EXEMPLO CURTO do formato JSON (com textos fictícios genéricos e sem nomes reais de pessoas da loja).

MENSAGEM DE USUÁRIO deve conter seções claras, com todos os números já formatados:
- Quem: gerente (nome), loja, vendedora (nome, cargo), período analisado (todo o histórico ou o mês de referência), data de admissão NÃO é necessária.
- Indicadores do período: valor vendido, vendas, peças, atendimentos, ticket médio, P.A., conversão e, se houver mês de referência com meta, a meta do mês e o atingimento.
- Resumo mensal (um bloco por mês usando vendedor.resumo_mensal()): ticket médio, P.A., conversão, atingimento; marque como "mês parcial (apenas N dias com dados)" quando dias_com_dados < 10.
- Comparativo com a média do time (usando o ComparativoTime recebido): para cada métrica, valor, média do time, diferença percentual, posição "Xº de N" e situação (acima/abaixo/na média). Deixe explícito que NÃO há meta de P.A. nem de conversão, apenas a média do time como referência.
- Anotações do gerente SOBRE a vendedora (data + texto, ordem cronológica) e anotações sobre o time inteiro (data + texto). NÃO inclua anotações sobre outras pessoas.
- Instrução final: "Gere o roteiro em JSON conforme as regras."

Testes em backend/tests/test_prompt_feedback.py usando dados sintéticos (sem CSV) e UM teste de integração com os CSVs reais (DataLoader) para a Bianca: verifique que (a) devolve 2 mensagens com roles corretos; (b) a mensagem de sistema contém "JSON", as 4 chaves e "SBI"; (c) a mensagem de usuário contém o nome da vendedora, "50,5%" (conversão real), os textos das 3 anotações dela e as 2 do time, e NÃO contém os nomes das outras vendedoras (Sabrina, Kaique, Lucas, Marcelo, Renata, Tatiane, Vanessa); (d) formatação de moeda/percentual/None; (e) marcação de mês parcial para novembro/2026 (1 dia de dados).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em TODO arquivo criado (cabeçalho, docstrings, passos explicados, termos técnicos em linguagem simples). Comente também, dentro do texto do prompt montado no código, POR QUE cada regra existe (ex.: "não comparar com colegas pelo nome: isso humilha e gera conflito"), usando comentários de código ao lado do texto, não dentro do texto enviado à IA.

Validação: suíte completa a partir de backend/ com saída real. Execute também um `python -c` que imprima o prompt completo da Bianca (system + user) para eu ler, SEM chamar API. Não faça commit. Mensagem sugerida: "Cria construtor do prompt de feedback com SBI e dados da vendedora".

### Prompt 12
FATIA 2.3 — Serviço de integração com a LLM (DeepSeek) — Etapa 2

Pré-requisito: fatias 2.1 e 2.2 concluídas.

Objetivo: criar backend/services/llm_service.py com a classe `LLMService`. Os testes NÃO podem chamar a internet: use um cliente falso (fake). Não peça, leia nem imprima a chave da API.

Construtor: LLMService(data_loader: DataLoader | None = None, client=None, modelo: str | None = None, thinking: str | None = None). 
- data_loader None => cria um DataLoader() padrão.
- client None => o cliente real é criado de forma PREGUIÇOSA só na primeira chamada: carregue backend/.env com python-dotenv usando o caminho ENV_FILE do config (sem exigir que exista), leia a chave da variável DEEPSEEK_API_KEY e crie `OpenAI(api_key=..., base_url=LLM_BASE_URL, timeout=LLM_TIMEOUT_SEGUNDOS, max_retries=LLM_MAX_TENTATIVAS_SDK)`. Se a chave não existir ou estiver vazia, levante LLMNaoConfiguradoError com mensagem em português explicando como configurar (copiar .env.example para .env e preencher), sem nunca incluir o valor da chave.
- modelo: argumento > variável DEEPSEEK_MODEL (se não vazia) > LLM_MODELO_PADRAO. thinking: argumento > DEEPSEEK_THINKING > LLM_THINKING_PADRAO.

Método principal: `gerar_roteiro_feedback(self, vendedor_id: str, mes_referencia: str | None = None) -> FeedbackRoteiro`:
1. Busca o Vendedor (DataLoader.obter_vendedor), o comparativo (obter_comparativo_time com o mesmo mês), as anotações dele (obter_anotacoes_do_vendedor), as do time (obter_gerente().anotacoes_do_time()) e o nome do gerente/loja. Se o vendedor não existir, deixe VendedorNaoEncontradoError subir (não capture).
2. Monta as mensagens com prompt_feedback.montar_mensagens.
3. Chama `client.chat.completions.create(model=..., messages=..., response_format={"type": "json_object"}, max_tokens=LLM_MAX_TOKENS, temperature=LLM_TEMPERATURA, extra_body=...)`. extra_body = {"thinking": {"type": <valor>}} quando thinking não for "omitir"; se for "omitir", não envie extra_body. Comente que temperatura não faz efeito com thinking ligado.
4. Lê `choices[0].message.content` e `finish_reason`. Se finish_reason == "length" => LLMRespostaInvalidaError (resposta cortada; sugerir aumentar max_tokens). Se content for None/vazio/só espaços => LLMRespostaInvalidaError (o modo JSON da API às vezes devolve vazio).
5. Converte para dict: remova cercas de markdown (```json ... ```) se existirem, faça json.loads; JSON inválido ou que não seja um objeto => LLMRespostaInvalidaError (sem incluir a resposta inteira na mensagem; no máximo os primeiros 200 caracteres).
6. Cria FeedbackRoteiro.de_dict(dados); ValueError => LLMRespostaInvalidaError.
7. Devolve o FeedbackRoteiro (o JSON final é roteiro.para_dict()).

Tratamento de exceções da SDK (importe de openai): 
- openai.AuthenticationError (e PermissionDeniedError) => LLMNaoConfiguradoError ("chave recusada pelo provedor");
- openai.APITimeoutError => LLMIndisponivelError (tempo esgotado);
- openai.APIConnectionError => LLMIndisponivelError (sem conexão);
- openai.RateLimitError => LLMIndisponivelError (limite de uso);
- openai.APIStatusError (demais): status 402 => LLMIndisponivelError com mensagem de saldo insuficiente; 5xx => LLMIndisponivelError (servidor do provedor); 400/422 => LLMIndisponivelError com "requisição recusada" e o código de status (o parâmetro do modelo/thinking pode estar errado; sugerir conferir DEEPSEEK_MODEL e DEEPSEEK_THINKING).
- Capture openai.OpenAIError genérico por último. Use `raise ... from erro` para manter a causa original. NUNCA inclua a chave, cabeçalhos ou o corpo bruto da requisição em mensagens ou logs.
Observe: a ordem dos `except` importa (subclasses antes das classes pai); explique isso em comentário.

Testes em backend/tests/test_llm_service.py com um FakeClient que imita `client.chat.completions.create(...)` e devolve objetos simples com `.choices[0].message.content` e `.choices[0].finish_reason`; também permita ao fake levantar exceções reais da SDK (construa openai.APITimeoutError, APIConnectionError, AuthenticationError, RateLimitError, APIStatusError com httpx.Request/Response mínimos; httpx já é dependência da openai). Cubra: caminho feliz (JSON válido vira FeedbackRoteiro com as 4 listas); parâmetros enviados (model, response_format json_object, max_tokens, extra_body thinking disabled; "omitir" não envia extra_body); JSON dentro de cerca ```json; conteúdo vazio; JSON inválido; JSON que é lista; chaves faltando (vira listas vazias — a qualidade será tratada na próxima fatia, mas registre isso em um comentário); finish_reason "length"; cada exceção da SDK mapeada para a exceção de domínio certa; vendedor inexistente sobe VendedorNaoEncontradoError sem chamar a API; chave ausente => LLMNaoConfiguradoError (use variável de ambiente limpa via unittest.mock.patch.dict e um ENV_FILE inexistente). Em nenhum teste a chave real pode aparecer.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em TODO arquivo criado, explicando em linguagem simples: o que é um cliente de API, o que é timeout, o que é "JSON mode", o que é thinking, por que a ordem dos except importa e por que usamos um cliente fake nos testes.

Validação: suíte completa a partir de backend/ com saída real. Confirme com `grep -rn "sk-" backend/ --include=*.py` (ou equivalente) que não há nada parecido com chave no código. Não faça commit. Mensagem sugerida: "Cria LLMService com chamada ao DeepSeek, leitura do JSON e tratamento de erros".

### Prompt 13
FATIA 2.4 — Validação de qualidade da resposta da IA e nova tentativa — Etapa 2

Pré-requisito: fatia 2.3 concluída.

Objetivo: impedir que respostas ruins cheguem ao gerente. Hoje o LLMService aceita qualquer JSON com as 4 chaves; vamos validar o conteúdo e, se reprovar, pedir uma correção UMA vez.

1. Crie backend/services/validador_feedback.py (módulo puro, sem rede) com a função `validar_roteiro(roteiro: FeedbackRoteiro, vendedor_nome: str, nomes_colegas: Iterable[str]) -> list[str]` que devolve uma lista de problemas em português (lista vazia = aprovado). Regras:
   a) cada uma das 4 listas deve ter pelo menos 1 item; limites: pontos_positivos 1–6, pontos_melhoria 1–5, possiveis_motivos 1–5, roteiro_conversa 4–12 itens; cada item com 10 a 700 caracteres após strip;
   b) nenhum texto pode citar o nome (completo ou primeiro nome) de colegas da vendedora: use normalizar_nome (domain/texto.py) e busca por palavra inteira (regex com \b sobre texto normalizado) para não confundir pedaços de palavra. O nome da própria vendedora e o do gerente são permitidos. Se o primeiro nome do colega coincidir com o da vendedora, ignore esse nome;
   c) roteiro_conversa deve ter pelo menos 3 itens que contenham "?" (perguntas abertas);
   d) frases genéricas proibidas, comparadas sem acento e sem diferenciar maiúsculas: "prezado colaborador", "multiplas dimensoes", "buscar a excelencia", "oportunidades de melhoria em" (mantenha a lista em uma constante fácil de editar, com comentário explicando que são clichês de "texto de robô" vistos nos exemplos ruins do desafio).
   Cada problema deve dizer qual lista/regra falhou e, quando possível, o trecho que causou (curto).

2. Em LLMService (alterando o que for necessário de llm_service.py), depois de converter o JSON em FeedbackRoteiro, chame validar_roteiro. Se houver problemas: faça UMA nova chamada à API reenviando as mensagens originais + a resposta anterior da IA (role assistant) + uma mensagem de usuário em português listando os problemas e pedindo para devolver o JSON completo corrigido, mantendo as regras. Se a segunda resposta também reprovar (ou não for JSON válido), levante LLMRespostaInvalidaError listando os problemas da última tentativa (sem texto longo da IA). Se a primeira resposta aprovar, não faça segunda chamada. Total máximo: 2 chamadas por geração; comente por que limitamos (custo e tempo de espera do gerente).
   Os nomes dos colegas vêm de DataLoader.listar_vendedores() (todos exceto o vendedor atual).
   O FeedbackRoteiro devolvido continua sendo o mesmo tipo.

3. Atualize os testes existentes de test_llm_service.py que dependiam de "chaves faltando viram listas vazias": agora isso deve levar à nova tentativa/erro; ajuste esses testes (e só eles) e explique em comentário. Acrescente testes: resposta válida aprova com 1 chamada; resposta que cita "Sabrina" reprova e a 2ª resposta corrigida aprova (verifique que o fake recebeu 2 chamadas e que a 2ª inclui a lista de problemas); reprovada nas 2 tentativas => LLMRespostaInvalidaError com no máximo 2 chamadas; cliché "Prezado colaborador" detectado; poucas perguntas detectadas; palavra inteira (ex.: nome "Ana" não deve disparar em "plano"). Crie backend/tests/test_validador_feedback.py para as regras do validador isoladas.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em TODO código novo ou alterado, explicando em linguagem simples o que é regex/palavra inteira, por que validamos a saída de uma IA ("a IA pode errar ou escorregar na regra") e por que há só uma nova tentativa.

Validação: suíte completa a partir de backend/ com saída real. Não faça commit. Mensagem sugerida: "Adiciona validação de qualidade do feedback gerado e uma nova tentativa".

### Prompt 14
FATIA 2.5 — Script para testar com o DeepSeek de verdade e fechamento da Etapa 2

Pré-requisito: fatias 2.1 a 2.4 concluídas.

Objetivo: me dar um jeito seguro de fazer a chamada real (eu rodo; você NÃO tem e NÃO deve pedir a chave) e documentar.

1. Crie backend/scripts/__init__.py (vazio) e backend/scripts/testar_deepseek.py, executável com `python -m scripts.testar_deepseek` a partir de backend/, usando argparse:
   - `--vendedor` (padrão "Bianca"): aceita nome/primeiro nome (DataLoader.buscar_vendedor_por_nome) ou um ID como "C0031";
   - `--mes` (opcional, "AAAA-MM");
   - `--mostrar-prompt`: imprime as mensagens (system e user) montadas e SAI sem chamar a API nem exigir chave;
   - `--listar-modelos`: usa o cliente real para listar os ids de modelo disponíveis na conta (client.models.list()) e imprime só os ids (útil porque os nomes de modelo da DeepSeek mudam); exige chave;
   - sem flags: chama LLMService.gerar_roteiro_feedback e imprime o resultado como JSON bonito (json.dumps com ensure_ascii=False e indent=2), seguido de um resumo legível das 4 seções.
   Trate DominioError imprimindo a mensagem em português e saindo com código 1, sem traceback; qualquer outra exceção segue o comportamento normal. NUNCA imprima a chave, nem parte dela, nem o ambiente.

2. Crie backend/tests/test_llm_real.py com testes que só rodam quando a variável de ambiente RODAR_TESTES_LLM=1 e DEEPSEEK_API_KEY existirem (caso contrário usam unittest.skipUnless e aparecem como "skipped"): um teste que chama gerar_roteiro_feedback para a Bianca e confere que as 4 listas vêm preenchidas e que o validador aprova. Explique em comentário que consome créditos e que não roda por padrão.

3. Atualize COMO-RODAR.md (é o único arquivo de documentação que você pode editar): acrescente uma seção em português, simples, "Testar a integração com a IA (DeepSeek)" com: como preencher backend/.env (DEEPSEEK_API_KEY, e opcionalmente DEEPSEEK_MODEL e DEEPSEEK_THINKING), os comandos `python -m scripts.testar_deepseek --mostrar-prompt`, `python -m scripts.testar_deepseek --listar-modelos`, `python -m scripts.testar_deepseek --vendedor Bianca`, o que fazer se der "modelo não encontrado" (rodar --listar-modelos e ajustar DEEPSEEK_MODEL; conferir a documentação oficial em api-docs.deepseek.com) e o aviso de que a chamada real consome créditos.

4. Validação final da Etapa 2 (execute e mostre as saídas reais):
   - suíte completa passando a partir de backend/ (os testes reais devem aparecer como skipped);
   - `python -m scripts.testar_deepseek --mostrar-prompt` mostrando o prompt da Bianca, sem chave e sem rede;
   - `python -m scripts.testar_deepseek` SEM chave configurada deve imprimir a mensagem amigável de LLMNaoConfiguradoError e sair com código 1, sem traceback (rode isso de verdade em um ambiente sem DEEPSEEK_API_KEY);
   - GET /health continua funcionando (suba o uvicorn rapidamente a partir de backend/, chame e encerre);
   - `git status --short`: só arquivos de backend/ e COMO-RODAR.md; nenhum .env, venv ou __pycache__; busca por padrões de chave ("sk-") no repositório sem resultados.

Ao final, diga claramente: (a) tudo o que foi validado de verdade; (b) que a chamada real ao DeepSeek ainda depende de mim, com os comandos exatos para eu rodar; (c) pendências reais. Não declare a Etapa 2 concluída antes de eu colar aqui o resultado da chamada real. Não faça commit. Mensagem sugerida: "Adiciona script de teste real da IA, testes opcionais e documentação". Lembre-me de registrar no DIARIO.md o que decidi e aprendi, sem escrever por mim.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em TODO arquivo criado.

## 2026-11-11

### Prompt 1
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de pip/npm install, git add/commit/checkout).

Projeto: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Backend FastAPI + Pandas, frontend React (não mexa no frontend). Um co-piloto que ajuda o gerente Diego Furtado (C0030, loja L004) a preparar o feedback da vendedora Bianca Rocha (C0031) e dá à regional Patrícia Lemos uma visão executiva. Etapas 0, 1 e 2 prontas (domínio, DataLoader, LLMService). Estamos na Etapa 3: criar a API REST (endpoints finos, contratos Pydantic, CORS, erros {"erro": "..."}), em fatias pequenas.

Leia SOMENTE estes arquivos agora (não leia o frontend, nem scripts/, nem os testes inteiros, nem os CSVs além do cabeçalho): backend/config.py, backend/services/data_loader.py, backend/domain/vendedor.py, backend/domain/anotacao.py, backend/domain/excecoes.py e a lista de arquivos de backend/tests/. Depois responda em no máximo 8 linhas com o que entendeu e dúvidas. Não escreva código.

Regras para TODOS os prompts seguintes:
- Leia apenas os arquivos que cada prompt citar; não explore o repositório por conta própria.
- Endpoints finos: sem regra de negócio nem cálculo de métrica nas rotas. Métricas já existem em Vendedor/DataLoader: reaproveite, nunca duplique fórmulas. Taxas trafegam como fração 0–1; valores indisponíveis são null, nunca NaN.
- Imports absolutos a partir de backend/. Testes com unittest (stdlib) em backend/tests/, rodados de dentro de backend/ com o python do venv: `python -m unittest discover -s tests -t .` (Windows: backend/venv/Scripts/python). A suíte existente deve continuar passando. Testes nunca chamam a internet. NUNCA peça, leia ou imprima a chave DEEPSEEK_API_KEY.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código novo: português simples; cabeçalho em todo arquivo; docstring em toda classe e função (o que faz, recebe, devolve, exemplo curto quando ajudar); comentar cada bloco explicando o PORQUÊ; explicar termos técnicos na primeira vez com palavras do dia a dia; fórmulas escritas em palavras; testes comentados dizendo o que verificam. Não altere código antigo só para comentar.
- NÃO faça git commit/add/push/reset (eu faço os commits). Nunca coloque segredos em arquivos versionados. Não modifique dados/, prompts/, README.md, BRIEFING.md, DIARIO.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md, .claude/ nem o frontend, a menos que o prompt peça.
- Comandos de shell simples, um por vez, sem one-liners longos com pipes/awk. Se a sessão for interrompida, na retomada verifique `git status --short` e só crie o que ainda não existir.
- Não invente fatos sobre o repositório; se algo do prompt contradisser o código, pare e me avise.
- Ao final de cada prompt informe: arquivos criados/alterados, comandos de validação rodados e o resultado REAL.

Aguarde o primeiro prompt.

### Prompt 2
FATIA 3.1a — CSVs da regional, constantes e entidade AnotacaoRegional

Leia apenas: backend/config.py, backend/domain/anotacao.py e backend/tests/test_entidades.py (só o estilo).

1. COPIE (não mova; dados/ não pode ser alterado) de dados/desafio-3-feedback/ para backend/data/ os arquivos anotacoes_regional.csv e metas_loja.csv. Confirme com diff que ficaram idênticos e que o .gitignore não os ignora (`git check-ignore -v backend/data/anotacoes_regional.csv` não deve listar nada).
2. Em backend/config.py ACRESCENTE, sem alterar o que existe: ARQUIVO_ANOTACOES_REGIONAL = "anotacoes_regional.csv" e ARQUIVO_METAS_LOJA = "metas_loja.csv".
3. Crie backend/domain/anotacao_regional.py: `AnotacaoRegional`, dataclass(frozen=True) com data (date), autora (str), texto (str). (Colunas do CSV: data, autora, anotacao.)
4. Crie backend/tests/test_anotacao_regional.py: criação válida, imutabilidade (alterar atributo levanta FrozenInstanceError) e um teste em test_config já existente NÃO: crie um teste novo que confirme que os dois arquivos novos existem em DATA_DIR.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real e `git status --short`. Não faça commit. Mensagem sugerida: "Adiciona CSVs da regional e entidade AnotacaoRegional".

### Prompt 3
FATIA 3.1b — DataLoader lê anotações da regional e metas da loja

Pré-requisito: 3.1a concluída. Leia apenas: backend/services/data_loader.py, backend/domain/anotacao_regional.py, backend/config.py e a parte inicial de backend/tests/test_data_loader.py (só para copiar o estilo de dados sintéticos).

Em backend/services/data_loader.py ACRESCENTE, sem mudar o comportamento atual, a leitura dos dois novos arquivos, no MESMO padrão dos existentes (leitura preguiçosa com cache, coleções privadas, DadosIndisponiveisError para arquivo ausente ou coluna faltando). Colunas obrigatórias: anotacoes_regional.csv = data, autora, anotacao; metas_loja.csv = mes, meta_valor. Novos métodos públicos:
- listar_anotacoes_regional() -> tuple[AnotacaoRegional, ...] em ordem cronológica;
- obter_meta_loja(mes: str) -> float | None (None se o mês não existir);
- listar_metas_loja() -> dict[str, float] (devolva uma CÓPIA; mes -> meta).

Testes em um arquivo NOVO backend/tests/test_data_loader_regional.py: CSVs sintéticos em diretório temporário (leitura correta, arquivo ausente, coluna faltando) e um teste de fumaça com os reais: 5 anotações da Patrícia; obter_meta_loja("2026-10") == 317200.0; obter_meta_loja("2030-01") é None; alterar o dict devolvido por listar_metas_loja() não muda o loader.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "DataLoader passa a ler anotações da regional e metas da loja".

### Prompt 4
FATIA 3.1c — Vendas do gerente no DataLoader

Pré-requisito: 3.1b concluída. Leia apenas: backend/services/data_loader.py, backend/domain/vendedor.py e backend/domain/gerente.py.

Em backend/services/data_loader.py ACRESCENTE o método público obter_vendas_do_gerente() -> Vendedor: um objeto Vendedor com os indicadores diários do próprio gerente (Diego, C0030, que já existem em indicadores_diarios_vendedor.csv), cargo "gerente", loja da configuração e SEM metas (ele não tem meta individual; metas vazias deve funcionar). Objetivo: reaproveitar os métodos de métrica de Vendedor (valor_vendido, ticket médio etc.) para a visão da regional. Reaproveite a rotina de montagem de Vendedor que já existe no loader; não duplique a leitura do CSV.
IMPORTANTE: o gerente NÃO pode aparecer em listar_vendedores(), obter_vendedor() (continua dando VendedorNaoEncontradoError para C0030) nem no comparativo do time; esses comportamentos não podem mudar.

Testes em backend/tests/test_data_loader_regional.py (acrescente ao arquivo criado em 3.1b): com dados sintéticos e com os CSVs reais: obter_vendas_do_gerente() retorna C0030 / "Diego Furtado" / cargo "gerente"; valor_vendido("2026-10") ≈ 10916; atingimento_meta("2026-10") é None; listar_vendedores() continua com 8 pessoas sem C0030; obter_vendedor("C0030") continua levantando VendedorNaoEncontradoError.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real e `git status --short` (só arquivos de backend/). Não faça commit. Mensagem sugerida: "DataLoader expõe as vendas do gerente".

### Prompt 5
FATIA 3.2a — Configuração e entidade RegistroFeedback

Leia apenas: backend/config.py, backend/domain/feedback_roteiro.py, backend/domain/anotacao_regional.py (só o estilo) e .gitignore.

Contexto: a visão da regional precisa saber para quais vendedores já foi preparado um roteiro. Hoje nada é guardado depois que a IA responde. VOCABULÁRIO: o sistema só sabe que o roteiro foi GERADO/PREPARADO, não que a conversa aconteceu; nunca use "realizado".

1. Em backend/config.py ACRESCENTE REGISTRO_FEEDBACKS_ARQUIVO = DATA_DIR / "registro_feedbacks.json" (comente: uso local, criado sozinho, fora do git).
2. Em .gitignore (único arquivo de configuração que esta parte pode alterar) adicione `backend/data/registro_feedbacks.json` com um comentário curto.
3. Crie backend/domain/registro_feedback.py: `RegistroFeedback`, dataclass(frozen=True): feedback_id (str, uuid4), vendedor_id, vendedor_nome, mes_referencia (str | None), gerado_em (datetime com fuso UTC), roteiro (dict com as 4 listas, vindo de FeedbackRoteiro.para_dict()). Métodos: para_dict() (datas em texto ISO 8601) e @classmethod de_dict() que levanta ValueError se faltar campo ou o tipo estiver errado.
4. Teste novo backend/tests/test_registro_feedback_entidade.py: ida e volta para_dict/de_dict preservando o horário com fuso; imutabilidade; de_dict com campo faltando e com data inválida => ValueError.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique UUID e UTC em linguagem simples). Validação: suíte completa a partir de backend/ com saída real; `git check-ignore -v backend/data/registro_feedbacks.json` deve mostrar a regra. Não faça commit. Mensagem sugerida: "Adiciona entidade RegistroFeedback e configuração do registro".

### Prompt 6
FATIA 3.2b — Serviço RegistroFeedbackService

Pré-requisito: 3.2a concluída. Leia apenas: backend/config.py, backend/domain/registro_feedback.py, backend/domain/feedback_roteiro.py e backend/domain/excecoes.py.

Crie backend/services/registro_feedback.py: `RegistroFeedbackService(arquivo: Path = REGISTRO_FEEDBACKS_ARQUIVO)` com:
- registrar(vendedor_id, vendedor_nome, mes_referencia, roteiro: FeedbackRoteiro) -> RegistroFeedback (gera id e horário UTC);
- listar(vendedor_id: str | None = None) -> list[RegistroFeedback], do mais novo para o mais antigo;
- ultimo_de(vendedor_id) -> RegistroFeedback | None;
- contar_por_vendedor() -> dict[str, int].
Regras: arquivo inexistente = lista vazia (não é erro e NÃO é criado até o primeiro registro); escrita ATÔMICA (grava num arquivo temporário na mesma pasta e troca com os.replace); um threading.Lock protege o ciclo ler-alterar-gravar (o FastAPI atende pedidos em threads); JSON corrompido ou com formato inesperado => DadosIndisponiveisError com mensagem clara em português, SEM apagar nem sobrescrever o arquivo; utf-8 com ensure_ascii=False.

Teste novo backend/tests/test_registro_feedback.py usando tempfile (NUNCA o arquivo real): arquivo inexistente => vazio e nenhum arquivo criado; registrar e listar (ordem); filtro por vendedor; ultimo_de; contar_por_vendedor; persistência entre duas instâncias; arquivo corrompido => erro e conteúdo intacto; nenhum .tmp sobrando; 20 threads registrando 1 cada => 20 registros.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique escrita atômica, lock/trava e thread em linguagem simples). Validação: suíte completa com saída real; confirme que backend/data/registro_feedbacks.json NÃO existe. Não faça commit. Mensagem sugerida: "Cria serviço de registro local dos roteiros gerados".

### Prompt 7
FATIA 3.3a — Exceção de loja e contratos de erro e métricas

Leia apenas: backend/domain/excecoes.py, backend/domain/comparativo_time.py, a lista de métodos públicos de backend/domain/vendedor.py e a saída de `pip list` filtrando "pydantic" no venv (para usar a sintaxe da versão instalada).

1. Em backend/domain/excecoes.py ACRESCENTE `LojaNaoEncontradaError(DominioError)` (código de loja inexistente), com docstring didática. Não altere as existentes.
2. Crie backend/contracts/erros.py: `ErroResposta` { erro: str }.
3. Crie backend/contracts/metricas.py com Field(description=...) em português em cada campo (aparece no Swagger):
   - `MetricasDTO` { valor_vendido, vendas, pecas, atendimentos, ticket_medio | None, pecas_por_atendimento | None, conversao | None (fração de 0 a 1) };
   - `MetricaComparadaDTO` (espelha ComparativoTime/MetricaComparada: nome, valor, media_time, diferenca_percentual, posicao, total_vendedores, situacao; use Literal para nome e situacao);
   - `ResumoMensalDTO` { mes, dias_com_dados, mes_parcial: bool, valor_vendido, vendas, pecas, atendimentos, ticket_medio, pecas_por_atendimento, conversao, meta | None, atingimento_meta | None }.
   Campos float não aceitam NaN nem infinito (use allow_inf_nan=False ou validador, conforme a versão do Pydantic; comente).
4. Teste novo backend/tests/test_contratos_metricas.py: criação válida; None vira null na serialização (model_dump_json); NaN rejeitado; valor de Literal inválido rejeitado; LojaNaoEncontradaError herda de DominioError.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique Pydantic, validação, Literal e None em linguagem simples). Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria contratos de erro e métricas e exceção de loja".

### Prompt 8
FATIA 3.3b — Contratos de vendedores e de feedback

Pré-requisito: 3.3a concluída. Leia apenas: backend/contracts/metricas.py, backend/domain/anotacao.py e backend/domain/feedback_roteiro.py.

1. Crie backend/contracts/vendedores.py (Field(description=...) em português):
   - `AnotacaoDTO` { data: date, sobre, texto, e_do_time: bool };
   - `FeedbackPreparadoDTO` { feedback_id, mes_referencia | None, gerado_em: datetime };
   - `VendedorResumoDTO` { vendedor_id, nome, cargo, metricas: MetricasDTO, comparativo: list[MetricaComparadaDTO] };
   - `ListaVendedoresResposta` { loja_id, loja_nome, mes: str | None, vendedores: list[VendedorResumoDTO] };
   - `HistoricoVendedorResposta` { vendedor_id, nome, cargo, loja_id, loja_nome, metricas (histórico todo), resumo_mensal: list[ResumoMensalDTO], comparativo: list[MetricaComparadaDTO], anotacoes: list[AnotacaoDTO] (só as SOBRE a pessoa), anotacoes_do_time: list[AnotacaoDTO], feedbacks_preparados: list[FeedbackPreparadoDTO] }.
2. Crie backend/contracts/feedback.py:
   - `FeedbackGerarRequisicao` { vendedor_id: str (obrigatório, min_length=1, espaços nas pontas removidos), mes_referencia: str | None com validação do formato "AAAA-MM" (mês 01 a 12; rejeita "2026-13", "2026/10", "outubro") };
   - `FeedbackRoteiroDTO` { pontos_positivos, pontos_melhoria, possiveis_motivos, roteiro_conversa: list[str] };
   - `FeedbackGerarResposta` { feedback_id, vendedor_id, vendedor_nome, mes_referencia | None, gerado_em: datetime, roteiro: FeedbackRoteiroDTO }.
3. Teste novo backend/tests/test_contratos_vendedores_feedback.py: requisição válida e inválida (vendedor_id vazio ou só espaços, os formatos de mês acima), espaços removidos, serialização dos DTOs de vendedores com dados fictícios, e que nenhum DTO aceita receber um objeto de domínio ou DataFrame diretamente.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria contratos de vendedores e de feedback".

### Prompt 9
FATIA 3.3c — Contratos da visão regional

Pré-requisito: 3.3b concluída. Leia apenas: backend/contracts/vendedores.py (estilo) e backend/domain/anotacao_regional.py.

Crie backend/contracts/regional.py (Field(description=...) em português; razões como fração de 0 a 1, null quando indisponíveis, sem NaN):
- `ResultadoLojaMesDTO` { mes, mes_parcial: bool, dias_com_dados: int, meta_loja | None, vendas_loja (inclui as vendas do gerente), atingimento_loja | None, vendas_vendedores (sem o gerente), atingimento_vendedores | None, vendas_gerente, participacao_gerente | None (fração das vendas da loja feitas pelo gerente) };
- `AcompanhamentoVendedorDTO` { vendedor_id, nome, anotacoes_do_gerente: int, ultima_anotacao_em: date | None, roteiros_preparados: int, ultimo_roteiro_em: datetime | None, situacao: Literal["com_roteiro", "sem_roteiro"] };
- `AcompanhamentoFeedbackDTO` { total_vendedores, vendedores_com_roteiro, cobertura (fração), total_roteiros_preparados, vendedores: list[AcompanhamentoVendedorDTO] };
- `AnotacaoRegionalDTO` { data: date, autora, texto };
- `DesempenhoGerenteResposta` { gerente_id, gerente_nome, loja_id, loja_nome, periodo_inicio: date | None, periodo_fim: date | None, resultado_loja: list[ResultadoLojaMesDTO], acompanhamento_feedback: AcompanhamentoFeedbackDTO, anotacoes_regional: list[AnotacaoRegionalDTO] }.
Comente nos campos de roteiro: "preparado" quer dizer que o roteiro foi gerado, não que a conversa aconteceu.

Teste novo backend/tests/test_contratos_regional.py: criação válida com dados fictícios, null onde permitido, Literal de situacao inválido rejeitado, NaN rejeitado, serialização de datas em texto ISO.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria contratos da visão regional".

### Prompt 10
FATIA 3.3d — Mapeadores de domínio para DTO

Pré-requisito: 3.3a a 3.3c concluídas. Leia apenas: backend/contracts/metricas.py, backend/contracts/vendedores.py, backend/contracts/feedback.py, a lista de métodos públicos de backend/domain/vendedor.py, backend/domain/comparativo_time.py, backend/domain/anotacao.py, backend/domain/feedback_roteiro.py e, em backend/services/prompt_feedback.py, apenas o trecho que define quando um mês é "parcial".

Crie backend/contracts/mapeadores.py com funções PURAS que convertem entidades em DTOs, sem recalcular nenhuma fórmula (use os métodos de Vendedor):
- metricas_de(vendedor, mes: str | None = None) -> MetricasDTO;
- resumo_mensal_de(item: dict) -> ResumoMensalDTO, onde item é um elemento de Vendedor.resumo_mensal(); mes_parcial = dias_com_dados < 10. Reutilize a regra que já existe em prompt_feedback.py: importe a constante de lá OU mova-a para config.py sem mudar o comportamento; escolha o menor impacto e me diga qual;
- comparativo_de(ComparativoTime) -> list[MetricaComparadaDTO];
- anotacao_de(Anotacao) -> AnotacaoDTO;
- roteiro_de(FeedbackRoteiro) -> FeedbackRoteiroDTO.
(Mapeadores de registro e de regional ficam para as partes que os usam.)

Teste novo backend/tests/test_mapeadores.py com a Bianca real (DataLoader dos CSVs reais): conversão ≈ 0,505; ticket médio ≈ 206,3; resumo mensal de 2026-11 com mes_parcial True e de 2026-10 com False; comparativo com 3 métricas (conversão posição 1 de 8, "acima"; P.A. posição 8 de 8, "abaixo"); anotacao_de com e_do_time True e False; roteiro_de preserva as 4 listas. Se algum valor real divergir, NÃO ajuste o teste: investigue e me avise.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique "mapeador" e "função pura"). Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria mapeadores de domínio para DTO".

### Prompt 11
FATIA 3.4a — Configuração de CORS, httpx e dependências

Leia apenas: backend/config.py, backend/.env.example, backend/requirements.txt e os construtores (apenas __init__) de DataLoader (backend/services/data_loader.py), LLMService (backend/services/llm_service.py) e RegistroFeedbackService (backend/services/registro_feedback.py).

1. Verifique se o pacote `httpx` está no venv (`python -c "import httpx"`): o TestClient do FastAPI precisa dele. Se NÃO estiver, acrescente `httpx` em backend/requirements.txt com um comentário de uma linha ("usado pelo TestClient nos testes") e me avise no final para eu rodar `pip install -r requirements.txt` (não instale você mesmo).
2. Em backend/config.py ACRESCENTE ENV_FRONTEND_ORIGINS = "FRONTEND_ORIGINS" e FRONTEND_ORIGINS_PADRAO = ("http://localhost:5173", "http://127.0.0.1:5173") (comente: o Vite serve o frontend na porta 5173; a variável aceita várias origens separadas por vírgula). Em backend/.env.example acrescente a linha comentada `#FRONTEND_ORIGINS=` com explicação em português.
3. Crie backend/endpoints/dependencias.py com funções para o Depends do FastAPI, cada uma devolvendo UMA instância compartilhada (functools.lru_cache): obter_data_loader() -> DataLoader; obter_registro_feedbacks() -> RegistroFeedbackService; obter_llm_service() -> LLMService (criado com o MESMO DataLoader; a leitura da chave continua preguiçosa, não ocorre aqui). Comente que os testes trocam essas funções com app.dependency_overrides e explique singleton em linguagem simples.
4. Teste novo backend/tests/test_dependencias.py: cada função devolve o tipo certo; duas chamadas devolvem o MESMO objeto; obter_llm_service usa o mesmo DataLoader de obter_data_loader (use cache_clear() nos testes para isolar); criar o LLMService sem chave NÃO levanta erro.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Adiciona configuração de CORS e dependências compartilhadas da API".

### Prompt 12
FATIA 3.4b — Tratamento global de erros

Pré-requisito: 3.4a concluída. Leia apenas: backend/domain/excecoes.py e backend/contracts/erros.py.

Crie backend/endpoints/erros.py com `registrar_tratadores_de_erro(app)`, que instala handlers devolvendo SEMPRE o corpo {"erro": "mensagem em português"}:
- VendedorNaoEncontradoError e LojaNaoEncontradaError -> 404;
- RequestValidationError (entrada inválida) -> 400, com mensagem resumida e legível dizendo campo e problema (ex.: "mes_referencia: use o formato AAAA-MM"), sem despejar a estrutura técnica do Pydantic;
- LLMIndisponivelError -> 503; LLMRespostaInvalidaError -> 502; LLMNaoConfiguradoError -> 500 (mensagem: serviço de IA não configurado no servidor; NUNCA revele chave nem caminhos de arquivo);
- DadosIndisponiveisError e qualquer outro DominioError -> 500;
- starlette HTTPException (rota inexistente 404, método não permitido 405) -> mesmo status, corpo {"erro": ...} em português;
- Exception genérica -> 500 com {"erro": "Erro interno do servidor."}, traceback registrado no log (logging), nunca na resposta.
Documente em comentário a tabela exceção -> status. Ainda NÃO mexa no main.py.

Teste novo backend/tests/test_erros_globais.py com TestClient sobre um app de TESTE criado no próprio arquivo (FastAPI() + registrar_tratadores_de_erro + rotas temporárias que levantam cada exceção): confira status e corpo de cada caso; Exception genérica não vaza a mensagem original; validação -> 400 em português; rota inexistente e método errado -> {"erro": ...}. Use TestClient(app, raise_server_exceptions=False) onde preciso e comente por quê.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique handler/tratador de exceção e status HTTP). Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria tratamento global de erros da API".

### Prompt 13
FATIA 3.4c — main.py: CORS, tratadores de erro e aquecimento dos dados

Pré-requisito: 3.4a e 3.4b concluídas. Leia apenas: backend/main.py, backend/config.py, backend/endpoints/dependencias.py, backend/endpoints/erros.py e o início de backend/tests/test_erros_globais.py (estilo de TestClient).

Reescreva backend/main.py preservando a rota /health e os comentários didáticos:
- load_dotenv(ENV_FILE) (caminho do config);
- `app = FastAPI(title="FullStore Feedback Inteligente", version="0.1.0", lifespan=...)`;
- CORSMiddleware: allow_origins vindas da variável FRONTEND_ORIGINS (separadas por vírgula, com strip; se vazia, usa o padrão do config), allow_methods ["GET", "POST", "OPTIONS"], allow_headers ["Content-Type"], SEM allow_credentials (não usamos cookies). Crie uma função pequena `ler_origens_permitidas()` para ser testável;
- registrar_tratadores_de_erro(app);
- lifespan (aquecimento): na subida chama obter_data_loader().listar_vendedores() para carregar os CSVs uma vez só; se falhar com DadosIndisponiveisError, registre o erro no log e deixe o servidor subir (as rotas devolverão o erro 500 amigável). Explique em comentário por que aquecer;
- no ponto onde os routers serão incluídos, deixe o comentário "# routers incluídos nas próximas partes (3.5 a 3.7)". NÃO crie arquivos de rotas ainda.

Teste novo backend/tests/test_servidor_base.py com TestClient sobre o app REAL: /health ok; rota inexistente -> 404 com {"erro": ...}; POST em /health -> 405 com {"erro": ...}; preflight CORS (OPTIONS com Origin http://localhost:5173 e Access-Control-Request-Method: POST) devolve access-control-allow-origin correto, e uma origem não permitida (http://site-estranho.com) NÃO recebe esse cabeçalho; ler_origens_permitidas com a variável vazia, com uma origem e com duas separadas por vírgula e espaços (use unittest.mock.patch.dict); a subida com TestClient usado como context manager executa o aquecimento sem erro.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique CORS, middleware, preflight e lifespan). Validação: suíte completa com saída real; suba o uvicorn de dentro de backend/, chame `curl http://localhost:8000/health` e uma rota inexistente mostrando o corpo, e encerre o servidor. Não faça commit. Mensagem sugerida: "Configura CORS, erros globais e aquecimento no main.py".

### Prompt 14
FATIA 3.5a — GET /api/vendedores/{loja_id}

Leia apenas: backend/main.py, backend/contracts/vendedores.py, backend/contracts/mapeadores.py, backend/endpoints/dependencias.py, a lista de métodos públicos de backend/services/data_loader.py, backend/config.py e o início de backend/tests/test_servidor_base.py (estilo de TestClient).

Crie backend/endpoints/vendedores.py com `APIRouter(prefix="/api", tags=["Vendedores"])` e inclua-o no main.py (no ponto marcado pelo comentário).

Rota: GET /api/vendedores/{loja_id} — função `def` (não async), response_model=ListaVendedoresResposta, responses documentando 404 e 400 com ErroResposta.
- Query opcional `mes` (AAAA-MM; use Query com pattern; formato inválido => 400 pelo handler global).
- loja_id é comparado sem diferenciar maiúsculas/minúsculas com a loja configurada (L004); outra => levante LojaNaoEncontradaError("Loja 'X' não encontrada.").
- Para cada vendedor de DataLoader.listar_vendedores() (Depends(obter_data_loader)): metricas do período (mes ou histórico todo) com metricas_de, e comparativo com DataLoader.obter_comparativo_time(vendedor_id, mes) + comparativo_de. A rota só orquestra: ZERO cálculo próprio, ZERO Pandas. Ordem da lista = ordem do CSV. O gerente não aparece.

Teste novo backend/tests/test_endpoints_vendedores_lista.py com TestClient e DataLoader REAL: 8 vendedores e nenhum com cargo "gerente"; Bianca (C0031) com conversão ≈ 0,505 e, no comparativo, conversão posição 1 de 8 "acima" e P.A. posição 8 de 8 "abaixo"; ?mes=2026-10 altera os valores; ?mes=2026-13 -> 400 com {"erro": ...}; "L999" -> 404 com {"erro": ...}; "l004" minúsculo funciona; o JSON bruto não contém "NaN". Se algum valor real divergir, NÃO ajuste o teste: investigue e me avise.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique APIRouter, parâmetro de caminho e query). Validação: suíte completa com saída real; suba o uvicorn, rode `curl http://localhost:8000/api/vendedores/L004` (mostre as primeiras linhas) e confirme que /docs responde 200 listando a rota. Não faça commit. Mensagem sugerida: "Cria endpoint de lista de vendedores da loja".

### Prompt 15
FATIA 3.5b — GET /api/vendedores/{vendedor_id}/historico

Pré-requisito: 3.5a concluída. Leia apenas: backend/endpoints/vendedores.py, backend/contracts/vendedores.py, backend/contracts/mapeadores.py, backend/services/registro_feedback.py (só os métodos públicos) e backend/domain/gerente.py (só os métodos públicos).

1. Em backend/contracts/mapeadores.py ACRESCENTE `feedback_preparado_de(RegistroFeedback) -> FeedbackPreparadoDTO` (só id, mês e horário; o texto do roteiro NÃO entra aqui).
2. Em backend/endpoints/vendedores.py ACRESCENTE: GET /api/vendedores/{vendedor_id}/historico — função `def`, response_model=HistoricoVendedorResposta, 404 documentado.
   - Aceita só ID de vendedor (ex.: C0031). ID inexistente ou do gerente (C0030) => VendedorNaoEncontradoError (404 pelo handler global).
   - Monta: identidade; metricas do histórico todo; resumo_mensal (cada item de Vendedor.resumo_mensal() via resumo_mensal_de); comparativo do histórico todo; anotacoes SOBRE o vendedor (DataLoader.obter_anotacoes_do_vendedor); anotacoes_do_time (Gerente.anotacoes_do_time()); feedbacks_preparados (RegistroFeedbackService.listar(vendedor_id), via Depends(obter_registro_feedbacks)).
   - As duas rotas do arquivo têm formatos diferentes (um segmento vs. dois) e não conflitam: confirme isso no teste.

Teste novo backend/tests/test_endpoints_vendedores_historico.py com TestClient, DataLoader real e RegistroFeedbackService apontando para arquivo TEMPORÁRIO via dependency_overrides: histórico da Bianca com 4 meses no resumo (2026-08 a 2026-11), novembro com mes_parcial true, 3 anotações dela e 2 do time, nenhuma anotação sobre outras pessoas, feedbacks_preparados vazio e depois com 1 item após registrar um no registro de teste; C0030 e "XXXX" -> 404 com {"erro": ...}; JSON sem NaN; a rota da lista (3.5a) continua funcionando.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real; suba o uvicorn e rode `curl http://localhost:8000/api/vendedores/C0031/historico` mostrando as primeiras linhas; /docs lista as 2 rotas. Não faça commit. Mensagem sugerida: "Cria endpoint de histórico do vendedor".

### Prompt 16
FATIA 3.6a — POST /api/feedback/gerar (caminho feliz)

Leia apenas: backend/main.py, backend/endpoints/vendedores.py (estilo), backend/endpoints/dependencias.py, backend/contracts/feedback.py, backend/contracts/mapeadores.py, backend/services/registro_feedback.py (só métodos públicos) e, em backend/services/llm_service.py, apenas a assinatura e a docstring de gerar_roteiro_feedback.

1. Em backend/contracts/mapeadores.py ACRESCENTE `resposta_de_feedback(RegistroFeedback) -> FeedbackGerarResposta` (reaproveite roteiro_de).
2. Crie backend/endpoints/feedback.py com `APIRouter(prefix="/api", tags=["Feedback"])` e inclua-o no main.py.
   POST /api/feedback/gerar — função `def`, NÃO `async def` (a chamada à IA bloqueia por segundos; o FastAPI roda funções normais em threads; explique em comentário). Corpo: FeedbackGerarRequisicao. response_model=FeedbackGerarResposta; documente 400, 404, 500, 502 e 503 com ErroResposta.
   Fluxo: (1) DataLoader.obter_vendedor(vendedor_id) (inexistente ou gerente => 404, SEM chamar a IA); (2) LLMService.gerar_roteiro_feedback(vendedor_id, mes_referencia) via Depends(obter_llm_service); (3) SOMENTE se a IA devolveu um roteiro válido, registrar no RegistroFeedbackService (vendedor_id, nome, mês, roteiro); (4) devolver a resposta pelo mapeador. Se a IA falhar, NADA é registrado e o erro sobe para o handler global. A rota é fina: nada de prompt, validação de qualidade ou fórmulas.
   Se gravar o registro falhar (DadosIndisponiveisError), deixe subir (500 com mensagem clara) e comente a decisão: é melhor avisar o erro do que esconder, porque sem registro a regional não acompanha.

Teste novo backend/tests/test_endpoints_feedback.py com TestClient, um LLMService FALSO via dependency_overrides (classe fake com gerar_roteiro_feedback que devolve um FeedbackRoteiro fixo e guarda os argumentos recebidos), DataLoader real e registro em arquivo temporário. NENHUM teste chama a internet. Cubra: 200 com as 4 listas preenchidas, feedback_id e gerado_em presentes, 1 registro gravado, e o fake recebeu vendedor_id e mes_referencia corretos; sem mes_referencia; duas gerações => 2 registros com ids diferentes; o histórico da Bianca (rota 3.5b) passa a listar o feedback gerado; corpo sem vendedor_id -> 400 em português; mes_referencia "2026-13" -> 400.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Você NÃO deve tentar a chamada real à IA. Não faça commit. Mensagem sugerida: "Cria endpoint de geração de feedback com registro do roteiro".

### Prompt 17
FATIA 3.6b — Caminhos de falha do POST /api/feedback/gerar

Pré-requisito: 3.6a concluída. Leia apenas: backend/endpoints/feedback.py, backend/tests/test_endpoints_feedback.py e backend/domain/excecoes.py.

Acrescente em um arquivo NOVO backend/tests/test_endpoints_feedback_falhas.py (sem editar o existente; reaproveite os ajudantes de teste copiando o mínimo necessário) testes com o LLMService FALSO programado para falhar:
- vendedor "C9999" e "C0030" -> 404 com {"erro": ...} e o fake NÃO foi chamado;
- LLMIndisponivelError -> 503 e NADA registrado;
- LLMRespostaInvalidaError -> 502 e NADA registrado;
- LLMNaoConfiguradoError -> 500, mensagem sem a palavra da chave nem caminhos de arquivo;
- falha ao gravar o registro (DadosIndisponiveisError no RegistroFeedbackService falso) -> 500 com mensagem clara;
- exceção inesperada no fake -> 500 com {"erro": "Erro interno do servidor."} sem vazar a mensagem original.
Se algum teste mostrar um bug na rota, corrija a rota com a menor mudança e me explique.

Validação: suíte completa com saída real. Depois suba o uvicorn SEM chave configurada (confirme que DEEPSEEK_API_KEY não está definida no ambiente do processo, sem imprimir seu valor) e rode `curl -X POST http://localhost:8000/api/feedback/gerar -H "Content-Type: application/json" -d "{\"vendedor_id\": \"C0031\"}"`: deve responder 500 com {"erro": ...} amigável, sem traceback e sem chave. Isso confirma o erro sem gastar créditos. Encerre o servidor. Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Não faça commit. Mensagem sugerida: "Testa os caminhos de falha da geração de feedback".

### Prompt 18
FATIA 3.7a — ConsolidadoRegional: resultado mensal da loja

Leia apenas: backend/contracts/regional.py, a lista de métodos públicos de backend/services/data_loader.py, a lista de métodos públicos de backend/domain/vendedor.py, backend/config.py e, em backend/services/prompt_feedback.py, apenas o trecho da regra de mês parcial (ou a constante que a 3.3d escolheu).

Crie backend/services/consolidado_regional.py com a classe `ConsolidadoRegional(data_loader, registro)` e, por enquanto, só o método `obter_resultado_loja() -> list[dict]` (cada dict com exatamente os campos de ResultadoLojaMesDTO). Fórmulas (escreva-as em palavras nos comentários):
- Meses: união dos meses com dados dos 8 vendedores e do gerente, em ordem.
- Por mês: meta_loja = DataLoader.obter_meta_loja(mes) (None se não houver); vendas_vendedores = soma de valor_vendido(mes) dos 8 vendedores (listar_vendedores()); vendas_gerente = valor_vendido(mes) do Vendedor de obter_vendas_do_gerente(); vendas_loja = vendas_vendedores + vendas_gerente; atingimento_loja = vendas_loja ÷ meta_loja; atingimento_vendedores = vendas_vendedores ÷ meta_loja; participacao_gerente = vendas_gerente ÷ vendas_loja. Denominador zero ou ausente => None.
- dias_com_dados = maior número de dias com dados entre as pessoas naquele mês; mes_parcial = dias_com_dados < 10 (mesma regra dos contratos).
- Comente POR QUE mostramos dois atingimentos: a meta da loja é a soma das metas dos vendedores, que NÃO inclui o gerente; as vendas do gerente ajudam a loja, mas não contam para a meta individual de ninguém.

Teste novo backend/tests/test_consolidado_resultado_loja.py: (1) com STUBS simples no lugar do DataLoader (classes pequenas que devolvem Vendedores sintéticos e metas), conferindo cada fórmula à mão, denominador zero e mês parcial; (2) com os CSVs reais: 4 meses; em 2026-10 meta_loja == 317200.0, vendas_vendedores ≈ 315781.85 (atingimento ≈ 0,9955), vendas_loja ≈ 326697.48 (atingimento ≈ 1,03), vendas_gerente ≈ 10916; 2026-11 com mes_parcial True. Se algum valor real divergir, NÃO ajuste o teste: investigue e me avise.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria consolidado regional: resultado mensal da loja".

### Prompt 19
FATIA 3.7b — ConsolidadoRegional: acompanhamento e resposta completa

Pré-requisito: 3.7a concluída. Leia apenas: backend/services/consolidado_regional.py, backend/contracts/regional.py, os métodos públicos de backend/services/registro_feedback.py e de backend/domain/gerente.py, e a lista de métodos públicos de backend/services/data_loader.py.

Em backend/services/consolidado_regional.py ACRESCENTE:
1. `obter_acompanhamento_feedback() -> dict` (campos de AcompanhamentoFeedbackDTO). Para cada um dos 8 vendedores, na ordem do CSV: anotacoes_do_gerente = quantidade de anotações do Diego SOBRE a pessoa; ultima_anotacao_em = data da mais recente (ou None); roteiros_preparados e ultimo_roteiro_em vindos do RegistroFeedbackService; situacao = "com_roteiro" se roteiros_preparados > 0, senão "sem_roteiro". Resumo: total_vendedores; vendedores_com_roteiro; cobertura = vendedores_com_roteiro ÷ total_vendedores; total_roteiros_preparados.
2. `obter_desempenho_gerente() -> dict` com exatamente os campos de DesempenhoGerenteResposta: gerente_id e gerente_nome (do Gerente), loja_id e loja_nome (do DataLoader/config), periodo_inicio e periodo_fim (menor e maior data dos indicadores de vendedores e gerente; None se não houver), resultado_loja (3.7a), acompanhamento_feedback e anotacoes_regional (listar_anotacoes_regional(), cronológica, cada uma como dict data/autora/texto).
Comente: "roteiro preparado" NÃO é "feedback realizado"; o sistema só sabe que o roteiro foi gerado.

Teste novo backend/tests/test_consolidado_acompanhamento.py: com stubs sintéticos (cobertura 0, 1/8 e 8/8, última anotação, vendedor sem anotações) e com os CSVs reais e registro temporário: 8 vendedores todos "sem_roteiro" com registro vazio e cobertura 0; 5 anotações da regional; depois de registrar um roteiro da Bianca, ela vira "com_roteiro", cobertura = 0,125 e total_roteiros_preparados = 1; Bianca com 3 anotações do gerente; gerente_nome "Diego Furtado", loja L004; periodo_inicio 2026-08-01 e periodo_fim 2026-11-01; o dict de obter_desempenho_gerente() é aceito por DesempenhoGerenteResposta(**dict) sem erro. Se algum valor real divergir, NÃO ajuste o teste: investigue e me avise.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Completa o consolidado regional com o acompanhamento de roteiros".

### Prompt 20
FATIA 3.7c — GET /api/regional/desempenho-gerente

Pré-requisito: 3.7a e 3.7b concluídas. Leia apenas: backend/services/consolidado_regional.py (só assinaturas), backend/contracts/regional.py, backend/endpoints/dependencias.py, backend/endpoints/vendedores.py (estilo), backend/main.py e o início de backend/tests/test_endpoints_vendedores_historico.py (estilo de TestClient e overrides).

1. Em backend/endpoints/dependencias.py ACRESCENTE obter_consolidado_regional() (singleton com lru_cache, montado com obter_data_loader() e obter_registro_feedbacks(); atenção: o registro precisa ser o MESMO usado pela rota de feedback para a regional enxergar os roteiros gerados).
2. Crie backend/endpoints/regional.py com `APIRouter(prefix="/api", tags=["Regional"])` e inclua-o no main.py. GET /api/regional/desempenho-gerente — função `def`, response_model=DesempenhoGerenteResposta, erros documentados com ErroResposta. A rota só chama ConsolidadoRegional.obter_desempenho_gerente() via Depends e devolve o resultado (o Pydantic valida o dict; se precisar de conversão, crie o mapeador em contracts/mapeadores.py).

Teste novo backend/tests/test_endpoints_regional.py com TestClient, overrides (DataLoader real, registro temporário compartilhado): 200 e estrutura do contrato; resultado_loja com 4 meses e outubro com meta 317200.0; 5 anotações da regional; JSON bruto sem NaN; ao registrar um roteiro da Bianca no registro de teste, a rota mostra a Bianca "com_roteiro"; e um teste de INTEGRAÇÃO entre rotas: com o LLM falso, POST /api/feedback/gerar para C0031 e em seguida GET /api/regional/desempenho-gerente mostra a Bianca "com_roteiro" e total_roteiros_preparados = 1 (isso prova que as duas rotas usam o mesmo registro).

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: suíte completa com saída real; suba o uvicorn e rode `curl http://localhost:8000/api/regional/desempenho-gerente` mostrando o trecho de resultado_loja de outubro e o acompanhamento. Não faça commit. Mensagem sugerida: "Cria endpoint da visão regional".

### Prompt 21
FATIA 3.8a — Arquivo backend/api.http

Leia apenas: backend/main.py, os decoradores de rota (@router.get/@router.post e caminhos) de backend/endpoints/*.py e backend/contracts/feedback.py.

Crie backend/api.http no formato do VS Code REST Client (aceito também pelo JetBrains), com `@base = http://localhost:8000` e uma requisição para cada rota, separadas por `###`, cada uma com um comentário em português antes explicando o que faz: GET /health; GET /api/vendedores/L004; GET /api/vendedores/L004?mes=2026-10; GET /api/vendedores/C0031/historico; POST /api/feedback/gerar com {"vendedor_id": "C0031"} (avise no comentário que consome créditos da DeepSeek e pode levar de 10 a 60 segundos); o mesmo POST com "mes_referencia": "2026-10"; GET /api/regional/desempenho-gerente; e dois exemplos de erro (loja inexistente L999 e mes_referencia inválido "2026-13"). Não crie testes nem altere outro arquivo.

Validação: confira que as rotas do arquivo existem de fato em /openapi.json (suba o uvicorn, consulte e encerre). Não faça commit. Mensagem sugerida: "Adiciona arquivo api.http com exemplos de chamadas".

### Prompt 22
FATIA 3.8b — Documentação da API

Leia apenas: COMO-RODAR.md, backend/endpoints/erros.py e backend/config.py.

Edite SOMENTE COMO-RODAR.md: acrescente uma seção em português simples "Usar a API" com: como subir o servidor (de dentro de backend/ com o venv ativo); onde ver a documentação interativa (http://localhost:8000/docs); como usar o arquivo backend/api.http; a lista das rotas com uma linha cada; o formato dos erros ({"erro": "..."}) com a tabela de status confirmada em endpoints/erros.py (400 entrada inválida, 404 não encontrado, 500 erro interno ou IA não configurada, 502 resposta inválida da IA, 503 IA indisponível); a variável opcional FRONTEND_ORIGINS (CORS); e o aviso de que backend/data/registro_feedbacks.json é criado sozinho, não é versionado e guarda os roteiros gerados (explique "roteiro preparado" ≠ "feedback realizado"). Não altere o restante do arquivo.

Validação: mostre o `git diff COMO-RODAR.md` resumido. Não faça commit. Mensagem sugerida: "Documenta o uso da API no COMO-RODAR".

### Prompt 23
FATIA 3.8c — Validação final da Etapa 3 (não crie nem altere código, só valide e relate)

Rode e mostre as saídas reais:
1. Suíte completa a partir de backend/ (diga quantos testes passaram e se algum ficou "skipped").
2. Suba o uvicorn de dentro de backend/ e confira: /docs responde 200; /openapi.json lista exatamente estas rotas: /health, /api/vendedores/{loja_id}, /api/vendedores/{vendedor_id}/historico, /api/feedback/gerar, /api/regional/desempenho-gerente.
3. curl em cada rota GET com um resumo do resultado; o POST sem chave devolvendo o 500 amigável; um erro 404 (loja L999) e um 400 (mes=2026-13), ambos com {"erro": ...}.
4. Preflight CORS: curl -i -X OPTIONS http://localhost:8000/api/feedback/gerar -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: POST" -H "Content-Type: application/json" mostrando access-control-allow-origin.
5. Varreduras: `grep -rn "fetch\|axios" backend/` sem resultados; `grep -rn "sk-" backend/ --include=*.py` sem resultados; nenhuma regra de cálculo dentro de backend/endpoints/ (liste os imports de cada arquivo ali e confirme que não importam pandas).
6. `git status --short`: deve haver só arquivos de backend/, COMO-RODAR.md e .gitignore; nenhum .env, venv, __pycache__ nem registro_feedbacks.json.
Encerre o servidor.

Ao final diga claramente: (a) o que foi validado de verdade; (b) que a geração real de feedback pela API depende de mim, com os passos (preencher backend/.env, subir o servidor, enviar o POST do api.http para a Bianca, depois abrir a rota regional); (c) pendências reais. Não declare a Etapa 3 concluída antes de eu colar o resultado do POST real. Lembre-me de registrar no DIARIO.md o que decidi e aprendi, sem escrever por mim. Não faça commit.

### Prompt 24
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de npm install, pip install, git add/commit/checkout).

Projeto: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um co-piloto que ajuda o gerente Diego Furtado (C0030, loja L004, Aurora Shopping Centro) a preparar o feedback da vendedora Bianca Rocha (C0031) e dá à gerente regional Patrícia Lemos uma visão executiva. A IA (DeepSeek) gera um roteiro de feedback no padrão SBI que o gerente revisa.

Estado atual: Etapas 0 a 3 prontas. O BACKEND (FastAPI, pasta backend/) já expõe a API REST: GET /health; GET /api/vendedores/{loja_id}?mes=AAAA-MM (lista da loja com métricas e comparativo com o time); GET /api/vendedores/{vendedor_id}/historico; POST /api/feedback/gerar (corpo {"vendedor_id": "C0031", "mes_referencia": "2026-10" opcional}); GET /api/regional/desempenho-gerente. Erros sempre no formato {"erro": "mensagem em português"} com status 400 (entrada inválida), 404 (não encontrado), 500 (erro interno ou IA não configurada), 502 (resposta inválida da IA) ou 503 (IA indisponível). CORS permite http://localhost:5173. O FRONTEND (React + Vite, JavaScript, pasta frontend/) ainda está só com a página inicial limpa. Vamos agora fazer a "Etapa 4 – Frontend: estrutura, contexto e serviços de API", dividida em 7 partes.

Tarefa agora (somente leitura):
1. Leia: frontend/package.json, frontend/.env.example, frontend/vite.config.js, frontend/.oxlintrc.json, frontend/src/main.jsx, frontend/src/App.jsx, a lista de arquivos de frontend/src/, COMO-RODAR.md (seção "Usar a API") e backend/api.http.
2. Leia os CONTRATOS do backend para saber o formato exato das respostas: backend/contracts/vendedores.py, backend/contracts/feedback.py, backend/contracts/regional.py, backend/contracts/erros.py (são apenas leitura; não leia o resto do backend).
3. NÃO leia nem aplique frontend/DESIGN.md agora: ele é o guia visual e só será usado na Etapa 5. NÃO leia dados/, prompts/ nem node_modules.
4. Responda só com um resumo de no máximo 10 linhas do que entendeu e as dúvidas. Não escreva código nem crie arquivos.

Convenções para TODAS as partes seguintes:
- SEPARAÇÃO DE RESPONSABILIDADES: o frontend só consome a API REST. Nenhuma regra de cruzamento de dados, nenhuma conta de métrica (ticket médio, P.A., conversão, atingimento) e nenhuma chamada à IA no frontend: os números já chegam calculados do backend (taxas como fração de 0 a 1; null = indisponível). Nenhum `fetch` direto e nenhuma chamada Axios dentro de telas ou componentes: toda comunicação HTTP passa por frontend/src/services/ (um cliente Axios central). Telas e componentes usam o contexto/serviços.
- Stack: React 19 + Vite, JavaScript (não TypeScript), módulos ES, axios e lucide-react já instalados. NÃO adicione dependências novas (nada de react-router, TypeScript, Tailwind, bibliotecas de UI ou de teste) sem eu pedir. Testes de lógica pura com o executor embutido do Node (`node --test`, `node:test` e `node:assert/strict`), arquivos terminados em `.test.js` ao lado do código. Validações padrão: `npm test`, `npm run lint` e `npm run build`, rodados dentro de frontend/.
- A regra do oxlint "react/only-export-components": arquivos de componente exportam só componentes; contexto, hook e constantes ficam em arquivos separados.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código novo, em português (pt-BR) e linguagem simples, para quem não conhece JavaScript/React: cabeçalho (/** ... */) em todo arquivo dizendo para que serve e como se encaixa no projeto; comentário de documentação em toda função, classe e componente (o que faz, recebe, devolve, exemplo curto quando ajudar); comentar cada bloco explicando o PORQUÊ; explicar termos técnicos na primeira vez que aparecem no arquivo, com palavras do dia a dia (ex.: "Promise: uma promessa de resultado que chega depois", "async/await: espera o resultado sem travar a tela", "interceptor: um porteiro que olha toda resposta antes de entregá-la", "reducer: função que recebe o estado atual e uma ação e devolve o novo estado", "Context: um jeito de compartilhar dados entre componentes sem passá-los um a um", "hook: função especial do React, nome começa com use", "AbortController: botão de cancelar uma chamada em andamento"); comentários corretos e atualizados; testes comentados dizendo o que verificam. Não altere código antigo só para comentar.
- Regras do repositório: mudanças pequenas e coesas; NÃO faça git commit/add/push/reset (eu faço os commits); nenhum segredo em arquivos versionados (o frontend usa só VITE_API_URL, que não é segredo); não modifique backend/, dados/, prompts/, README.md, BRIEFING.md, DIARIO.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md, .claude/ nem frontend/DESIGN.md, a menos que o prompt peça explicitamente.
- Leia apenas os arquivos que cada parte citar; não explore o repositório por conta própria. Comandos de shell simples, um por vez, sem one-liners longos com pipes/awk. Se a sessão for interrompida, na retomada rode `git status --short` e só crie o que ainda não existir.
- Não invente fatos sobre o repositório nem sobre a API: confira nos contratos. Se algo do prompt contradisser o código real, pare e me avise.
- Ao final de cada parte informe: arquivos criados/alterados, comandos de validação rodados e o resultado REAL.

Aguarde o primeiro prompt.

### Prompt 25
PARTE 4.1 — Cliente Axios central e tratamento unificado de erros

Leia apenas: frontend/package.json, frontend/.env.example, frontend/src/main.jsx (só o estilo dos comentários) e backend/contracts/erros.py.

Objetivo: a base de toda comunicação HTTP do frontend. Nada de telas.

1. Crie frontend/src/services/erroApi.js:
   - `class ErroApi extends Error` com as propriedades: message (texto em português pronto para mostrar ao usuário), tipo, status (número ou null) e detalhes (null; reservado). tipo é um destes textos: 'rede' (servidor inacessível), 'tempo_esgotado', 'cliente' (resposta 4xx), 'servidor' (resposta 5xx), 'cancelada' (chamada cancelada de propósito), 'validacao' (argumento inválido detectado antes de chamar a API), 'desconhecido'. Exporte também a lista de tipos como constante.
   - `normalizarErro(erro)`: converte qualquer erro do Axios em ErroApi. Regras: se já for ErroApi, devolve igual; cancelamento (axios.isCancel, ou código ERR_CANCELED) => tipo 'cancelada'; resposta do servidor com corpo {"erro": "texto"} => message = esse texto, tipo 'cliente' (4xx) ou 'servidor' (5xx) e status preenchido; resposta sem esse campo => mensagem genérica por faixa de status; sem resposta e código ECONNABORTED ou ETIMEDOUT => 'tempo_esgotado' com mensagem "A resposta demorou mais do que o esperado. Tente novamente."; sem resposta (rede) => 'rede' com "Não foi possível conectar ao servidor. Verifique se o backend está rodando."; qualquer outro => 'desconhecido' com mensagem genérica. NUNCA copie para o erro a URL, os cabeçalhos, o objeto de configuração do Axios nem o corpo bruto da resposta.
   - `erroFoiCancelamento(erro)`: true se for ErroApi de tipo 'cancelada'.
2. Crie frontend/src/services/api.js:
   - `criarClienteApi({ baseURL, timeout = 20000, adapter } = {})`: devolve uma instância de axios.create com baseURL (sem barra no final), timeout, cabeçalho Accept application/json e o adapter opcional (usado só nos testes). Interceptor de RESPOSTA: no sucesso devolve apenas `resposta.data` (os serviços recebem direto os dados); no erro rejeita com normalizarErro(erro).
   - `API_URL`: lê `import.meta.env?.VITE_API_URL` (o `?.` é proposital, para o arquivo também funcionar fora do Vite, nos testes e no script de verificação) e, se vazio, usa "http://localhost:8000" (explique em comentário). `export const api = criarClienteApi({ baseURL: API_URL })`.
3. Em frontend/package.json acrescente SOMENTE o script "test": "node --test" (sem dependências novas). Remova frontend/src/services/.gitkeep (a pasta passa a ter arquivos).
4. Testes em frontend/src/services/api.test.js (node:test) usando um `adapter` falso passado a criarClienteApi (uma função que devolve uma Promise com resposta {status, data, headers: {}, config} ou rejeita com `new AxiosError(mensagem, código, config, requisição, resposta)`; importe AxiosError do axios): sucesso devolve só os dados; 404 com {"erro": "Loja 'L999' não encontrada."} => ErroApi tipo 'cliente', status 404 e a mesma mensagem; 400; 500 com corpo sem campo erro => mensagem genérica; 503 com erro => tipo 'servidor'; sem resposta => 'rede'; código ECONNABORTED => 'tempo_esgotado'; cancelamento via AbortController (signal passado na chamada) => 'cancelada' e erroFoiCancelamento true; baseURL sem barra final; o ErroApi não contém URL nem cabeçalhos (verifique as chaves do objeto).

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação (rode dentro de frontend/ e mostre a saída real): `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria cliente Axios central e tratamento unificado de erros".

### Prompt 26
PARTE 4.2a — vendedorService e regionalService

Pré-requisito: 4.1 concluída. Leia apenas: frontend/src/services/api.js, frontend/src/services/erroApi.js, frontend/src/services/api.test.js (só o estilo do adapter falso), backend/contracts/vendedores.py e backend/contracts/regional.py.

Crie, sem tocar em telas:
1. frontend/src/services/vendedorService.js:
   - `criarVendedorService(cliente = api)` devolve { obterVendedoresPorLoja, obterDetalhesVendedor }; e o arquivo exporta também essas duas funções já ligadas ao cliente padrão (`export const { obterVendedoresPorLoja, obterDetalhesVendedor } = criarVendedorService()`). Explique em comentário por que a função fábrica existe: permitir trocar o cliente HTTP real por um falso nos testes.
   - obterVendedoresPorLoja(lojaId, { mes, signal } = {}) => GET /api/vendedores/{lojaId}, com o parâmetro de consulta `mes` SOMENTE se informado. Devolve os dados da API sem transformar.
   - obterDetalhesVendedor(vendedorId, { signal } = {}) => GET /api/vendedores/{vendedorId}/historico.
   - Em ambos, valide que o identificador é um texto não vazio (após trim); se não for, rejeite com `new ErroApi` de tipo 'validacao' e mensagem em português, SEM chamar a API. Use encodeURIComponent no identificador dentro do caminho.
2. frontend/src/services/regionalService.js: mesmo padrão (fábrica + exportação ligada ao cliente padrão) com `obterDesempenhoGerente({ signal } = {})` => GET /api/regional/desempenho-gerente.
3. Testes (node:test), um arquivo por serviço (vendedorService.test.js e regionalService.test.js), usando criarClienteApi com adapter falso que registra a requisição recebida: confira método, caminho exato (ex.: "/api/vendedores/L004", "/api/vendedores/C0031/historico", "/api/regional/desempenho-gerente"), params ({ mes: '2026-10' } só quando informado), que o signal é repassado, que identificador vazio/só espaços/ não texto rejeita com ErroApi 'validacao' sem chamar o adapter, que "L/004" é codificado no caminho, e que um erro 404 do servidor chega como ErroApi 'cliente' com a mensagem do backend.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação (dentro de frontend/, saída real): `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria serviços de vendedores e da visão regional".

### Prompt 27
PARTE 4.2b — feedbackService

Pré-requisito: 4.2a concluída. Leia apenas: frontend/src/services/vendedorService.js (como modelo), frontend/src/services/erroApi.js, backend/contracts/feedback.py e backend/endpoints/feedback.py (só os comentários e a assinatura da rota, para ver o que a rota pode demorar).

Crie frontend/src/services/feedbackService.js no mesmo padrão (fábrica + exportação ligada ao cliente padrão):
- `gerarFeedback(vendedorId, { mesReferencia, signal } = {})` => POST /api/feedback/gerar com corpo { vendedor_id } e, SOMENTE se mesReferencia for informado (não nulo, não vazio), também mes_referencia. O nome do campo no corpo é snake_case, como o backend espera; no JavaScript o parâmetro é camelCase (explique em comentário). Devolve os dados da API sem transformar (feedback_id, vendedor_id, vendedor_nome, mes_referencia, gerado_em, roteiro com as 4 listas).
- TIMEOUT PRÓPRIO desta chamada: 150000 ms (150 s), definido como constante exportada com comentário explicando: o backend pode chamar a IA até duas vezes (cada chamada pode levar até 60 s) e só então responde; com o timeout padrão de 20 s o frontend desistiria antes da resposta. Passe o timeout na configuração da requisição, sem alterar o timeout padrão do cliente.
- Valide vendedorId (texto não vazio) com ErroApi 'validacao', sem chamar a API. Não valide o formato de mesReferencia no frontend: o backend é a autoridade e devolve 400 com mensagem clara (explique em comentário).
- NÃO faça tentativas automáticas (retry): cada geração consome créditos de IA; comente isso.

Testes em feedbackService.test.js (adapter falso): corpo exato com e sem mesReferencia (sem a chave mes_referencia quando ausente); método POST e caminho; timeout de 150000 na configuração da requisição e timeout padrão do cliente inalterado (20000) nas outras chamadas; signal repassado; vendedorId inválido rejeita sem chamar o adapter; erros 400, 404, 502, 503 e 500 chegam como ErroApi com a mensagem do backend e o tipo certo; uma única chamada ao adapter mesmo quando falha (sem retry).

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação (dentro de frontend/, saída real): `npm test`, `npm run lint`, `npm run build`. NÃO tente chamar a IA de verdade. Não faça commit. Mensagem sugerida: "Cria serviço de geração de feedback".

### Prompt 28
PARTE 4.3a — Constantes e reducer (lógica pura do estado)

Pré-requisito: 4.2b concluída. Leia apenas: frontend/src/services/erroApi.js (para o formato do erro) e backend/contracts/vendedores.py (para saber que dados chegam).

Objetivo: o "cérebro" do estado da aplicação, SEM React e SEM rede, para ser testável com node --test.

1. Crie frontend/src/constantes.js: LOJA_PADRAO_ID = 'L004'; STATUS = { OCIOSO: 'ocioso', CARREGANDO: 'carregando', SUCESSO: 'sucesso', ERRO: 'erro' }; ABAS = { ANOTACOES: 'anotacoes', DADOS: 'dados', FEEDBACK: 'feedback' } (as três abas do gerente); VISOES = { GERENTE: 'gerente', REGIONAL: 'regional' }. Comente cada uma.
2. Crie frontend/src/context/appReducer.js exportando `criarEstadoInicial()`, `TIPOS` (nomes das ações) e `appReducer(estado, acao)`. Forma do estado:
   {
     lojaId,                      // LOJA_PADRAO_ID
     visao,                       // VISOES.GERENTE
     aba,                         // ABAS.DADOS
     vendedores: { status, dados: [], erro: null },   // lista da loja
     vendedorSelecionadoId: null,
     detalhes: { status, dados: null, erro: null },   // histórico do vendedor selecionado
     feedbacks: {},               // por vendedor_id: { status, dados, erro }
     regional: { status, dados: null, erro: null }
   }
   Ações (cada uma com payload simples): vendedores carregando/sucesso(dados = a lista de vendedores da resposta)/erro(mensagem); selecionar vendedor (muda vendedorSelecionadoId e REINICIA detalhes para ocioso; NÃO apaga feedbacks já gerados); detalhes carregando/sucesso/erro, cada uma levando o vendedorId a que pertence; feedback carregando/sucesso/erro por vendedorId; regional carregando/sucesso/erro; mudar aba; mudar visão.
   Regras: (a) resultado de DETALHES para um vendedor que não é mais o selecionado é IGNORADO (evita mostrar dados do vendedor errado quando o usuário clica rápido; explique a "corrida" em comentário); (b) mudar aba aceita só valores de ABAS e mudar visão só de VISOES (valor inválido: devolve o estado sem alterar); (c) o reducer é PURO: nunca altera o estado recebido, devolve um novo objeto, sem efeitos colaterais, sem datas ou chamadas HTTP; (d) ação desconhecida devolve o mesmo estado; (e) um erro guarda só a mensagem em texto (erro.message), nunca o objeto inteiro.
3. Testes em frontend/src/context/appReducer.test.js: estado inicial; fluxo de carregamento de vendedores (sucesso e erro); selecionar vendedor reinicia detalhes mas mantém feedbacks de outros vendedores; detalhes de vendedor não selecionado são ignorados; feedback por vendedor não interfere em outro; aba e visão válidas e inválidas; imutabilidade (compare o estado antigo antes e depois com structuredClone/deepEqual); ação desconhecida.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (explique reducer, estado, imutabilidade e "corrida" de requisições em linguagem simples). Validação (dentro de frontend/, saída real): `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria constantes e reducer do estado da aplicação".

### Prompt 29
PARTE 4.3b — Contexto React: Provider, hook e ações assíncronas

Pré-requisito: 4.3a concluída. Leia apenas: frontend/src/context/appReducer.js, frontend/src/constantes.js, frontend/src/services/vendedorService.js, frontend/src/services/feedbackService.js, frontend/src/services/regionalService.js, frontend/src/services/erroApi.js (só erroFoiCancelamento) e frontend/.oxlintrc.json.

Crie em frontend/src/context/, UM arquivo por papel (a regra only-export-components do oxlint exige isso):
1. appContext.js: `export const AppContext = createContext(null)`.
2. AppProvider.jsx: componente `AppProvider({ children, servicos })` que exporta SÓ o componente. Usa useReducer(appReducer, undefined, criarEstadoInicial). O parâmetro opcional `servicos` (padrão: os serviços reais dos arquivos de services/) permite trocar a rede por versões falsas no futuro; comente por quê. Fornece no valor do contexto (useMemo/useCallback para estabilidade) o `estado` e estas ações, TODAS passando pelos serviços e despachando as ações do reducer:
   - carregarVendedores({ mes } = {}): despacha carregando; chama obterVendedoresPorLoja(estado.lojaId, ...); sucesso => despacha com a lista; erro => despacha a mensagem. Se o erro for cancelamento, NÃO despacha nada.
   - selecionarVendedor(vendedorId): despacha seleção e, em seguida, carrega os detalhes do vendedor (obterDetalhesVendedor) despachando carregando/sucesso/erro com o vendedorId. Cancele a requisição de detalhes anterior ainda em andamento com um AbortController guardado em useRef (ao selecionar outro vendedor), e ignore erros de cancelamento.
   - gerarFeedback(vendedorId, { mesReferencia } = {}): se já houver uma geração em andamento para ESSE vendedor, não dispara outra (evita gastar créditos com duplo clique; comente); despacha carregando/sucesso/erro por vendedor. Sem retry.
   - carregarRegional(): despacha carregando/sucesso/erro; cancela a anterior em andamento.
   - mudarAba(aba), mudarVisao(visao).
   Ao desmontar o Provider, cancele as requisições pendentes (useEffect de limpeza). Em modo de desenvolvimento o React StrictMode monta e desmonta duas vezes: explique em comentário como o cancelamento evita estado inconsistente.
3. useApp.js: hook `useApp()` que devolve o valor do contexto e lança Error em português claro se usado fora do AppProvider.
4. Altere frontend/src/main.jsx SOMENTE para envolver <App /> com <AppProvider> (mantenha StrictMode e os comentários didáticos, atualizando-os).
Não altere App.jsx nesta parte. Sem estilos. Os arquivos de contexto NÃO importam axios nem usam fetch.

Validação (dentro de frontend/, saída real): `npm test` (a suíte anterior continua passando), `npm run lint` (sem warnings novos de only-export-components) e `npm run build`. Explique no final, em 5 linhas, como as telas da Etapa 5 vão usar `useApp()`. Não faça commit. Mensagem sugerida: "Cria contexto React com ações assíncronas ligadas aos serviços".

### Prompt 30
PARTE 4.3b — Contexto React: Provider, hook e ações assíncronas

Pré-requisito: 4.3a concluída. Leia apenas: frontend/src/context/appReducer.js, frontend/src/constantes.js, frontend/src/services/vendedorService.js, frontend/src/services/feedbackService.js, frontend/src/services/regionalService.js, frontend/src/services/erroApi.js (só erroFoiCancelamento) e frontend/.oxlintrc.json.

Crie em frontend/src/context/, UM arquivo por papel (a regra only-export-components do oxlint exige isso):
1. appContext.js: `export const AppContext = createContext(null)`.
2. AppProvider.jsx: componente `AppProvider({ children, servicos })` que exporta SÓ o componente. Usa useReducer(appReducer, undefined, criarEstadoInicial). O parâmetro opcional `servicos` (padrão: os serviços reais dos arquivos de services/) permite trocar a rede por versões falsas no futuro; comente por quê. Fornece no valor do contexto (useMemo/useCallback para estabilidade) o `estado` e estas ações, TODAS passando pelos serviços e despachando as ações do reducer:
   - carregarVendedores({ mes } = {}): despacha carregando; chama obterVendedoresPorLoja(estado.lojaId, ...); sucesso => despacha com a lista; erro => despacha a mensagem. Se o erro for cancelamento, NÃO despacha nada.
   - selecionarVendedor(vendedorId): despacha seleção e, em seguida, carrega os detalhes do vendedor (obterDetalhesVendedor) despachando carregando/sucesso/erro com o vendedorId. Cancele a requisição de detalhes anterior ainda em andamento com um AbortController guardado em useRef (ao selecionar outro vendedor), e ignore erros de cancelamento.
   - gerarFeedback(vendedorId, { mesReferencia } = {}): se já houver uma geração em andamento para ESSE vendedor, não dispara outra (evita gastar créditos com duplo clique; comente); despacha carregando/sucesso/erro por vendedor. Sem retry.
   - carregarRegional(): despacha carregando/sucesso/erro; cancela a anterior em andamento.
   - mudarAba(aba), mudarVisao(visao).
   Ao desmontar o Provider, cancele as requisições pendentes (useEffect de limpeza). Em modo de desenvolvimento o React StrictMode monta e desmonta duas vezes: explique em comentário como o cancelamento evita estado inconsistente.
3. useApp.js: hook `useApp()` que devolve o valor do contexto e lança Error em português claro se usado fora do AppProvider.
4. Altere frontend/src/main.jsx SOMENTE para envolver <App /> com <AppProvider> (mantenha StrictMode e os comentários didáticos, atualizando-os).
Não altere App.jsx nesta parte. Sem estilos. Os arquivos de contexto NÃO importam axios nem usam fetch.

Validação (dentro de frontend/, saída real): `npm test` (a suíte anterior continua passando), `npm run lint` (sem warnings novos de only-export-components) e `npm run build`. Explique no final, em 5 linhas, como as telas da Etapa 5 vão usar `useApp()`. Não faça commit. Mensagem sugerida: "Cria contexto React com ações assíncronas ligadas aos serviços".

### Prompt 31
PARTE 4.4b — Script de verificação, documentação e fechamento da Etapa 4

Pré-requisito: 4.4a concluída. Leia apenas: frontend/package.json, frontend/src/services/api.js, os três arquivos de service (vendedorService.js, regionalService.js, feedbackService.js), COMO-RODAR.md e frontend/.env.example.

1. Crie frontend/scripts/verificar-api.mjs (Node puro, sem dependências novas) que usa criarClienteApi e as FÁBRICAS dos serviços (não o cliente padrão) com a URL vinda de `--url` (padrão http://localhost:8000) e roda em ordem, imprimindo uma linha curta por passo (OK/FALHOU): (a) obterVendedoresPorLoja('L004') devolve 8 vendedores; (b) obterDetalhesVendedor('C0031') devolve resumo de 4 meses; (c) obterDesempenhoGerente() devolve resultado de 4 meses; (d) obterVendedoresPorLoja('L999') rejeita com ErroApi tipo 'cliente', status 404 e mensagem do backend; (e) servidor fora do ar (aponte para uma porta fechada, ex.: http://localhost:9) devolve ErroApi tipo 'rede'. SOMENTE com a flag `--gerar` ele também chama gerarFeedback('C0031') (aviso claro no cabeçalho do script: consome créditos); sem a flag NÃO chama a IA. Saída com código 1 se algum passo falhar. Nunca imprima cabeçalhos nem dados sensíveis. Em frontend/package.json acrescente SOMENTE o script "verificar:api": "node scripts/verificar-api.mjs".
2. Edite COMO-RODAR.md (único arquivo de documentação que você pode editar) acrescentando uma seção "Frontend: comunicação com a API" em português simples: como criar frontend/.env a partir de .env.example (VITE_API_URL), a ordem para subir tudo (backend na porta 8000, depois frontend com npm run dev), o que o painel de verificação mostra em http://localhost:5173, os comandos `npm test`, `npm run verificar:api` e `npm run verificar:api -- --gerar` (avisando que o último gasta créditos), e o que fazer se aparecer "Não foi possível conectar ao servidor" (backend desligado, porta errada, CORS/FRONTEND_ORIGINS no backend).
3. Validação final da Etapa 4 (execute e mostre as saídas reais, sem alterar código):
   - dentro de frontend/: `npm test`, `npm run lint`, `npm run build`;
   - suba o backend (de dentro de backend/, com o python do venv: `uvicorn main:app --port 8000`), rode `npm run verificar:api` e mostre a saída; encerre o backend;
   - varreduras: `grep -rn "fetch(" frontend/src` sem resultados; `grep -rln "axios" frontend/src` deve listar APENAS arquivos dentro de frontend/src/services/ (e testes deles); nenhum arquivo em context/, components/ ou pages/ importa axios; `grep -rn "ticket\|conversao" frontend/src --include=*.jsx` só pode exibir campos recebidos da API, sem fórmulas (liste e confirme);
   - `git status --short`: só frontend/ e COMO-RODAR.md; nenhum .env, node_modules ou dist.
Ao final diga claramente: (a) o que foi validado de verdade; (b) o que depende de mim no navegador, com os passos exatos (subir backend e frontend, abrir http://localhost:5173, ver a lista de vendedores, selecionar a Bianca, ver os detalhes, carregar a visão regional e, só se eu quiser gastar créditos, gerar o feedback); (c) pendências reais. Não declare a Etapa 4 concluída antes de eu confirmar o teste no navegador. Lembre-me de registrar no DIARIO.md o que decidi e aprendi, sem escrever por mim. Não faça commit. Mensagem sugerida: "Adiciona script de verificação da API e documentação do frontend".


## 2026-11-12

### Prompt 1
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de npm/pip install, criar pastas, rodar build que gere arquivos, git add/commit/checkout). Pode apenas LER arquivos e listar pastas.

Vou te passar uma sequência de prompts, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar. Não implemente nada por conta própria.

Projeto: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um co-piloto que ajuda o gerente Diego Furtado (C0030, loja L004, Aurora Shopping Centro) a preparar o feedback da vendedora Bianca Rocha (C0031) com base nos indicadores de vendas e nas anotações dele. A gerente regional Patrícia Lemos acompanha, numa visão executiva, se os feedbacks estão sendo preparados e como a loja está indo. O cenário da demo é o fim de outubro de 2026.

Estado atual: as Etapas 0 a 4 estão prontas.
- backend/ (FastAPI + Pandas + DeepSeek): domínio, DataLoader, LLMService, contratos Pydantic e 5 rotas (GET /health, GET /api/vendedores/{loja_id}, GET /api/vendedores/{vendedor_id}/historico, POST /api/feedback/gerar, GET /api/regional/desempenho-gerente). Não vamos mexer no backend.
- frontend/ (React + Vite, JavaScript): cliente Axios central (src/services/api.js), serviços (vendedorService, feedbackService, regionalService), estado global (src/context/: AppProvider, appReducer, useApp) e um painel TEMPORÁRIO de verificação (src/components/PainelVerificacao.jsx). As pastas src/pages/ e src/components/ ainda não têm telas reais.
Vamos agora fazer a "Etapa 5 – Páginas e componentes de interface", dividida em fatias pequenas.

Leia agora, sem alterar:
1. README.md, BRIEFING.md (seção "Desafio 3 — O feedback que ninguém dá"), COMO-RODAR.md, DIARIO.md e .gitignore.
2. frontend/package.json, frontend/index.html, frontend/src/main.jsx, App.jsx, App.css, index.css, constantes.js.
3. frontend/src/context/ inteiro (AppProvider.jsx, appReducer.js, useApp.js, appContext.js) — preste atenção no formato do estado (criarEstadoInicial), nas ações expostas pelo useApp() e no mapa estado.feedbacks[vendedorId] = { status, dados, erro }.
4. frontend/src/services/ (só os arquivos .js que não são de teste) e frontend/src/components/PainelVerificacao.jsx (para ver como o contexto é usado hoje).
5. frontend/DESIGN.md: o frontmatter (cores, tipografia, rounded, spacing, components) e as seções "Overview", "Colors", "Do's and Don'ts" e "Agent Prompt Guide".
6. Só para conhecer os formatos de resposta da API: backend/contracts/metricas.py, vendedores.py, feedback.py e regional.py. Veja também de relance backend/endpoints/vendedores.py (a lista de vendedores NÃO inclui o gerente; o histórico do gerente C0030 devolve 404).
7. Os cabeçalhos dos CSVs em backend/data/.

Responda só com um resumo curto (máx. 15 linhas) do que entendeu, do estado atual do frontend e das dúvidas que tiver. Aponte também qualquer contradição que encontrar entre o DESIGN.md e a necessidade de contraste/legibilidade (por exemplo, cores de fundo e de texto que não combinam). Não escreva código e não crie arquivos.

Convenções que valem para TODOS os prompts seguintes:
- Separação de responsabilidades: nenhuma regra de negócio, nenhum cruzamento de dados de vendas, nenhum cálculo de métrica (ticket médio, P.A., conversão, atingimento, cobertura, participação) e nenhuma chamada à LLM no frontend. O frontend só mostra o que o backend devolve. Formatar para exibição (R$ 1.234,56; 32,5%; "outubro de 2026") é permitido e NÃO é regra de negócio. Taxas chegam como fração 0–1; valor indisponível chega como null e deve aparecer como "—", nunca como "NaN", "null" ou "undefined".
- As telas NUNCA chamam fetch nem axios diretamente: só leem o estado e chamam as ações do contexto com o hook useApp() (carregarVendedores, selecionarVendedor, gerarFeedback, carregarRegional, mudarAba, mudarVisao). Não altere src/context/ nem src/services/ a menos que o prompt peça. Se faltar algo no contexto, PARE e me avise em vez de contornar.
- Navegação por estado (abas e visões do contexto). NÃO instale react-router nem nenhuma outra dependência (sem Tailwind, sem biblioteca de UI, sem testing-library). Só React, axios e lucide-react, que já estão instalados.
- Visual: siga o frontend/DESIGN.md. Use SOMENTE cores, fontes, raios e espaçamentos declarados nele, guardados como variáveis CSS num lugar só (não espalhe códigos de cor pelos arquivos). Garanta contraste legível (AA) entre texto e fundo. Se o DESIGN.md tiver uma combinação ilegível, escolha outra combinação entre os tokens do próprio arquivo e me avise. Não baixe fontes da internet: use a pilha de fontes do DESIGN.md com os fallbacks.
- Todo texto que a IA gerou (roteiro) e toda anotação são exibidos como TEXTO simples do React. Nunca use dangerouslySetInnerHTML.
- Todos os textos da interface em português (pt-BR), claros e sem jargão. Mensagens de erro humanas, sem stack trace, URL ou dados internos.
- Estados da interface: toda tela que depende da API deve tratar carregando (skeleton ou spinner), erro (mensagem + botão "Tentar de novo" quando fizer sentido) e vazio (mensagem explicando que não há dados).
- Nomes de arquivos e identificadores em português, seguindo o que já existe (ex.: PainelVerificacao.jsx, appReducer.js). Componentes e páginas em src/components/ e src/pages/; um componente por arquivo, com o CSS dele ao lado (ex.: CartaoIndicador.jsx + CartaoIndicador.css), com nomes de classe prefixados para não colidir.
- Testes: o frontend usa `node --test` (sem navegador e sem JSX). Por isso, toda lógica que dê para isolar (formatação, escolha de rótulos, ordenação) deve ficar em funções puras em arquivos .js, com testes .test.js ao lado. Os componentes são validados com `npm run build` e `npm run lint`. Os testes nunca chamam a internet.
- Comandos de validação (de dentro de frontend/): `npm run build`, `npm run lint` e `npm test`. A suíte existente deve continuar passando.
- Regras do repositório: mudanças pequenas e coesas; NÃO faça git commit/add/push/amend/reset (o commit é feito por mim); nunca coloque chaves ou segredos em arquivos versionados; não modifique backend/, dados/, prompts/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md, .claude/ nem COMO-RODAR.md, a menos que o prompt peça explicitamente. O registro dos prompts é feito por mim/pela ferramenta.
- Não invente dados nem fatos; confira no código, nos contratos e nos CSVs. Se algo do prompt contradisser o código, pare e me avise.
- Comandos de shell simples, um por vez, sem one-liners longos com pipes/awk. Se a sessão for interrompida, na retomada verifique `git status --short` e só crie o que ainda não existir.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: todo código que você escrever (JavaScript, JSX, CSS e testes) deve ser bem comentado, em português (pt-BR) e em linguagem simples, para que qualquer pessoa, mesmo sem conhecer a linguagem, entenda o que acontece em cada parte. Regras:
  1. Todo arquivo começa com um comentário de 2 a 4 linhas dizendo, em palavras simples, para que serve o arquivo e como ele se encaixa no projeto (em CSS, use /* ... */ no topo; em JSX, o comentário de cabeçalho fica antes dos imports).
  2. Todo componente e toda função tem comentário de bloco (/** ... */) explicando: o que faz, o que recebe (props ou parâmetros), o que devolve e, quando ajudar, um exemplo curto (ex.: "formatarMoeda(1234.5) devolve 'R$ 1.234,50'").
  3. Dentro das funções e componentes, comente cada bloco lógico explicando o que está sendo feito e POR QUÊ, não apenas repetindo o código. Dentro do JSX use {/* comentário */}. Evite comentários óbvios linha a linha; prefira explicar a intenção.
  4. Explique termos técnicos na primeira vez em que aparecerem no arquivo, com palavras do dia a dia (ex.: "props: os dados que um componente recebe de quem o usa", "estado: informação que muda e faz a tela se atualizar", "hook: função do React que começa com 'use' e dá superpoderes ao componente", "useEffect: roda um código depois que a tela aparece", "skeleton: um esboço cinza que aparece no lugar do conteúdo enquanto ele carrega", "variável CSS: um valor com nome, como --cor-primaria, reutilizado em vários lugares", "aria-label: texto lido por leitores de tela").
  5. Em CSS, comente o que cada grupo de regras estiliza e por que o valor foi escolhido (ex.: "cor com contraste suficiente para leitura").
  6. Cálculos e regras de exibição ficam escritos em palavras (ex.: "mostra '—' quando o valor é nulo, porque a API manda null quando não há dados").
  7. Nos testes, comente o que cada teste verifica e por que aquele resultado é o esperado.
  8. Comentários devem ser corretos e estar sempre atualizados com o código; se alterar o código, atualize o comentário. Nada de comentários em inglês, jargão sem explicação ou textos longos demais: frases curtas e diretas.
  9. Não altere código de fatias anteriores só para adicionar comentários, a não ser que o prompt peça.
- Ao fim de cada prompt, informe: arquivos criados/alterados, comandos de validação executados e o resultado REAL. Não declare algo validado sem ter executado. Coisas que só dá para ver no navegador (aparência, clique) você NÃO consegue confirmar: diga isso e me dê o passo a passo para eu conferir.

Aguarde o primeiro prompt. Agora responda só com o resumo e as dúvidas, sem modificar nada.

### Prompt 2
FATIA 5.1 — Tokens de design e estilos base (Etapa 5)

Leia apenas: frontend/DESIGN.md (frontmatter e seções Colors, Typography, Layout, Shapes, Components e Do's and Don'ts), frontend/src/index.css, frontend/src/App.css e frontend/src/main.jsx.

Objetivo: criar a base visual do app (cores, fonte, espaçamentos, raios e classes de uso comum) num único lugar, sem criar nenhuma tela ainda.

Tarefas:
1. Crie frontend/src/estilos/tokens.css com variáveis CSS (:root) para: cores (primária, primária ativa, tinta/ink, texto, texto suave, borda, fundo da página, superfície suave, texto sobre primária, texto sobre fundo escuro, e as cores de estado — sucesso, alerta, perigo — apenas se existirem no DESIGN.md; se não existirem, escolha entre os tokens declarados e explique), a família de fonte (com fallbacks do DESIGN.md), a escala tipográfica usada no app, a escala de espaçamentos e a escala de raios. Use SOMENTE valores do DESIGN.md.
2. Decida e documente em comentário, no próprio tokens.css, quais combinações de fundo e texto serão usadas e por quê. O DESIGN.md manda o fundo da página ser o roxo (#8328D9) e o texto principal ser o #17171C, que tem contraste ruim entre si. Proposta: fundo da página roxo; painéis e cartões em superfície suave (#F5EFFB) com texto ink; barra lateral e cabeçalho em tom escuro do próprio DESIGN.md com texto branco; botão principal em #00E6B8 com texto #111111. Se achar uma combinação melhor entre os tokens do arquivo, use-a e me conte. Confira o contraste de cada par e anote em comentário o resultado aproximado da razão de contraste (mínimo 4,5:1 para texto normal).
3. Crie frontend/src/estilos/base.css com: reset mínimo (box-sizing, margens), estilo do body e títulos (h1 a h4) usando os tokens, estilo de foco visível para teclado (:focus-visible com contorno bem visível), e classes utilitárias de uso geral com prefixo "ui-": ui-cartao (superfície com borda e raio), ui-botao-primario, ui-botao-secundario (ambos com estados hover, foco e desabilitado), ui-texto-suave e ui-visualmente-oculto (esconde da tela mas continua legível por leitores de tela).
4. Inclua um bloco @media (prefers-reduced-motion: reduce) em base.css que desliga animações e transições do app.
5. Importe tokens.css e base.css em frontend/src/main.jsx (antes do index.css). Reduza o frontend/src/index.css ao que ainda faltar (ou deixe só o que não conflita). NÃO apague nem altere frontend/src/App.css: o painel temporário ainda depende dele e deve continuar funcionando.

Não crie componentes, páginas nem outros arquivos. Não instale dependências.

Validação (execute de verdade): `npm run build` e `npm run lint` em frontend/; `npm test` (a suíte existente continua passando); `git status --short` deve mostrar só: estilos/tokens.css, estilos/base.css, main.jsx e index.css. Diga que a aparência final só pode ser conferida por mim no navegador (`npm run dev`, abrir http://localhost:5173): o painel temporário deve continuar abrindo sem erros no console.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo arquivo criado ou alterado (cabeçalho do arquivo, comentário em cada grupo de regras CSS explicando o que estiliza e por quê, termos como "variável CSS", ":root" e ":focus-visible" explicados em palavras simples). Antes de terminar, releia o que você escreveu e confirme que uma pessoa que não conhece CSS entenderia cada parte.

Não faça commit. Mensagem de commit sugerida: "Cria tokens de design e estilos base do frontend".

### Prompt 3
FATIA 5.2 — Formatadores de exibição, com testes (Etapa 5)

Leia apenas: backend/contracts/metricas.py, vendedores.py, feedback.py e regional.py (só os campos e descrições), frontend/src/constantes.js e frontend/src/services/vendedorService.test.js (só o estilo dos testes).

Objetivo: criar funções puras que transformam os valores da API em texto para a tela. Nada de React aqui. Isso é FORMATAÇÃO de exibição, não regra de negócio: nenhuma função pode calcular métrica; elas só deixam o número bonito.

Tarefas:
1. Crie frontend/src/utilitarios/formatadores.js com funções exportadas, todas devolvendo "—" (travessão) quando o valor for null, undefined, NaN ou não for do tipo esperado:
   - formatarMoeda(valor): reais no padrão brasileiro. Ex.: 1234.5 → "R$ 1.234,50". Use Intl.NumberFormat com 'pt-BR'.
   - formatarNumero(valor, casas = 2): decimal pt-BR. Ex.: 1.2 → "1,20".
   - formatarInteiro(valor): inteiro com separador de milhar. Ex.: 3250 → "3.250".
   - formatarPercentual(fracao, casas = 1): recebe fração 0–1 e mostra em %. Ex.: 0.325 → "32,5%". A multiplicação por 100 é só exibição.
   - formatarDiferencaPercentual(valor): sinal explícito. Ex.: 12.3 → "+12,3%", -8 → "−8,0%". Pergunte-se no código (comentário) se o backend manda isso em pontos percentuais ou fração: confira na descrição do campo diferenca_percentual em backend/contracts/metricas.py e siga exatamente o que está escrito lá; se a descrição for ambígua, PARE e me avise.
   - formatarMes(mesAAAAMM): "2026-10" → "outubro de 2026". Entrada inválida → "—".
   - formatarData(valor): aceita "AAAA-MM-DD" e devolve "10/10/2026". Atenção: não use new Date("2026-10-10") direto, porque o fuso horário pode mostrar o dia anterior; monte a data a partir das partes do texto.
   - formatarDataHora(valor): aceita ISO com hora (ex.: "2026-11-11T14:30:00") e devolve "11/11/2026 às 14:30".
   - rotuloMetrica(nome): "ticket_medio" → "Ticket médio", "pecas_por_atendimento" → "Peças por atendimento (P.A.)", "conversao" → "Taxa de conversão". Nome desconhecido → devolve o próprio texto.
   - rotuloSituacaoMetrica(situacao): "acima" → "Acima da média do time", "abaixo" → "Abaixo da média do time", "na_media" → "Na média do time", "indisponivel" → "Sem dados para comparar".
   - rotuloSituacaoAcompanhamento(situacao): "com_roteiro" → "Roteiro preparado", "sem_roteiro" → "Sem roteiro".
2. Crie frontend/src/utilitarios/formatadores.test.js (node --test, com node:test e node:assert) cobrindo: cada função com valor normal, com null/undefined/NaN, e os casos de borda (zero, negativo, mês inválido, data com fuso). Para a formatação com Intl, lembre que o espaço entre "R$" e o número pode ser um espaço especial (não separável): escreva os testes de forma que não quebrem por isso (por exemplo, normalizando espaços antes de comparar) e explique em comentário por quê.

Não crie componentes nem altere outros arquivos.

Validação (execute de verdade): `npm test` (mostre quantos testes passaram), `npm run lint`, `npm run build`, `git status --short` (só utilitarios/ novos).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo arquivo criado: cabeçalho, comentário de bloco em cada função com exemplo de entrada e saída, termos como "função pura", "Intl.NumberFormat", "NaN" e "fuso horário" explicados em palavras do dia a dia, e cada teste dizendo o que verifica e por que o resultado é o esperado.

Não faça commit. Mensagem de commit sugerida: "Adiciona formatadores de exibição com testes".

### Prompt 4
FATIA 5.3a — Componentes de estado: carregando, erro e vazio (Etapa 5)

Pré-requisito: fatias 5.1 e 5.2 concluídas. Leia apenas: frontend/src/estilos/tokens.css, frontend/src/estilos/base.css, frontend/src/constantes.js e o início de frontend/src/components/PainelVerificacao.jsx (só para ver o padrão de comentários).

Objetivo: criar três componentes reutilizáveis para os estados que toda tela com API precisa mostrar. Eles NÃO usam o contexto: recebem tudo por props e podem ser usados em qualquer página.

Tarefas (arquivos em frontend/src/components/, cada .jsx com seu .css ao lado):
1. EstadoCarregando.jsx — props: titulo (padrão "Carregando…"), descricao (opcional), linhas (quantidade de linhas de esqueleto, padrão 3) e variante ("texto" ou "cartao"). Mostra um skeleton (blocos cinza com animação suave de brilho, desligada por prefers-reduced-motion) e um texto legível. Acessibilidade: container com role="status", aria-live="polite" e aria-busy="true"; o texto do titulo é lido por leitores de tela.
2. EstadoErro.jsx — props: mensagem (texto já amigável vindo do estado), aoTentarDeNovo (função opcional) e rotuloBotao (padrão "Tentar de novo"). Mostra ícone (lucide-react), título "Algo não saiu como esperado", a mensagem e, se aoTentarDeNovo existir, o botão. Container com role="alert". Nunca mostra o objeto de erro inteiro: só o texto recebido.
3. EstadoVazio.jsx — props: titulo, descricao e icone opcional (componente do lucide-react). Mostra uma mensagem centralizada explicando por que não há dados (ex.: "Ainda não há anotações para esta pessoa.").

Regras: sem chamadas HTTP, sem useApp, sem lógica de negócio. Cores e espaçamentos só via variáveis CSS dos tokens. Não use dangerouslySetInnerHTML.

Não altere App.jsx, o contexto, os serviços nem o PainelVerificacao. Os componentes ainda não aparecem na tela (serão usados nas próximas fatias).

Validação (execute de verdade): `npm run build`, `npm run lint`, `npm test`, `git status --short` (só os 6 arquivos novos). Diga que não dá para ver os componentes no navegador ainda.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: cabeçalho em cada arquivo, comentário de bloco explicando o que cada componente recebe (props) e devolve, comentários {/* */} no JSX explicando cada parte e por que existe, e termos como "componente", "props", "skeleton", "role" e "aria-live" explicados em palavras simples. Releia no fim e confirme que alguém sem experiência em React entenderia.

Não faça commit. Mensagem de commit sugerida: "Cria componentes de estado carregando, erro e vazio".

### Prompt 5
FATIA 5.3b — Cartão de indicador e selo de situação (Etapa 5)

Pré-requisito: 5.1, 5.2 e 5.3a concluídas. Leia apenas: frontend/src/utilitarios/formatadores.js, frontend/src/estilos/tokens.css, frontend/src/estilos/base.css, frontend/src/components/EstadoVazio.jsx (só o estilo) e backend/contracts/metricas.py (descrição de MetricaComparadaDTO).

Objetivo: criar os dois componentes visuais que mostram um número com seu significado.

Tarefas (em frontend/src/components/, cada .jsx com .css ao lado):
1. Selo.jsx — um selo pequeno (badge) com texto curto e um tom: "neutro", "positivo", "atencao" ou "negativo". Props: texto, tom (padrão "neutro") e icone opcional (lucide-react). A cor NUNCA é a única forma de passar a informação: sempre há texto (e, se possível, ícone). Use as cores de estado dos tokens, e a cor primária só para destaque de ação (não para estado).
2. CartaoIndicador.jsx — um cartão que mostra uma métrica. Props: rotulo (ex.: "Ticket médio"), valorFormatado (texto já formatado, ex.: "R$ 150,20"), detalhe opcional (linha pequena, ex.: "Média do time: R$ 210,00") e situacao opcional ("acima" | "abaixo" | "na_media" | "indisponivel"). Se houver situacao, mostra um Selo com o texto de rotuloSituacaoMetrica. Mapeamento de tom (decisão só de exibição): acima → positivo; abaixo → atencao; na_media → neutro; indisponivel → neutro. Explique em comentário que "abaixo" usa tom de atenção e não de erro, porque estar abaixo da média do time é um ponto de desenvolvimento, não uma falha.
3. Coloque o mapeamento situação → tom em uma função pura, em frontend/src/utilitarios/tomDaSituacao.js, com testes em tomDaSituacao.test.js (todas as 4 situações e um valor desconhecido, que deve virar "neutro").

Regras: o CartaoIndicador NÃO calcula nada e NÃO formata: recebe o texto pronto. Sem useApp, sem HTTP.

Validação (execute de verdade): `npm test` (mostre o total), `npm run lint`, `npm run build`, `git status --short`.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todos os arquivos (cabeçalho, comentário de bloco com as props, {/* */} no JSX, comentários no CSS, testes explicando o que verificam). Termos novos ("props", "badge", "tom") explicados em palavras simples.

Não faça commit. Mensagem de commit sugerida: "Cria cartão de indicador e selo de situação".

### Prompt 6
FATIA 5.4a — Barra lateral: lista de colaboradores (Etapa 5)

Pré-requisito: 5.1 a 5.3b concluídas. Leia apenas: frontend/src/context/AppProvider.jsx (só as ações expostas), frontend/src/context/appReducer.js (formato de estado.vendedores e estado.vendedorSelecionadoId), frontend/src/context/useApp.js, frontend/src/constantes.js, frontend/src/components/EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, frontend/src/components/PainelVerificacao.jsx (só para ver como ele usa carregarVendedores e selecionarVendedor) e backend/contracts/vendedores.py (VendedorResumoDTO).

Objetivo: criar a lista de colaboradores que fica na lateral. Ela só mostra e seleciona; não navega entre abas ainda (isso é a fatia 5.4b).

Tarefas:
1. Em frontend/src/constantes.js ACRESCENTE, sem alterar o que existe, a constante VENDEDOR_FOCO_ID = 'C0031' com comentário explicando que é a vendedora Bianca Rocha, usada no cenário da demo apenas para já vir selecionada quando a lista carregar (é uma conveniência de tela, não uma regra de negócio).
2. Crie frontend/src/components/ListaColaboradores.jsx:
   - props: nenhuma obrigatória; usa useApp() para ler estado.vendedores (status, dados, erro) e estado.vendedorSelecionadoId e para chamar selecionarVendedor e carregarVendedores.
   - Um useEffect que chama carregarVendedores() uma vez, quando o status ainda for "ocioso" (comente por que a condição evita pedir duas vezes, já que o StrictMode do React roda efeitos em dobro em desenvolvimento).
   - Um segundo useEffect: quando a lista chegar com sucesso, nenhum vendedor estiver selecionado e existir um item com vendedor_id igual a VENDEDOR_FOCO_ID, chama selecionarVendedor(VENDEDOR_FOCO_ID). Se a Bianca não estiver na lista, não seleciona ninguém.
   - Estados: carregando → EstadoCarregando (variante "texto", 4 linhas); erro → EstadoErro com botão que chama carregarVendedores(); lista vazia → EstadoVazio.
   - Sucesso: uma lista (ul) de botões, um por colaborador, mostrando nome e cargo. O item selecionado tem aria-current="true" e destaque visual claro (não só cor: use também borda/ícone). Cada botão chama selecionarVendedor(vendedor_id). Navegável por teclado (Tab e Enter/Espaço).
   - Mostre apenas o que a API devolveu (a lista não inclui o gerente). Não ordene nem filtre por conta própria além da ordem recebida.
3. Crie ListaColaboradores.css com os estilos (tokens, foco visível, área de clique mínima de 44px de altura).

Ainda NÃO ligue o componente em App.jsx e não mexa no PainelVerificacao.

Validação (execute de verdade): `npm run build`, `npm run lint`, `npm test`, `git status --short` (constantes.js alterado + 2 arquivos novos). Se o backend estiver no ar, rode também `npm run verificar:api` e diga o resultado; se não estiver, diga que não foi possível. Explique que a conferência visual será feita depois da fatia 5.4b.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código novo (cabeçalho, comentário de bloco, cada useEffect explicado com o PORQUÊ, "hook", "useEffect", "aria-current" e "StrictMode" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Cria lista de colaboradores da barra lateral".

### Prompt 7
FATIA 5.4b — Layout principal e navegação (Etapa 5)

Pré-requisito: 5.4a concluída. Leia apenas: frontend/src/App.jsx, frontend/src/App.css, frontend/src/main.jsx, frontend/src/context/AppProvider.jsx (só as ações), frontend/src/constantes.js, frontend/src/components/ListaColaboradores.jsx e frontend/src/components/PainelVerificacao.jsx (só para ver como ele troca aba e visão).

Objetivo: montar a casca do app: cabeçalho, barra lateral com a lista e as abas, e a área central que mostra o conteúdo conforme a visão e a aba escolhidas. As páginas reais virão nas próximas fatias; por enquanto a área central mostra um aviso "Em construção" para cada uma.

Tarefas (em frontend/src/components/, cada .jsx com .css ao lado):
1. Cabecalho.jsx — título "Feedback Inteligente", subtítulo "Co-piloto de feedback para a liderança da Rede Aurora" e o nome da loja quando disponível em estado.vendedores (confira o que a API devolve no contrato; se o nome da loja não estiver no estado, não invente: mostre só o título). Inclui o alternador de visão com dois botões, "Gerente" e "Regional", que chamam mudarVisao(VISOES.GERENTE) e mudarVisao(VISOES.REGIONAL). O botão da visão ativa tem aria-pressed="true".
2. NavegacaoAbas.jsx — as três abas "Anotações", "Dados" e "Feedback" (valores de ABAS), que chamam mudarAba. Use a semântica de abas: role="tablist" no container, role="tab" e aria-selected em cada aba, role="tabpanel" na área central (ligada à aba por aria-labelledby/aria-controls), e navegação por setas esquerda/direita. As abas só aparecem na visão do gerente.
3. BarraLateral.jsx — junta o título "Equipe", a ListaColaboradores e, abaixo do colaborador selecionado, a NavegacaoAbas (a barra lateral é onde se escolhe a pessoa e o que ver dela). Só aparece na visão do gerente; na visão regional ela não é exibida.
4. AreaCentral.jsx — decide o que mostrar: visão regional → aviso "Visão regional em construção"; visão do gerente sem ninguém selecionado → EstadoVazio pedindo para escolher um colaborador; visão do gerente com alguém selecionado → um aviso "Aba <nome da aba> em construção" para cada aba. Comente que, nas próximas fatias, cada aviso será trocado pela página real, e que é nesta arquivo que isso será ligado.
5. Reescreva frontend/src/App.jsx para renderizar Cabecalho + BarraLateral + AreaCentral num layout de duas colunas (grid) que, em telas estreitas (menos de 768px), empilha tudo numa coluna. Use o hook useApp() só onde precisar. NÃO renderize mais o PainelVerificacao no App (o arquivo dele continua existindo; será removido na fatia 5.10). Atualize o comentário de cabeçalho do App.jsx, que hoje diz que ele mostra o painel temporário.
6. Em App.css, NÃO apague as regras do painel temporário (ficarão até a 5.10); acrescente apenas as regras do layout principal, ou crie App.layout.css se preferir separar. Explique a escolha em comentário.

Regras: sem react-router, sem fetch/axios nas telas, sem lógica de negócio. Uma única fonte de verdade para aba e visão: o estado do contexto.

Validação (execute de verdade): `npm run build`, `npm run lint`, `npm test`, `git status --short`. Suba `npm run dev` em background, confirme com curl que http://localhost:5173 responde 200 com o título "Feedback Inteligente" no HTML e encerre o processo. Depois me dê o passo a passo para eu conferir no navegador (backend no ar + `npm run dev`): lista de colaboradores aparece, Bianca já vem selecionada, as três abas trocam o aviso, o alternador Gerente/Regional troca o layout e não há erros no console.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo arquivo (cabeçalho, comentário de bloco com props/uso do contexto, {/* */} no JSX, comentários no CSS explicando o layout em grade, e termos como "grid", "role", "aria-selected" e "layout responsivo" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Cria layout principal com cabeçalho, barra lateral e abas".

### Prompt 8
FATIA 5.5 — Aba Dados: indicadores, comparativo com o time e resumo mensal (Etapa 5)

Pré-requisito: 5.4b concluída. Leia apenas: frontend/src/components/AreaCentral.jsx, CartaoIndicador.jsx, Selo.jsx, EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, frontend/src/utilitarios/formatadores.js, frontend/src/context/appReducer.js (formato de estado.detalhes e dos TIPOS de detalhes) e backend/contracts/metricas.py e vendedores.py (HistoricoVendedorResposta, MetricasDTO, MetricaComparadaDTO, ResumoMensalDTO).

Objetivo: criar a página da aba "Dados" do colaborador selecionado. Tudo vem pronto do backend (estado.detalhes.dados); a página só organiza e formata.

Tarefas:
1. Crie frontend/src/pages/PaginaDados.jsx (+ PaginaDados.css). Lê estado.detalhes e estado.vendedorSelecionadoId com useApp().
   - Carregando → EstadoCarregando (variante "cartao"); erro → EstadoErro com botão que chama selecionarVendedor(estado.vendedorSelecionadoId) para tentar de novo; sem dados → EstadoVazio.
   - Seção "Indicadores do período": três CartaoIndicador (Ticket médio em reais, P.A. com 2 casas, Taxa de conversão em %), usando os valores de detalhes.dados.metricas e formatadores. Em cada cartão, use o item correspondente de detalhes.dados.comparativo (campo nome) para preencher situacao e o detalhe "Média do time: …" (media_time formatada do mesmo jeito da métrica) e, se vier, "Posição X de Y" (posicao e total_vendedores). Se uma métrica não tiver item no comparativo, mostra o cartão sem selo.
   - Seção "Totais do período": valor vendido, vendas, peças e atendimentos, em formato de lista de termos (dl) simples.
   - Seção "Resultado por mês": uma tabela acessível (caption, th scope) com uma linha por item de resumo_mensal: mês (formatarMes), valor vendido, vendas, ticket médio, P.A., conversão, meta, atingimento da meta. Se mes_parcial for true, mostra um Selo "Mês parcial" ao lado do mês (o mês ainda não terminou). Em telas estreitas a tabela rola na horizontal dentro do próprio container, sem quebrar a página.
   - Nenhuma conta: atingimento, ticket e demais valores são exibidos como vêm; null vira "—".
2. Se precisar de lógica de apoio (por exemplo, achar o item do comparativo por nome, ou montar o texto "Posição 3 de 8"), faça em funções puras em frontend/src/utilitarios/dadosDoVendedor.js, com testes em dadosDoVendedor.test.js (sucesso, item ausente, valores null).
3. Em AreaCentral.jsx, troque o aviso "Aba Dados em construção" pela PaginaDados (altere só esse trecho e o import).

Validação (execute de verdade): `npm test` (mostre o total), `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador com a Bianca selecionada: os três cartões aparecem; os números batem com `curl http://localhost:8000/api/vendedores/C0031/historico`; a conversão da Bianca aparece como acima da média e o P.A. como abaixo (confira no JSON antes de afirmar); a tabela mensal tem os meses do histórico com o mês parcial sinalizado; nada aparece como "NaN" ou "undefined".

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, cada seção do JSX comentada com o que mostra e de onde vem o dado, termos como "tabela acessível", "scope" e "overflow" explicados em palavras simples, e os testes dizendo o que verificam).

Não faça commit. Mensagem de commit sugerida: "Cria página da aba Dados".

### Prompt 9
FATIA 5.6 — Aba Anotações (Etapa 5)

Pré-requisito: 5.5 concluída. Leia apenas: frontend/src/components/AreaCentral.jsx, EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, Selo.jsx, frontend/src/pages/PaginaDados.jsx (só o estilo), frontend/src/utilitarios/formatadores.js e backend/contracts/vendedores.py (AnotacaoDTO e HistoricoVendedorResposta).

Objetivo: mostrar o que o gerente escreveu sobre a pessoa selecionada e sobre o time, do jeito que ele escreveu.

Tarefas:
1. Crie frontend/src/pages/PaginaAnotacoes.jsx (+ PaginaAnotacoes.css). Lê estado.detalhes (via useApp), com os mesmos tratamentos de carregando, erro (botão que chama selecionarVendedor de novo) e vazio da PaginaDados.
   - Seção "Anotações sobre <nome>": lista de detalhes.dados.anotacoes, da mais recente para a mais antiga (ordene por data, em função pura), cada uma com a data (formatarData) e o texto exatamente como veio (sem corrigir, sem resumir, sem cortar). Cada item é um elemento <article> ou <li> com <time dateTime="…"> para a data.
   - Seção "Anotações sobre o time": lista de detalhes.dados.anotacoes_do_time, no mesmo formato, com uma frase curta explicando que são observações sobre a loja toda e podem ajudar a entender o contexto.
   - Sem anotações em uma seção → EstadoVazio com texto próprio (ex.: "Ainda não há anotações sobre esta pessoa.").
   - Uma observação curta e fixa no topo: "Estas são as suas anotações originais. O roteiro de feedback usa o que está escrito aqui, junto com os números." (é um texto de orientação, sem prometer nada além disso).
2. A função de ordenação (mais recente primeiro; datas iguais mantêm a ordem recebida) fica em frontend/src/utilitarios/ordenarAnotacoes.js, com testes (lista vazia, datas fora de ordem, datas iguais, a entrada não pode ser alterada).
3. Em AreaCentral.jsx, troque o aviso da aba Anotações pela PaginaAnotacoes (só esse trecho e o import).

Regras: texto de anotação é exibido como texto simples (nunca HTML). Não altere o texto das anotações.

Validação (execute de verdade): `npm test` (total), `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir com a Bianca: as anotações dela aparecem da mais recente (08/10/2026, sobre o cinto no caixa) para a mais antiga (06/08/2026), e as do time aparecem em outra seção. Confira no CSV backend/data/anotacoes_gerente.csv antes de afirmar quantas são.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, explicação do porquê de cada decisão — por exemplo, por que ordenar sem alterar a lista original — e "elemento time/dateTime" explicado em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Cria página da aba Anotações".

### Prompt 10
FATIA 5.7a — Aba Feedback: botão de gerar e estados da geração (Etapa 5)

Pré-requisito: 5.6 concluída. Leia apenas: frontend/src/components/AreaCentral.jsx, EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, Selo.jsx, frontend/src/context/AppProvider.jsx (ação gerarFeedback), frontend/src/context/appReducer.js (formato de estado.feedbacks[vendedorId]), frontend/src/services/feedbackService.js (comentário do timeout), frontend/src/utilitarios/formatadores.js e backend/contracts/feedback.py e vendedores.py (FeedbackGerarResposta, FeedbackPreparadoDTO).

Objetivo: criar a página da aba "Feedback" com tudo, menos a exibição bonita do roteiro (que é a fatia 5.7b). Aqui entram o seletor de mês, o botão de gerar e os estados visuais de espera, erro e sucesso.

Tarefas:
1. Crie frontend/src/pages/PaginaFeedback.jsx (+ PaginaFeedback.css). Lê com useApp(): estado.vendedorSelecionadoId, estado.detalhes e estado.feedbacks[vendedorId] (pode ser undefined se nunca gerou).
2. Bloco "Gerar roteiro de feedback":
   - Seletor de período (select com label): a opção "Todo o histórico" (sem mês) e uma opção por item de detalhes.dados.resumo_mensal (texto com formatarMes, e "(parcial)" quando mes_parcial for true). Pré-selecione o último mês com mes_parcial igual a false; se não houver, "Todo o histórico". Escolher o pré-selecionado é só apresentação, não é cálculo: comente isso.
   - Botão primário "Gerar roteiro" que chama gerarFeedback(vendedorId, { mesReferencia }) (sem mesReferencia quando for "Todo o histórico"). Desabilitado enquanto o status for "carregando" (o contexto já ignora cliques duplicados; a desabilitação é para o usuário entender).
   - Aviso fixo e claro perto do botão: "A geração usa IA, consome créditos e pode levar até alguns minutos. Revise tudo antes de usar: você continua sendo o dono da conversa."
3. Estados do resultado, em uma área com aria-live="polite":
   - ocioso (nunca gerou) → EstadoVazio explicando o que será gerado: pontos positivos, pontos de melhoria, possíveis motivos e um roteiro de conversa (sem prometer resultado).
   - carregando → EstadoCarregando (variante "cartao", com 4 blocos de esqueleto, um para cada seção) com texto "Preparando o roteiro… isso pode levar de 10 segundos a alguns minutos." e uma indicação de que não precisa clicar de novo.
   - erro → EstadoErro com a mensagem do estado e botão "Tentar de novo" que chama gerarFeedback novamente com o mesmo período. NÃO faça nova tentativa automática (cada geração gasta créditos).
   - sucesso → por enquanto mostre apenas um resumo simples: nome, período (formatarMes ou "Todo o histórico"), data/hora (formatarDataHora) e, abaixo, as 4 listas em texto simples sem estilo especial. O visual final do roteiro entra na 5.7b.
4. Bloco "Roteiros já preparados" com a lista de detalhes.dados.feedbacks_preparados (período e data/hora de cada um), ou EstadoVazio se vier vazia. Escreva um texto curto explicando: "roteiro preparado" não significa "feedback realizado": é só o rascunho gerado. Atenção: depois de gerar, o contexto NÃO recarrega esse histórico; não altere o contexto para isso. Se isso ficar estranho na tela, anote como pendência no relatório final.
5. A lógica de montar as opções do seletor e escolher o padrão fica em função pura em frontend/src/utilitarios/opcoesDePeriodo.js, com testes (sem meses, só mês parcial, vários meses com o último parcial, entrada inválida).
6. Em AreaCentral.jsx, troque o aviso da aba Feedback pela PaginaFeedback (só esse trecho e o import).

Importante sobre a IA: o roteiro é texto simples. Nada de HTML. Não monte prompt nem valide a qualidade do roteiro no frontend.

Validação (execute de verdade): `npm test` (total), `npm run lint`, `npm run build`, `git status --short`. NÃO chame a geração real (gasta créditos). Me dê o passo a passo para eu conferir no navegador SEM gastar crédito: abrir a aba Feedback, ver o estado ocioso, o seletor com os meses e o aviso; para testar o estado de erro, suba o frontend com o backend desligado e clique em "Gerar roteiro" (deve aparecer erro amigável e o botão "Tentar de novo"). A geração real fica por minha conta.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, cada estado da tela explicado, "aria-live", "select" e "estado derivado" explicados em palavras simples, testes dizendo o que verificam).

Não faça commit. Mensagem de commit sugerida: "Cria página da aba Feedback com geração e estados".

### Prompt 11
FATIA 5.7b — Visualizador do roteiro de feedback (Etapa 5)

Pré-requisito: 5.7a concluída. Leia apenas: frontend/src/pages/PaginaFeedback.jsx, frontend/src/components/Selo.jsx, frontend/src/estilos/tokens.css, frontend/src/estilos/base.css, frontend/src/utilitarios/formatadores.js e backend/contracts/feedback.py (FeedbackRoteiroDTO e FeedbackGerarResposta; leia também as descrições dos campos para saber o que cada lista significa).

Objetivo: exibir o roteiro gerado pela IA de forma clara, bem organizada e fácil de usar durante a conversa, num layout expandido (aproveitando a largura da área central).

Tarefas:
1. Crie frontend/src/components/VisualizadorRoteiro.jsx (+ VisualizadorRoteiro.css). Props: roteiro (as 4 listas: pontos_positivos, pontos_melhoria, possiveis_motivos, roteiro_conversa), vendedorNome, mesReferencia e geradoEm.
2. Estrutura visual (cada seção é uma <section> com título e ícone do lucide-react):
   - "Pontos positivos" (reconhecimentos baseados nos dados) — destaque em tom positivo.
   - "Pontos de melhoria" (alavancas de desenvolvimento) — destaque em tom de atenção, nunca de erro.
   - "Possíveis motivos" — com uma legenda curta: "São hipóteses para investigar na conversa, não conclusões."
   - "Roteiro de conversa sugerido" — lista NUMERADA (ol) na ordem recebida, porque o roteiro segue a ordem da conversa (abertura, perguntas abertas, combinados).
   - Cabeçalho do visualizador: "Roteiro para <vendedorNome>", período (formatarMes ou "Todo o histórico") e "Gerado em <formatarDataHora>".
   - Uma nota fixa discreta: "Os pontos de melhoria e o roteiro seguem o método SBI (Situação, Comportamento e Impacto). Adapte ao seu jeito: a conversa é sua." Não explique mais que isso.
   - Se uma lista vier vazia, mostre "Nada sugerido nesta seção." em vez de deixar a seção em branco.
3. Layout expandido: em telas largas (a partir de 1024px) use duas colunas — pontos positivos e pontos de melhoria de um lado; possíveis motivos e roteiro de conversa do outro. Em telas estreitas, uma coluna. Quando a aba Feedback estiver ativa, permita que a área central use toda a largura disponível (sem o limite estreito das outras abas); faça isso com uma classe da própria PaginaFeedback, sem alterar o layout das outras abas.
4. Todo texto vem da IA: renderize como texto simples do React (as quebras de linha podem ser preservadas com CSS white-space: pre-line, sem HTML).
5. Acessibilidade: ordem de títulos coerente (h2/h3), listas semânticas, foco visível, e contraste conferido.
6. Em PaginaFeedback.jsx, substitua o resumo provisório da 5.7a (as 4 listas simples) pelo VisualizadorRoteiro. Mantenha o resto da página igual.
7. Se precisar de lógica de apoio (por exemplo, rótulo do período), use o que já existe nos formatadores ou crie função pura com teste.

Regras: o componente NÃO valida nem corrige o roteiro; mostra o que veio. Sem useApp dentro do VisualizadorRoteiro (ele só recebe props, para ser fácil de testar e reaproveitar).

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short`. Como não dá para gerar sem gastar crédito, para você conferir a aparência SEM gastar: peça-me o JSON de uma resposta real da API (cole o resultado do POST do backend/api.http, sem chaves) ou, se eu preferir, sugira um jeito seguro de ver o componente com dados de exemplo SEM deixar código de demonstração no repositório (por exemplo, um arquivo temporário que eu apague depois). Não deixe dados falsos no código versionado.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco com as props, cada seção comentada com o que mostra e por quê, "SBI", "lista numerada semântica" e "white-space: pre-line" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Cria visualizador do roteiro de feedback".

### Prompt 12
FATIA 5.8a — Visão regional: resultado da loja e acompanhamento dos feedbacks (Etapa 5)

Pré-requisito: 5.7b concluída. Leia apenas: frontend/src/components/AreaCentral.jsx, CartaoIndicador.jsx, Selo.jsx, EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, frontend/src/utilitarios/formatadores.js, frontend/src/context/AppProvider.jsx (carregarRegional), frontend/src/context/appReducer.js (estado.regional) e backend/contracts/regional.py (leia as descrições de cada campo para não interpretar errado: atingimento, participação do gerente, cobertura, "com_roteiro").

Objetivo: criar a visão executiva da Patrícia (gerente regional) sobre a loja do Diego. Tudo vem pronto de GET /api/regional/desempenho-gerente; a página só organiza e formata.

Tarefas:
1. Crie frontend/src/pages/PaginaRegional.jsx (+ PaginaRegional.css). Usa useApp(): estado.regional (status, dados, erro) e carregarRegional.
   - Um useEffect chama carregarRegional() quando a página aparece (comente por que recarregar toda vez que a visão abre: assim os roteiros recém-gerados pelo Diego aparecem).
   - Carregando → EstadoCarregando (variante "cartao"); erro → EstadoErro com botão que chama carregarRegional(); sem dados → EstadoVazio.
   - Cabeçalho: "Loja <loja_nome> — gerente <gerente_nome>" e o período (periodo_inicio a periodo_fim, formatarData).
2. Seção "Resultado da loja por mês": tabela acessível com uma linha por item de resultado_loja: mês (formatarMes, com Selo "Mês parcial" quando mes_parcial for true), meta da loja, vendas da loja, atingimento da loja (%), vendas dos vendedores, atingimento dos vendedores, vendas do gerente e participação do gerente (%). Sem nenhuma conta: use exatamente os campos recebidos. Na tabela, o atingimento da loja ganha um Selo: "Meta batida" (tom positivo) quando atingimento_loja for maior ou igual a 1, e "Abaixo da meta" (tom de atenção) quando menor; sem valor, sem selo. Isso é só apresentação: comente que a comparação com 1 (100%) não cria métrica nova, apenas escolhe o texto do selo.
3. Seção "Acompanhamento dos feedbacks":
   - Um CartaoIndicador "Cobertura de roteiros" com formatarPercentual(cobertura) e o detalhe "<vendedores_com_roteiro> de <total_vendedores> vendedores com roteiro preparado" e outro com "Total de roteiros preparados" (total_roteiros_preparados).
   - Uma lista/tabela com um item por vendedor de acompanhamento_feedback.vendedores: nome, situação (Selo com rotuloSituacaoAcompanhamento: com_roteiro em tom positivo, sem_roteiro em tom de atenção), quantidade de anotações do gerente, data da última anotação (formatarData) e data do último roteiro (formatarDataHora). Campos nulos viram "—".
   - Uma frase fixa de esclarecimento: "Roteiro preparado significa que o gerente gerou o rascunho no sistema. Isso não confirma que a conversa de feedback aconteceu."
4. Funções de apoio (tom do selo de atingimento, texto do período, etc.) em funções puras em frontend/src/utilitarios/visaoRegional.js, com testes em visaoRegional.test.js (atingimento maior, igual e menor que 1, null, situação desconhecida).
5. Em AreaCentral.jsx, troque o aviso da visão regional pela PaginaRegional (só esse trecho e o import).
6. NÃO inclua ainda as anotações da regional (fatia 5.8b).

Validação (execute de verdade): `npm test` (total), `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir (backend no ar): a visão Regional mostra os meses de agosto a novembro (novembro parcial, se a API mandar assim), a meta de outubro de 317.200,00, e a cobertura em 0% antes de qualquer geração; compare com `curl http://localhost:8000/api/regional/desempenho-gerente`. Depois que eu gerar o roteiro da Bianca pela aba Feedback e voltar à visão Regional, a Bianca deve aparecer como "Roteiro preparado" e a cobertura deve subir.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, cada seção comentada com o que mostra e de onde vem o dado, termos como "atingimento", "cobertura" e "participação do gerente" explicados em palavras simples, e fórmulas ESCRITAS EM PALAVRAS dizendo que quem calcula é o backend).

Não faça commit. Mensagem de commit sugerida: "Cria visão regional com resultado da loja e acompanhamento".

### Prompt 13 
FATIA 5.8b — Visão regional: anotações da regional (Etapa 5)

Pré-requisito: 5.8a concluída. Leia apenas: frontend/src/pages/PaginaRegional.jsx, frontend/src/pages/PaginaAnotacoes.jsx (estilo), frontend/src/utilitarios/ordenarAnotacoes.js e backend/contracts/regional.py (AnotacaoRegionalDTO).

Objetivo: mostrar na visão regional as observações da Patrícia sobre a liderança do Diego, que são a base do feedback que o gerente também precisa receber.

Tarefas:
1. Em PaginaRegional.jsx acrescente a seção "Anotações da regional sobre a liderança da loja", com os itens de estado.regional.dados.anotacoes_regional, da mais recente para a mais antiga (reaproveite a função de ordenação existente se o formato permitir; se os campos tiverem nomes diferentes — aqui são data, autora e texto —, crie uma função pura parecida em frontend/src/utilitarios/ordenarAnotacoes.js, sem quebrar os testes existentes, e acrescente testes). Cada item mostra data (formatarData), autora e texto exatamente como veio, em <time dateTime> e texto simples.
2. Lista vazia → EstadoVazio com texto próprio.
3. Uma frase de contexto: "Observações registradas nas visitas à loja. Servem de base para o feedback ao gerente."
4. Mantenha o restante da página como está. Se a PaginaRegional.jsx ficar grande demais (mais de ~250 linhas), extraia a seção de anotações para frontend/src/components/AnotacoesRegional.jsx (+ .css), recebendo as anotações por props.

Validação (execute de verdade): `npm test` (total), `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir: na visão Regional aparecem as 5 anotações da Patrícia (de 27/10/2026 até 18/08/2026, confira no CSV backend/data/anotacoes_regional.csv antes de afirmar), em ordem da mais recente para a mais antiga, com o texto igual ao do CSV.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código novo ou alterado, atualizando também os comentários de cabeçalho dos arquivos que você alterar para que continuem corretos.

Não faça commit. Mensagem de commit sugerida: "Adiciona anotações da regional à visão executiva".

### Prompt 14
FATIA 5.9 — Acessibilidade, responsividade e acabamento visual (Etapa 5)

Pré-requisito: 5.8b concluída. Leia apenas os arquivos de frontend/src/components/, frontend/src/pages/, frontend/src/estilos/ e frontend/src/App.jsx/App.css (ou App.layout.css). Não leia backend nem dados.

Objetivo: revisar tudo o que foi criado na Etapa 5 para garantir que o app seja usável por teclado, legível por leitores de tela e funcione bem em celular e desktop. Só ajustes; nenhuma funcionalidade nova.

Checklist (corrija o que encontrar e liste no relatório o que foi mudado, arquivo por arquivo):
1. Teclado: dá para percorrer tudo com Tab; a ordem é lógica; o foco é sempre visível; abas respondem às setas; nenhum botão é só um <div>.
2. Semântica: um único h1 na página; hierarquia de títulos sem pular níveis; listas são <ul>/<ol>; tabelas têm caption e th scope; imagens/ícones decorativos têm aria-hidden="true" e botões só com ícone têm aria-label.
3. Contraste: confira de novo cada par de cor usado no texto (mínimo 4,5:1 para texto normal e 3:1 para texto grande e bordas de controles). Corrija usando apenas tokens do DESIGN.md.
4. Estados: carregando usa role="status"/aria-busy; erros usam role="alert"; a mensagem não some sem o usuário perceber.
5. Responsividade: confira larguras de 360px, 768px, 1024px e 1440px (raciocinando pelo CSS, já que você não abre navegador): sem rolagem horizontal da página inteira, tabelas largas rolam dentro do próprio container, alvos de toque com pelo menos 44px, barra lateral empilha no topo em telas estreitas.
6. Movimento: animações respeitam prefers-reduced-motion.
7. Textos: todos em português, sem "undefined", "null" ou "NaN" visíveis (procure no código por lugares onde um valor pode chegar vazio sem passar pelos formatadores).
8. Título da aba do navegador (index.html) continua "Feedback Inteligente".

Regras: não altere o contexto, os serviços nem a lógica das telas; mudanças só em marcação (JSX), atributos de acessibilidade e CSS. Não instale ferramentas.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short`. Me dê um roteiro curto de conferência manual no navegador: navegar só com o teclado, reduzir a janela até a largura de um celular (F12 → modo dispositivo), e passar um leitor de tela se eu tiver.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: quando alterar um trecho, atualize o comentário dele, e comente os novos atributos de acessibilidade explicando o que cada um faz e para quem (ex.: "aria-hidden: esconde o ícone de leitores de tela, pois ele é só enfeite").

Não faça commit. Mensagem de commit sugerida: "Revisa acessibilidade e responsividade da interface".

### Prompt 15
FATIA 5.10 — Remover o painel temporário e atualizar a documentação do frontend (Etapa 5)

Pré-requisito: 5.9 concluída. Leia apenas: frontend/src/components/PainelVerificacao.jsx, frontend/src/App.css (e App.layout.css, se existir), frontend/src/App.jsx, frontend/README.md e a seção "Frontend" do COMO-RODAR.md (do título "## Frontend" até o fim da seção "Frontend: comunicação com a API").

Objetivo: tirar o painel de verificação, que existia só para testar o contexto, e deixar a documentação refletindo as telas reais.

Tarefas:
1. Confirme com grep que nenhum arquivo, além dele mesmo e do App.css, usa PainelVerificacao nem as classes do painel (.painel, .painel-cabecalho, .valores-brutos, .legenda, .erro). Se algo ainda usar, PARE e me avise.
2. Remova frontend/src/components/PainelVerificacao.jsx e as regras do App.css que só serviam a ele. Mantenha as regras do layout principal. Se o App.css ficar só com o layout, mantenha o nome atual.
3. Remova os arquivos .gitkeep de src/pages/ e src/components/ (as pastas agora têm arquivos).
4. No COMO-RODAR.md, edite SOMENTE a seção do frontend: substitua o trecho que fala do "painel temporário de verificação" por uma descrição curta das telas reais, em português simples: visão do gerente (barra lateral com a equipe, abas Anotações, Dados e Feedback), visão regional, e o aviso de que gerar o roteiro usa IA, consome créditos e pode levar de 10 segundos a alguns minutos. Mantenha os comandos úteis (npm test, npm run verificar:api etc.) e confirme que ainda existem no package.json.
5. Se frontend/README.md descrever o painel temporário, atualize só essa parte.
6. NÃO altere outras seções do COMO-RODAR.md nem nenhum outro documento.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `grep -rn "PainelVerificacao" frontend/src` sem resultados, `git status --short` e `git diff COMO-RODAR.md` resumido.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: se algum comentário de cabeçalho (App.jsx, main.jsx) ainda mencionar o painel temporário, atualize o texto para refletir a realidade. A documentação nova deve estar em português simples, sem jargão.

Não faça commit. Mensagem de commit sugerida: "Remove painel temporário e atualiza documentação do frontend".

### Prompt 16
FATIA 5.11 — Validação final da Etapa 5 (não crie nem altere código, só valide e relate)

Rode e mostre as saídas reais, de dentro de frontend/:
1. `npm test` (quantos testes passaram e se algum falhou), `npm run lint` e `npm run build`.
2. Varreduras (mostre os comandos e os resultados):
   - `grep -rn "fetch(\|axios" frontend/src/pages frontend/src/components` → sem resultados (as telas não chamam HTTP).
   - `grep -rn "dangerouslySetInnerHTML" frontend/src` → sem resultados.
   - `grep -rn "sk-\|DEEPSEEK" frontend` (ignorando node_modules) → sem resultados.
   - Liste todas as operações aritméticas (+, -, *, /) em frontend/src/pages e frontend/src/components e confirme, uma por uma, que não são cálculo de métrica (só layout, índices ou exibição). Se houver cálculo de negócio, aponte.
   - Procure cores soltas (#xxxxxx) fora de frontend/src/estilos/tokens.css e liste as que sobrarem.
3. `git status --short`: só arquivos de frontend/ e COMO-RODAR.md; nenhum .env, node_modules ou dist.
4. Confira se COMO-RODAR.md e o package.json continuam coerentes entre si (scripts citados existem).

### Prompt 17
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de npm/pip install, criar pastas, rodar build que gere arquivos, git add/commit/checkout). Pode apenas LER arquivos e listar pastas.

Vou te passar uma sequência de prompts, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar. Não implemente nada por conta própria.

Projeto: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um co-piloto que ajuda o gerente Diego Furtado (C0030, loja L004, Aurora Shopping Centro) a preparar o feedback da vendedora Bianca Rocha (C0031) com base nos indicadores de vendas e nas anotações dele. A gerente regional Patrícia Lemos acompanha numa visão executiva.

Estado atual: as Etapas 0 a 5 estão prontas.
- backend/ (FastAPI + Pandas + DeepSeek): domínio, DataLoader, LLMService, contratos Pydantic e 5 rotas (GET /health, GET /api/vendedores/{loja_id}, GET /api/vendedores/{vendedor_id}/historico, POST /api/feedback/gerar, GET /api/regional/desempenho-gerente).
- frontend/ (React + Vite, JavaScript): cliente Axios central, serviços, estado global em src/context/ (AppProvider, appReducer, useApp), tokens de design em src/estilos/, componentes em src/components/, páginas em src/pages/ (Dados, Anotações, Feedback, Regional) e funções puras com testes em src/utilitarios/.
Vamos agora fazer a "Etapa 6 – Ajustes de design e anotações em formato de chat", em fatias pequenas. O que vai mudar:
1. Abas: passam a ficar uma embaixo da outra, na ordem Feedback, Anotações, Dados, e o card do colaborador fica logo depois delas (por último, embaixo das três abas). Decisão tomada: o card vem por último; se eu pedir o contrário depois, será só ajuste de ordem.
2. Barra lateral: em vez da lista de toda a equipe, mostra só o colaborador escolhido num card, com uma seta ao lado do nome; ao clicar na seta aparecem os OUTROS colaboradores para trocar.
3. Aba Feedback: o botão "Gerar roteiro" vira "Gerar feedback"; some o aviso "A geração usa IA, consome créditos…"; os quatro blocos do resultado passam a ocupar toda a largura, um embaixo do outro, na ordem: Pontos positivos, Pontos de melhoria, Possíveis motivos e Roteiro de conversa sugerido.
4. Aba Anotações: ganha um campo para escrever novas anotações no próprio site, em formato de chat. Isso exige uma rota nova no backend para guardar as anotações.

Leia agora, sem alterar:
1. README.md, BRIEFING.md (seção "Desafio 3 — O feedback que ninguém dá"), COMO-RODAR.md, DIARIO.md e .gitignore.
2. Frontend: package.json, src/App.jsx, App.css, main.jsx, constantes.js; todo src/context/ (AppProvider.jsx, appReducer.js, appReducer.test.js, useApp.js, appContext.js); src/services/ (arquivos .js que não são de teste, mais vendedorService.test.js só para ver o estilo); src/components/ (BarraLateral, ListaColaboradores, NavegacaoAbas, AreaCentral, Cabecalho, VisualizadorRoteiro, EstadoCarregando, EstadoErro, EstadoVazio e os CSS ligados a eles); src/pages/PaginaFeedback.jsx, PaginaAnotacoes.jsx e seus CSS; src/estilos/tokens.css e base.css; src/utilitarios/ordenarAnotacoes.js e seu teste; e frontend/DESIGN.md (frontmatter, "Colors" e "Do's and Don'ts").
3. Backend: config.py, domain/anotacao.py, domain/gerente.py, domain/excecoes.py, services/data_loader.py (focando em obter_gerente, obter_anotacoes_do_vendedor e como o cache é montado), services/registro_feedback.py (como grava e lê o JSON), endpoints/dependencias.py, endpoints/vendedores.py, endpoints/erros.py, contracts/vendedores.py, contracts/mapeadores.py, contracts/erros.py, main.py, api.http e a lista de arquivos de backend/tests/. Veja também onde llm_service.py e consolidado_regional.py leem as anotações.
4. O cabeçalho do backend/data/anotacoes_gerente.csv.

Responda só com um resumo curto (máx. 15 linhas) do que entendeu, do estado atual e das dúvidas. Aponte em especial: (a) onde o backend lê as anotações e qual o menor caminho para uma anotação nova aparecer no histórico, no prompt da IA e na visão regional; (b) qualquer ponto em que o plano acima conflite com o código. Não escreva código e não crie arquivos.

Convenções que valem para TODOS os prompts seguintes:
- Separação de responsabilidades: nenhuma regra de negócio, nenhum cálculo de métrica e nenhuma chamada à LLM no frontend. Formatar para exibição é permitido. As telas NUNCA chamam fetch nem axios diretamente: leem o estado e chamam as ações do contexto com useApp(). Taxas chegam como fração 0–1; valor indisponível é null e aparece como "—", nunca "NaN", "null" ou "undefined".
- Onde cada coisa pode mudar: só mexa em src/context/ e src/services/ nas fatias que pedirem; só mexa no backend nas fatias 6.6a, 6.6b e 6.6c; só mexa em .gitignore, api.http e COMO-RODAR.md quando o prompt pedir. Se faltar algo fora do que o prompt autoriza, PARE e me avise em vez de contornar.
- Sem dependências novas (nem react-router, Tailwind, testing-library, nem pacotes Python novos). Navegação por estado (abas e visões do contexto).
- Visual: siga o DESIGN.md e os tokens de src/estilos/tokens.css. Nada de cores soltas fora dos tokens. Contraste AA, foco visível, alvos de toque com pelo menos 44px, animações respeitando prefers-reduced-motion. Ícones do lucide-react (confira com `npm run build` que o ícone escolhido existe na versão instalada).
- Todo texto vindo da IA ou digitado pelo usuário é exibido como TEXTO simples do React. Nunca use dangerouslySetInnerHTML.
- Textos da interface em português (pt-BR), claros e sem jargão; mensagens de erro humanas, sem stack trace nem dados internos.
- Estados da interface: toda tela que depende da API trata carregando, erro (com "Tentar de novo" quando fizer sentido) e vazio.
- Nomes de arquivos e identificadores em português, seguindo o que já existe; um componente por arquivo, com o CSS ao lado e classes prefixadas.
- Lógica isolável vai em funções puras em src/utilitarios/*.js com testes .test.js (o frontend usa `node --test`, sem navegador e sem JSX). Componentes são validados com `npm run build` e `npm run lint`.
- Backend: imports absolutos a partir de backend/, endpoints finos (sem regra de negócio nas rotas), testes com unittest da biblioteca padrão em backend/tests/, rodados de dentro de backend/ com o python do venv (`python -m unittest discover -s tests -t .`; Windows: backend/venv/Scripts/python). Testes nunca chamam a internet. NUNCA peça, leia ou imprima a chave DEEPSEEK_API_KEY. Erros no formato {"erro": "mensagem"}.
- Comandos de validação do frontend (de dentro de frontend/): `npm run build`, `npm run lint`, `npm test`. A suíte existente deve continuar passando (se um teste antigo precisar mudar porque o comportamento mudou de propósito, diga qual e por quê).
- Regras do repositório: mudanças pequenas e coesas; NÃO faça git commit/add/push/amend/reset (eu faço os commits); nunca coloque chaves ou segredos em arquivos versionados; não modifique dados/, prompts/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md nem .claude/. O registro dos prompts é feito por mim/pela ferramenta.
- Não invente dados nem fatos; confira no código, nos contratos e nos CSVs. Se algo do prompt contradisser o código, pare e me avise.
- Comandos de shell simples, um por vez, sem one-liners longos com pipes/awk. Se a sessão for interrompida, na retomada verifique `git status --short` e só crie o que ainda não existir.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: todo código que você escrever ou alterar (JavaScript, JSX, CSS, Python e testes) deve ser bem comentado, em português (pt-BR) e em linguagem simples, para que qualquer pessoa, mesmo sem conhecer a linguagem, entenda o que acontece em cada parte. Regras:
  1. Todo arquivo novo começa com um comentário de 2 a 4 linhas dizendo, em palavras simples, para que serve e como se encaixa no projeto (JS/JSX: /** ... */ antes dos imports; CSS: /* ... */ no topo; Python: docstring no topo).
  2. Todo componente e toda função tem comentário de bloco (JS: /** ... */; Python: docstring) explicando o que faz, o que recebe (props ou parâmetros), o que devolve e, quando ajudar, um exemplo curto (ex.: "iniciaisDoNome('Bianca Rocha') devolve 'BR'").
  3. Dentro das funções e componentes, comente cada bloco lógico explicando o que está sendo feito e POR QUÊ, não só repetindo o código. Dentro do JSX use {/* comentário */}. Evite comentários óbvios linha a linha; prefira explicar a intenção.
  4. Explique termos técnicos na primeira vez em que aparecerem no arquivo, com palavras do dia a dia (ex.: "props: os dados que um componente recebe de quem o usa", "estado: informação que muda e faz a tela se atualizar", "hook: função do React que começa com 'use'", "useEffect: roda um código depois que a tela aparece", "ref: uma caixinha que guarda um valor ou um elemento da tela sem redesenhar", "aria-expanded: avisa leitores de tela se um bloco está aberto ou fechado", "endpoint: um endereço da API que faz uma tarefa", "DTO: o formato dos dados que a API recebe ou devolve", "dataclass: um molde de objeto que guarda dados", "arquivo JSON: um arquivo de texto que guarda dados organizados").
  5. Em CSS, comente o que cada grupo de regras estiliza e por que o valor foi escolhido.
  6. Regras de exibição e de negócio escritas em palavras (ex.: "a anotação nova usa a data de hoje do servidor, para o usuário não conseguir inventar datas").
  7. Nos testes, comente o que cada teste verifica e por que aquele resultado é o esperado.
  8. Comentários devem ser corretos e estar sempre atualizados: ao alterar um trecho, atualize o comentário dele e o comentário de cabeçalho do arquivo (principalmente onde o texto antigo fala de "lista de toda a equipe", "duas colunas" ou "Gerar roteiro", que deixam de ser verdade). Nada de comentários em inglês, jargão sem explicação ou textos longos demais.
  9. Não altere código de fatias anteriores só para adicionar comentários, a não ser que o prompt peça.
- Ao fim de cada prompt, informe: arquivos criados/alterados, comandos de validação executados e o resultado REAL. Não declare algo validado sem ter executado. O que só dá para ver no navegador (aparência, clique, teclado) você NÃO consegue confirmar: diga isso e me dê o passo a passo para eu conferir.

Aguarde o primeiro prompt. Agora responda só com o resumo e as dúvidas, sem modificar nada.

### Prompt 18
FATIA 6.1 — Abas em fila vertical, na nova ordem (Etapa 6)

Leia apenas: frontend/src/constantes.js, frontend/src/components/NavegacaoAbas.jsx e NavegacaoAbas.css, frontend/src/context/appReducer.js (só criarEstadoInicial e o tratamento de MUDAR_ABA), frontend/src/context/appReducer.test.js, frontend/src/components/AreaCentral.jsx e frontend/src/estilos/tokens.css.

Objetivo: as abas passam a aparecer uma embaixo da outra, na ordem Feedback, Anotações, Dados, e a aba aberta ao entrar no app passa a ser Feedback. Ainda NÃO mexa na lista de colaboradores nem na BarraLateral (fatias 6.2 e 6.3).

Tarefas:
1. Em constantes.js, deixe os valores de ABAS e a lista de rótulos escritos na ordem Feedback, Anotações, Dados (a ordem dos itens no objeto serve de documentação). Não troque os valores técnicos ('feedback', 'anotacoes', 'dados').
2. Em appReducer.js, mude SOMENTE a aba inicial em criarEstadoInicial para ABAS.FEEDBACK (comente o porquê: o feedback é o fluxo principal do gerente). Atualize o teste que verifica o estado inicial em appReducer.test.js e diga no relatório exatamente qual teste mudou.
3. Em NavegacaoAbas.jsx: a ORDEM_ABAS passa a ser [FEEDBACK, ANOTACOES, DADOS]; o container ganha aria-orientation="vertical"; as setas ↑ e ↓ passam a mover entre as abas (com volta ao início/fim), e ← e → continuam funcionando também. Mantenha role="tablist", role="tab", aria-selected, aria-controls, tabIndex e o foco no botão novo. Cada aba ganha um ícone do lucide-react antes do texto (por exemplo Sparkles para Feedback, NotebookPen para Anotações e ChartColumn para Dados; se algum nome não existir na versão instalada, escolha outro parecido e me conte), com aria-hidden="true".
4. Em NavegacaoAbas.css: abas empilhadas (flex-direction: column), cada uma ocupando toda a largura do container, altura mínima de 44px, ícone + texto alinhados à esquerda, a aba ativa com destaque claro que não dependa só de cor (borda lateral ou fundo + peso da fonte), hover e foco visíveis. Só tokens do tema.
5. Atualize os comentários de cabeçalho de NavegacaoAbas.jsx e .css, que hoje descrevem abas lado a lado.

Validação (execute de verdade): `npm test` (diga quantos passaram e qual teste mudou), `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador: ao abrir o app, a aba Feedback vem ativa; as abas aparecem em fila (Feedback, Anotações, Dados); as setas ↑ ↓ trocam de aba; o foco aparece bem visível.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e atualize todo comentário que ficou desatualizado.

Não faça commit. Mensagem de commit sugerida: "Coloca abas em fila vertical com Feedback primeiro".


### Prompt 19
FATIA 6.2a — Funções de apoio do seletor de colaborador, com testes (Etapa 6)

Leia apenas: frontend/src/utilitarios/ordenarAnotacoes.js e ordenarAnotacoes.test.js (só o estilo) e backend/contracts/vendedores.py (VendedorResumoDTO: campos vendedor_id, nome e cargo).

Objetivo: criar, em arquivo próprio, a lógica pura que o seletor de colaborador (fatia 6.2b) vai usar. Nada de React aqui.

Tarefas:
1. Crie frontend/src/utilitarios/seletorColaborador.js com:
   - iniciaisDoNome(nome): devolve até 2 letras maiúsculas, a primeira letra do primeiro nome e a primeira do último nome. Ex.: "Bianca Rocha" → "BR"; "Marcelo Duarte" → "MD"; "Cher" → "C"; texto vazio, só espaços ou não-texto → "?". Ignora espaços extras.
   - encontrarColaborador(lista, id): devolve o item da lista com vendedor_id igual a id, ou null (lista inválida, id vazio ou inexistente).
   - outrosColaboradores(lista, idSelecionado): devolve uma NOVA lista sem o selecionado, mantendo a ordem recebida da API (sem ordenar por conta própria). Se idSelecionado for vazio/null ou não existir na lista, devolve todos. Lista inválida → lista vazia. A lista original nunca é alterada.
2. Crie frontend/src/utilitarios/seletorColaborador.test.js (node:test e node:assert) cobrindo os casos acima, incluindo nomes com espaços extras, acentos ("Tatiane Lopes" → "TL"), lista vazia, id inexistente e a garantia de que a lista original não foi alterada.

Não crie componentes nem altere outros arquivos.

Validação (execute de verdade): `npm test` (total), `npm run lint`, `npm run build`, `git status --short` (só 2 arquivos novos).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: cabeçalho, comentário de bloco com exemplo de entrada e saída em cada função, termos como "função pura" explicados em palavras simples, e cada teste dizendo o que verifica e por que o resultado é o esperado.

Não faça commit. Mensagem de commit sugerida: "Adiciona funções de apoio do seletor de colaborador".


### Prompt 20
FATIA 6.2b — Componente SeletorColaborador: card com seta e lista dos outros nomes (Etapa 6)

Pré-requisito: 6.1 e 6.2a concluídas. Leia apenas: frontend/src/components/ListaColaboradores.jsx e ListaColaboradores.css (para reaproveitar a lógica de carregar e auto-selecionar), frontend/src/components/EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, frontend/src/utilitarios/seletorColaborador.js, frontend/src/constantes.js, frontend/src/context/useApp.js, frontend/src/estilos/tokens.css e base.css.

Objetivo: criar o componente que mostra SÓ o colaborador escolhido, num card, com uma seta ao lado do nome. Ao clicar na seta, aparecem os OUTROS colaboradores; escolher um troca a pessoa. Ainda NÃO ligue o componente na BarraLateral (fatia 6.3) e ainda NÃO apague a ListaColaboradores.

Tarefas (em frontend/src/components/, SeletorColaborador.jsx + SeletorColaborador.css):
1. Dados: lê do contexto (useApp) estado.vendedores, estado.vendedorSelecionadoId, carregarVendedores e selecionarVendedor. Copie para cá o comportamento de carga que a ListaColaboradores já tem: pedir a lista uma única vez quando o status for "ocioso" (com a trava por ref por causa do StrictMode) e, quando a lista chegar sem ninguém selecionado, selecionar VENDEDOR_FOCO_ID se ele existir na lista. Mantenha os comentários explicando o porquê.
2. Estados: carregando → EstadoCarregando (variante "texto", 2 linhas); erro → EstadoErro com botão que chama carregarVendedores(); lista vazia → EstadoVazio.
3. Card fechado (estado normal): círculo com as iniciais (iniciaisDoNome, aria-hidden), o nome (destaque) e o cargo (texto suave) do colaborador selecionado, e à direita um botão só com ícone de seta (ChevronDown do lucide-react; vira ChevronUp quando aberto). O botão tem aria-label "Trocar de colaborador", aria-expanded (true/false) e aria-controls apontando para a lista. A seta é o controle; o card em si não é clicável. Área de clique do botão com no mínimo 44x44px.
4. Se ainda não houver ninguém selecionado (ex.: a Bianca não veio na lista), o card mostra "Escolher colaborador" no lugar do nome e a lista mostra todos.
5. Lista aberta: aparece logo abaixo do card (dentro do fluxo da página, empurrando o conteúdo; NÃO use posicionamento absoluto, para não ser cortada nem sumir no celular). Mostra só os OUTROS colaboradores (outrosColaboradores), cada um um <button> com iniciais, nome e cargo, na ordem recebida da API. Escolher um item chama selecionarVendedor(id), fecha a lista e devolve o foco para o botão da seta.
6. Teclado e leitor de tela: Esc fecha a lista e devolve o foco à seta; Tab/Shift+Tab percorrem os itens normalmente; as setas ↑ e ↓ movem o foco entre os itens da lista aberta (use refs). Padrão "disclosure": botão com aria-expanded + bloco que aparece/desaparece; não use role="menu" nem "listbox". Ao fechar, a lista sai do DOM (ou fica com hidden).
7. A lista fecha sozinha quando a troca termina de ser pedida. Se a pessoa clicar na seta de novo, alterna aberto/fechado.
8. CSS: card com superfície, borda e raio dos tokens; seta com hover e foco visíveis; item da lista com hover/foco; transição suave de abertura desligada por prefers-reduced-motion; sem cores soltas.

Regras: sem HTTP direto; sem regra de negócio; textos do nome e cargo como texto simples.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short` (só 2 arquivos novos). Como o componente ainda não está na tela, diga que a conferência visual fica para a fatia 6.3.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco com o que o componente lê do contexto, cada useEffect/ref/handler explicado com o PORQUÊ, e "aria-expanded", "disclosure", "ref" e "foco" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Cria seletor de colaborador com card e seta".


### Prompt 21
FATIA 6.3 — Barra lateral em fila: abas + card do colaborador (Etapa 6)

Pré-requisito: 6.1, 6.2a e 6.2b concluídas. Leia apenas: frontend/src/components/BarraLateral.jsx e BarraLateral.css, SeletorColaborador.jsx e .css, NavegacaoAbas.jsx e .css, frontend/src/App.jsx, App.css, frontend/src/components/AreaCentral.jsx e frontend/src/estilos/base.css (classe ui-visualmente-oculto).

Objetivo: montar a nova barra lateral. Em coluna, de cima para baixo: Feedback, Anotações, Dados e, por último, o card do colaborador (com a seta). A lista de toda a equipe deixa de existir.

Tarefas:
1. Reescreva BarraLateral.jsx: só aparece na visão do gerente. Estrutura: NavegacaoAbas (só quando há colaborador selecionado) seguida do SeletorColaborador, ambos dentro do <aside>. O SeletorColaborador deve ficar sempre montado (é ele que carrega a lista e seleciona a Bianca).
2. O título visível "Equipe" some. Mantenha um título acessível com a classe ui-visualmente-oculto (ex.: "Menu do colaborador") ligado ao <aside> por aria-labelledby, para leitores de tela.
3. BarraLateral.css: coluna única com espaçamento dos tokens; a ordem visual é a ordem do DOM (não use "order" do CSS, para a ordem de leitura e a de tela coincidirem). Largura da coluna lateral pode diminuir de 300px para algo mais enxuto (por exemplo 260px) em App.css; explique a escolha em comentário. No celular (menos de 768px) continua empilhando acima do conteúdo, como hoje.
4. Depois de confirmar com grep que ninguém mais importa ListaColaboradores, APAGUE frontend/src/components/ListaColaboradores.jsx e ListaColaboradores.css. Se algo ainda usar, PARE e me avise.
5. Atualize os comentários de cabeçalho de BarraLateral.jsx, AreaCentral.jsx (a mensagem "Selecione alguém na lista à esquerda…" também deve virar algo como "Escolha um colaborador no card da barra lateral…") e App.jsx/App.css se citarem "lista de colaboradores".

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `grep -rn "ListaColaboradores" frontend/src` sem resultados, `git status --short`. Passo a passo para eu conferir no navegador (backend no ar + `npm run dev`): a barra lateral mostra Feedback, Anotações e Dados em fila e, embaixo, o card da Bianca com a seta; clicar na seta mostra só os outros 7 nomes; escolher outro troca o card e carrega os dados da nova pessoa; Esc fecha; no celular tudo continua utilizável; sem erros no console.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e atualize todo comentário que ficou desatualizado.

Não faça commit. Mensagem de commit sugerida: "Reorganiza barra lateral com abas em fila e card do colaborador".


### Prompt 22
FATIA 6.4 — Aba Feedback: "Gerar feedback" e remoção do aviso (Etapa 6)

Leia apenas: frontend/src/pages/PaginaFeedback.jsx e PaginaFeedback.css.

Objetivo: ajustar só os textos desta página.

Tarefas:
1. O botão "Gerar roteiro" passa a ser "Gerar feedback". O título do bloco "Gerar roteiro de feedback" passa a ser "Gerar feedback".
2. REMOVA completamente o parágrafo "A geração usa IA, consome créditos e pode levar até alguns minutos. Revise tudo antes de usar: você continua sendo o dono da conversa." (o texto e o estilo que só servia a ele, se houver).
3. Ajuste os textos próximos que citam o botão antigo para não ficarem errados: a mensagem do estado ocioso que diz "clique em Gerar roteiro" deve dizer "clique em Gerar feedback"; o título do estado de carregamento "Preparando o roteiro…" vira "Preparando o feedback…" (mantenha a explicação de que pode levar de alguns segundos a alguns minutos, porque é informação de espera, não o aviso removido). Os rótulos "Roteiros já preparados", "Roteiro preparado" e "Roteiro de conversa sugerido" NÃO mudam.
4. Se aparecer no relatório algum outro texto visível que diga "Gerar roteiro", liste e corrija; não mexa em nomes internos de variáveis nem do contexto.
5. Atualize comentários que ainda falem do aviso removido ou do botão "Gerar roteiro".

Validação (execute de verdade): `grep -rn "Gerar roteiro" frontend/src` (mostre o resultado; só pode sobrar em comentário histórico, e prefira atualizar), `grep -rn "dono da conversa" frontend/src` sem resultados, `npm test`, `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador: aba Feedback com botão "Gerar feedback", sem o aviso, e estado vazio com o texto novo. NÃO gere feedback real (gasta créditos).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e mantenha os comentários corretos.

Não faça commit. Mensagem de commit sugerida: "Renomeia botão para Gerar feedback e remove aviso".

### Prompt 23
FATIA 6.5 — Cards do feedback em largura total, um embaixo do outro (Etapa 6)

Leia apenas: frontend/src/components/VisualizadorRoteiro.jsx e VisualizadorRoteiro.css, frontend/src/pages/PaginaFeedback.jsx e PaginaFeedback.css.

Objetivo: no resultado do feedback, cada card ocupa toda a largura da área central, um embaixo do outro, nesta ordem exata: 1) Pontos positivos, 2) Pontos de melhoria, 3) Possíveis motivos, 4) Roteiro de conversa sugerido.

Tarefas:
1. Em VisualizadorRoteiro.jsx, remova a grade de duas colunas e as duas "colunas": as quatro <section> ficam numa única coluna, na ordem acima. Mantenha o cabeçalho (nome, período, "Gerado em"), a nota do método SBI, os ícones, os tons de cada card (positivo, atenção, neutro), a legenda de "Possíveis motivos", a lista numerada do roteiro de conversa e o texto "Nada sugerido nesta seção." para listas vazias.
2. Em VisualizadorRoteiro.css, apague as regras da grade e das colunas (incluindo o @media de 1024px) e garanta que cada card tenha width: 100% e espaçamento vertical entre eles pelos tokens. Texto longo deve quebrar linha sem estourar o card (overflow-wrap).
3. Em PaginaFeedback.jsx/.css, se existir alguma classe ou regra criada só para o "layout expandido em duas colunas", remova-a; o resultado deve ocupar a largura da página como as demais abas.
4. Não mude a ordem do conteúdo recebido da API; só a organização visual. Texto da IA continua como texto simples.
5. Atualize os comentários de cabeçalho dos arquivos alterados, que hoje falam em duas colunas.

Validação (execute de verdade): `grep -n "grade\|coluna" frontend/src/components/VisualizadorRoteiro.*` (confirme que não sobrou regra de duas colunas), `npm test`, `npm run lint`, `npm run build`, `git status --short`. Como a geração real gasta crédito, peça-me que cole o JSON de uma resposta real (ou me diga como ver o componente com dados de exemplo num arquivo temporário que eu apago depois, sem deixar dados falsos no repositório). Passo a passo para eu conferir: quatro cards de largura total, empilhados na ordem pedida, em tela larga e no celular.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e atualize todo comentário que ficou desatualizado.

Não faça commit. Mensagem de commit sugerida: "Empilha cards do feedback em largura total".

### Prompt 24
FATIA 6.6a — Backend: guardar anotações novas (Etapa 6)

A partir desta fatia o backend pode ser alterado, mas só o que está listado aqui. Leia apenas: backend/config.py, backend/domain/anotacao.py, backend/domain/excecoes.py, backend/services/registro_feedback.py (modelo de como ler e gravar o JSON com segurança), backend/tests/test_registro_feedback.py (só o estilo dos testes) e o final do .gitignore.

Objetivo: criar o serviço que guarda as anotações escritas pelo gerente no site, sem mexer nos CSVs de dados. As anotações originais continuam no CSV; as novas ficam num arquivo JSON à parte, criado sozinho.

Tarefas:
1. Em backend/config.py ACRESCENTE, sem alterar o que existe: ANOTACOES_NOVAS_ARQUIVO = DATA_DIR / "anotacoes_novas.json" e ANOTACAO_TEXTO_MAXIMO = 1000 (limite de caracteres), com comentários explicando o porquê.
2. Em backend/domain/excecoes.py ACRESCENTE a exceção AnotacaoInvalidaError (mensagem em português para o usuário), seguindo o padrão das outras exceções do arquivo.
3. Crie backend/services/registro_anotacoes.py com a classe RegistroAnotacoesService, no mesmo estilo (e com o mesmo cuidado de gravação segura, tolerância a arquivo ausente ou corrompido e trava de concorrência, se houver) do RegistroFeedbackService:
   - __init__(arquivo=ANOTACOES_NOVAS_ARQUIVO).
   - registrar(sobre: str, texto: str, data: date | None = None) -> Anotacao: tira espaços das pontas do texto; recusa texto vazio ou maior que ANOTACAO_TEXTO_MAXIMO levantando AnotacaoInvalidaError; "sobre" também não pode ser vazio; se data for None usa a data de hoje (o parâmetro existe para os testes poderem fixar a data); grava e devolve a Anotacao criada (reaproveite a entidade domain.anotacao.Anotacao).
   - listar() -> tuple[Anotacao, ...]: devolve todas as anotações guardadas, na ordem em que foram registradas.
   O texto é guardado exatamente como digitado (sem corrigir nem resumir), só sem espaços nas pontas. Quebras de linha são preservadas.
4. No .gitignore, ACRESCENTE no fim, com comentário em português, a linha backend/data/anotacoes_novas.json (dado de execução, não código), sem alterar o resto.
5. Crie backend/tests/test_registro_anotacoes.py (unittest, usando arquivo temporário; nunca o arquivo real) cobrindo: registrar e listar; persistência entre duas instâncias do serviço (grava numa, lê noutra); texto com espaços nas pontas; texto vazio; texto só com espaços; texto acima do limite; texto com acentos e quebra de linha; arquivo ausente (lista vazia); arquivo corrompido (comportamento igual ao do registro de feedbacks: confira e siga o mesmo); data fixa pelo parâmetro e data de hoje por padrão.

Não crie rotas nem altere o DataLoader nesta fatia.

Validação (execute de verdade): suíte completa a partir de backend/ (diga o total e se algum teste ficou "skipped"), `git status --short` (só config.py, excecoes.py, o serviço novo, o teste novo e .gitignore) e `git check-ignore -v backend/data/anotacoes_novas.json` mostrando que o arquivo é ignorado.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código Python (docstring de arquivo, de classe e de função com exemplo, comentário em cada passo explicando o PORQUÊ, "arquivo JSON", "dataclass" e "exceção" explicados em palavras simples, testes comentados).

Não faça commit. Mensagem de commit sugerida: "Cria serviço para guardar anotações novas do gerente".


### Prompt 25
FATIA 6.6b — Backend: anotações novas entram no histórico, na IA e na visão regional (Etapa 6)

Pré-requisito: 6.6a concluída. Leia apenas: backend/services/data_loader.py (construtor, _carregar_dados, obter_gerente, obter_anotacoes_do_vendedor), backend/domain/gerente.py, backend/services/registro_anotacoes.py, backend/endpoints/dependencias.py, backend/tests/test_data_loader.py e test_gerente.py (só o estilo e como o DataLoader é montado nos testes) e, só como consulta, os trechos de llm_service.py e consolidado_regional.py que chamam obter_gerente()/obter_anotacoes_do_vendedor().

Objetivo: fazer com que as anotações guardadas pelo serviço da fatia anterior apareçam em TODOS os lugares onde o sistema lê as anotações do gerente: histórico do vendedor, prompt enviado à IA e acompanhamento da regional. A forma mais simples e menos invasiva: o DataLoader passa a juntar as anotações do CSV com as do serviço.

Tarefas:
1. No DataLoader, aceite um parâmetro OPCIONAL novo no construtor (por exemplo registro_anotacoes=None). Sem ele, o comportamento atual fica IDÊNTICO (todos os testes existentes devem passar sem alteração).
2. Com o serviço informado, o Gerente devolvido por obter_gerente() deve conter as anotações do CSV + as do serviço, em ordem de data (datas iguais: as do CSV antes, depois as novas, na ordem de registro). Como as anotações novas mudam a cada POST, o DataLoader NÃO pode usar uma versão "congelada" delas: leia o serviço a cada chamada de obter_gerente() (ou use outra estratégia que garanta que uma anotação recém-gravada apareça na próxima leitura), mas continue lendo e cacheando o CSV só uma vez. Explique em comentário a escolha e o porquê. Se isso exigir mexer em como o Gerente é construído, faça o mínimo e sem alterar o comportamento das outras partes; se encontrar um obstáculo real, PARE e me avise antes de mudar o domínio.
3. Em backend/endpoints/dependencias.py, ACRESCENTE obter_registro_anotacoes() (singleton com lru_cache, como os outros) e faça obter_data_loader() passar esse serviço ao DataLoader. Confira se existe algum outro lugar do código que monte um DataLoader para uso real (por exemplo scripts/); se existir, liste e NÃO altere sem eu pedir.
4. Crie backend/tests/test_data_loader_anotacoes_novas.py (arquivo temporário nos testes, nunca o arquivo real) cobrindo: sem o serviço, o resultado é igual ao de antes; uma anotação nova sobre a Bianca aparece em obter_anotacoes_do_vendedor("C0031") e em obter_gerente().anotacoes; uma anotação nova sobre outra pessoa NÃO aparece nas da Bianca; uma anotação nova "(time)" aparece em anotacoes_do_time(); a anotação gravada DEPOIS de o DataLoader já ter sido usado aparece na leitura seguinte; a ordem por data e o desempate descritos acima; e, no acompanhamento da regional, a contagem de anotações da Bianca aumenta em 1 depois de registrar uma (use o ConsolidadoRegional real com o DataLoader de teste, se der sem internet).
5. Teste também, sem internet, que o texto que vai para o prompt da IA inclui a anotação nova: monte o prompt com a função que o llm_service já usa (veja prompt_feedback.py) a partir de obter_anotacoes_do_vendedor e confira que o texto novo aparece no prompt. Se isso exigir cliente de LLM falso, siga o padrão dos testes existentes.

Validação (execute de verdade): suíte completa a partir de backend/ (total e "skipped"), `git status --short` (só os arquivos citados) e confirme que NENHUM teste existente precisou ser alterado (se algum precisou, diga qual e por quê).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código Python novo ou alterado, atualizando docstrings e comentários dos trechos que mudaram (por exemplo, o do DataLoader que diz que as anotações vêm só do CSV).

Não faça commit. Mensagem de commit sugerida: "Faz anotações novas entrarem no DataLoader, na IA e na regional".

### Prompt 26
FATIA 6.6c — Backend: rota POST /api/vendedores/{vendedor_id}/anotacoes (Etapa 6)

Pré-requisito: 6.6a e 6.6b concluídas. Leia apenas: backend/endpoints/vendedores.py, backend/endpoints/dependencias.py, backend/endpoints/erros.py, backend/contracts/vendedores.py, contracts/mapeadores.py (função anotacao_de), contracts/erros.py, backend/main.py, backend/api.http, backend/tests/test_endpoints_vendedores_historico.py (estilo de TestClient e overrides) e o teste que confere a lista de rotas do servidor (procure em backend/tests/ por "/api/regional/desempenho-gerente" para achar onde as rotas são listadas).

Objetivo: expor a rota para o frontend gravar uma anotação nova sobre um vendedor.

Tarefas:
1. Em backend/contracts/vendedores.py ACRESCENTE o DTO de entrada AnotacaoNovaRequisicao com o campo texto (string; descrição em português; limites coerentes com ANOTACAO_TEXTO_MAXIMO do config, e sem aceitar texto só de espaços). Não receba data nem "sobre" do cliente: quem decide a data (hoje, no servidor) e o nome da pessoa (vem do vendedor_id) é o backend.
2. Em backend/endpoints/vendedores.py ACRESCENTE POST /api/vendedores/{vendedor_id}/anotacoes, no mesmo router, response_model=AnotacaoDTO (o que já existe), status 201, erros documentados com ErroResposta. A rota é fina: busca o vendedor pelo DataLoader (ID desconhecido ou do gerente C0030 → 404, igual ao histórico), chama RegistroAnotacoesService.registrar(sobre=<nome do vendedor>, texto=<texto>) via Depends(obter_registro_anotacoes) e devolve a anotação convertida pelo mapeador existente. Texto inválido (AnotacaoInvalidaError) → 400 {"erro": "..."}; confira em endpoints/erros.py se o tratador global já cobre exceções de domínio desse tipo e acrescente o mapeamento no padrão que existe, sem criar um novo jeito de tratar erro. Erros de validação do Pydantic (corpo ausente, texto não é string) também devem sair como 400 no formato {"erro": ...}: confira se o tratador global já faz isso.
3. Crie backend/tests/test_endpoints_anotacoes.py com TestClient e overrides (DataLoader real + serviço de anotações com arquivo temporário): 201 e estrutura do corpo (data de hoje, sobre = nome da Bianca, texto igual ao enviado sem espaços nas pontas, e_do_time falso); depois do POST, GET /api/vendedores/C0031/historico contém a anotação nova (e as originais continuam); a anotação sobre a Bianca NÃO aparece no histórico de outra pessoa; vendedor inexistente → 404; C0030 → 404; texto vazio, só espaços, acima do limite e corpo sem "texto" → 400 com a chave "erro"; JSON bruto sem NaN; duas anotações seguidas mantêm a ordem; e a visão regional (GET /api/regional/desempenho-gerente) mostra anotacoes_do_gerente da Bianca aumentando em 1.
4. Atualize o teste que lista as rotas do servidor para incluir a nova (sem remover as antigas) e diga qual arquivo mudou.
5. Em backend/api.http ACRESCENTE (sem alterar o resto) duas requisições com comentário em português: o POST de anotação para C0031 com um texto de exemplo e um exemplo de erro (texto vazio).

Validação (execute de verdade): suíte completa a partir de backend/ (total e "skipped"); se as dependências estiverem instaladas, suba o uvicorn de dentro de backend/ com um arquivo de anotações TEMPORÁRIO (não use o real; se não houver jeito de trocar o arquivo sem editar código, valide só pelos testes e me diga) e rode curl no POST e no histórico, mostrando o resultado; confira com /openapi.json que a rota nova existe; `git status --short` (só os arquivos citados, e nenhum anotacoes_novas.json real criado/versionado). Encerre o servidor.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código Python novo ou alterado ("endpoint", "DTO", "status 201" e "dependência" explicados em palavras simples; regras como "a data vem do servidor, não do cliente" escritas em palavras).

Não faça commit. Mensagem de commit sugerida: "Cria rota para registrar anotações do gerente".


### Prompt 27
FATIA 6.7a — Frontend: serviço de anotações (Etapa 6)

Pré-requisito: 6.6c concluída. Nesta fatia você pode criar arquivos em frontend/src/services/. Leia apenas: frontend/src/services/vendedorService.js e vendedorService.test.js, services/api.js, services/erroApi.js e backend/contracts/vendedores.py (AnotacaoNovaRequisicao e AnotacaoDTO).

Objetivo: criar a camada HTTP para gravar uma anotação, no mesmo estilo dos outros serviços.

Tarefas:
1. Crie frontend/src/services/anotacaoService.js com a fábrica criarAnotacaoService(cliente = api) e a exportação padrão da função registrarAnotacao(vendedorId, texto, { signal } = {}):
   - valida o vendedorId (texto não vazio) e o texto (texto, não vazio depois de tirar espaços das pontas) lançando ErroApi do tipo "validacao" com mensagens humanas em português, sem chamar a API;
   - faz POST em /api/vendedores/{id}/anotacoes (com encodeURIComponent no id) com o corpo { texto } já sem espaços nas pontas (preserve as quebras de linha do meio);
   - devolve o corpo da resposta sem transformar (a anotação criada: data, sobre, texto, e_do_time).
   Não duplique regras do backend (limite de caracteres etc.): o backend é quem valida de verdade; o frontend só evita enviar vazio.
2. Crie frontend/src/services/anotacaoService.test.js no mesmo estilo do vendedorService.test.js (cliente falso com adapter, sem rede): envia o corpo certo e a URL certa; remove espaços das pontas; preserva quebra de linha interna; recusa id vazio e texto vazio/só espaços sem chamar a API; propaga erro 400 e 404 da API como ErroApi com a mensagem do campo "erro".
3. Não altere api.js, erroApi.js nem os outros serviços.

Validação (execute de verdade): `npm test` (total), `npm run lint`, `npm run build`, `git status --short` (só 2 arquivos novos).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco com exemplo, "fábrica de serviço", "adapter" e "AbortSignal" explicados em palavras simples; cada teste dizendo o que verifica).

Não faça commit. Mensagem de commit sugerida: "Cria serviço de anotações no frontend".


### Prompt 28
FATIA 6.7b — Frontend: contexto com a ação de adicionar anotação (Etapa 6)

Pré-requisito: 6.7a concluída. Nesta fatia você pode alterar frontend/src/context/. Leia apenas: frontend/src/context/AppProvider.jsx, appReducer.js, appReducer.test.js, useApp.js, frontend/src/services/anotacaoService.js e frontend/src/services/erroApi.js.

Objetivo: o estado global passa a saber enviar uma anotação nova e refletir o resultado na tela, seguindo exatamente o padrão que já existe para gerar feedback.

Tarefas:
1. appReducer.js: acrescente os tipos ANOTACAO_ENVIANDO, ANOTACAO_SUCESSO e ANOTACAO_ERRO e um novo pedaço de estado em criarEstadoInicial: novaAnotacao: { status: STATUS.OCIOSO, erro: null }. Regras:
   - ANOTACAO_ENVIANDO: status carregando, erro limpo.
   - ANOTACAO_SUCESSO: só se a ação for do vendedor selecionado agora (mesma proteção de "resposta antiga" que os detalhes já têm), acrescenta a anotação devolvida (acao.dados) NO FIM de detalhes.dados.anotacoes (sem mexer na lista original: crie uma nova), e volta o status de novaAnotacao para sucesso. Se os detalhes ainda não estiverem carregados, ou a anotação vier inválida, não quebre: ignore a inclusão e registre sucesso mesmo assim só se fizer sentido (explique sua decisão em comentário e nos testes).
   - ANOTACAO_ERRO: guarda só a mensagem de texto (use a função de mensagem de erro que já existe), nunca o objeto de erro.
   - SELECIONAR_VENDEDOR também reinicia novaAnotacao para o estado ocioso (trocar de pessoa não pode herdar o erro ou o "enviando" da anterior).
2. AppProvider.jsx: acrescente a ação adicionarAnotacao(vendedorId, texto) que despacha ENVIANDO, chama servicos.registrarAnotacao(vendedorId, texto, { signal }) e despacha SUCESSO ou ERRO (cancelamento não vira erro). Devolve uma Promise com true quando gravou e false quando falhou (a tela usa isso para limpar o campo só quando deu certo). Ignora uma nova chamada enquanto outra estiver em andamento (duplo clique não grava duas vezes). Sem tentativa automática. Cancele o pedido pendente ao desmontar, como já é feito com as outras ações. Inclua registrarAnotacao em SERVICOS_REAIS e adicionarAnotacao no valor do contexto (e na lista de dependências do useMemo).
3. appReducer.test.js: acrescente testes (sem alterar os existentes, exceto o do estado inicial se ele comparar o objeto inteiro: nesse caso diga qual mudou) para: estado inicial com novaAnotacao ocioso; ENVIANDO; SUCESSO acrescentando no fim sem alterar o estado anterior; SUCESSO de outro vendedor (resposta antiga) sendo ignorado; ERRO guardando só texto; trocar de vendedor limpando novaAnotacao.
4. Não altere src/services/ nem os componentes nesta fatia.

Validação (execute de verdade): `npm test` (total e quais testes são novos), `npm run lint`, `npm run build`, `git status --short`.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e atualize os comentários de cabeçalho do reducer e do provider para citar a nova ação ("reducer", "ação" e "estado imutável" já explicados no arquivo: mantenha a explicação em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Adiciona ação de nova anotação ao contexto".


### Prompt 29
FATIA 6.7c — Frontend: funções de apoio do chat de anotações, com testes (Etapa 6)

Leia apenas: frontend/src/utilitarios/ordenarAnotacoes.js e ordenarAnotacoes.test.js, frontend/src/utilitarios/formatadores.js (formatarData) e backend/contracts/vendedores.py (AnotacaoDTO).

Objetivo: preparar, em funções puras, o que o chat precisa: ordem cronológica (a mais antiga em cima, a mais nova embaixo, como num chat) e agrupamento por dia. Nada de React.

Tarefas:
1. Em frontend/src/utilitarios/ordenarAnotacoes.js ACRESCENTE (sem alterar as funções existentes nem os testes delas) ordenarDaMaisAntigaParaMaisRecente(lista): devolve uma NOVA lista ordenada por data crescente; datas iguais mantêm a ordem em que chegaram (a ordem em que foram escritas); lista inválida → lista vazia; a original nunca é alterada.
2. Crie frontend/src/utilitarios/agruparPorDia.js com agruparPorDia(listaOrdenada): recebe anotações já em ordem cronológica e devolve uma lista de grupos { data: "AAAA-MM-DD", itens: [...] }, um por dia, mantendo a ordem. Lista vazia → [].
3. Crie frontend/src/utilitarios/rotuloDoDia.js com rotuloDoDia(dataTexto, hojeTexto): "Hoje" quando a data é igual a hojeTexto, "Ontem" quando é o dia anterior, e a data formatada (formatarData) nos demais casos; entrada inválida → "—". Receba "hoje" por parâmetro (texto AAAA-MM-DD) em vez de usar a data do computador dentro da função, para ela continuar pura e testável. Monte datas a partir das partes do texto, sem new Date("AAAA-MM-DD") direto (problema de fuso horário), e trate virada de mês e de ano ao calcular "Ontem".
4. Testes (node:test) para as três: ordem correta, estabilidade para datas iguais, não alterar a lista original, entradas inválidas, agrupamento com 1 e vários dias, "Hoje", "Ontem", virada de mês (01/11 → ontem 31/10) e de ano (01/01 → ontem 31/12).
5. Se precisar de "hoje" no componente, a fatia seguinte cria uma função para isso; não crie agora.

Validação (execute de verdade): `npm test` (total e testes novos), `npm run lint`, `npm run build`, `git status --short`.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: cabeçalho, comentário de bloco com exemplo de entrada e saída em cada função, "ordenação estável", "função pura" e "fuso horário" explicados em palavras simples, e cada teste dizendo o que verifica.

Não faça commit. Mensagem de commit sugerida: "Adiciona ordenação e agrupamento por dia para o chat de anotações".

### Prompt 30
FATIA 6.7d — Frontend: aba Anotações em formato de chat (Etapa 6)

Pré-requisito: 6.7a, 6.7b e 6.7c concluídas. Leia apenas: frontend/src/pages/PaginaAnotacoes.jsx e PaginaAnotacoes.css, frontend/src/context/AppProvider.jsx (ação adicionarAnotacao) e appReducer.js (estado.novaAnotacao e estado.detalhes), frontend/src/components/EstadoCarregando.jsx, EstadoErro.jsx, EstadoVazio.jsx, frontend/src/utilitarios/ordenarAnotacoes.js, agruparPorDia.js, rotuloDoDia.js, formatadores.js, frontend/src/estilos/tokens.css e base.css.

Objetivo: transformar a aba Anotações numa conversa: o histórico de anotações do colaborador aparece como mensagens, e embaixo há um campo para escrever uma nova anotação, que fica guardada no sistema e passa a valer para o feedback.

Tarefas:
1. Reescreva PaginaAnotacoes.jsx. Continua usando estado.detalhes (carregando, erro com "Tentar de novo" que chama selecionarVendedor de novo, vazio) como hoje.
2. Área de mensagens (role="log", aria-live="polite", aria-label "Anotações sobre <nome>"): uma altura máxima razoável (por exemplo 60vh) com rolagem interna; as anotações de detalhes.dados.anotacoes em ordem cronológica (a mais antiga em cima, a mais nova embaixo), agrupadas por dia com um separador de dia centralizado (rotuloDoDia) e cada anotação num "balão" alinhado à direita (são mensagens do próprio gerente), com o texto exatamente como veio (preserve quebras de linha com white-space: pre-wrap) e a data em <time dateTime>. Ao abrir a aba, ao trocar de colaborador e depois de enviar, role até a última mensagem (use ref + scrollIntoView, com behavior "auto" quando o usuário prefere menos movimento). Sem anotações → EstadoVazio com "Ainda não há anotações sobre <nome>. Escreva a primeira abaixo."
3. Campo de escrever (fixo logo abaixo das mensagens): um <textarea> com label acessível ("Nova anotação"; pode ser visualmente oculta) e placeholder "Escreva uma observação sobre <nome>…"; botão "Enviar" com ícone Send do lucide-react (aria-label "Enviar anotação"). Enter envia; Shift+Enter quebra linha; durante composição de texto por IME (isComposing) o Enter não envia. O botão fica desabilitado quando o texto (sem espaços nas pontas) está vazio ou enquanto envia. Contador discreto de caracteres, com o limite de 1000 (use uma constante em constantes.js — pode acrescentar ANOTACAO_TEXTO_MAXIMO = 1000 com comentário dizendo que o limite real é validado pelo backend; é só para orientar a pessoa). Para ao chegar no limite (maxLength do textarea).
4. Envio: chama adicionarAnotacao(vendedorId, texto) do contexto. Se retornar true, limpa o campo e devolve o foco ao textarea; se false, MANTÉM o texto digitado e mostra, abaixo do campo, a mensagem de erro de estado.novaAnotacao.erro (role="alert") com a opção de tentar de novo pelo próprio botão Enviar. Enquanto envia mostre "Enviando…" no botão. Nada de tentativa automática.
5. Rascunho: ao trocar de colaborador, o campo é esvaziado (a página deve ser reinstanciada por pessoa, como a PaginaFeedback faz com key={vendedorSelecionadoId} em AreaCentral.jsx; altere só essa linha de AreaCentral.jsx e diga que alterou).
6. As anotações sobre o time (detalhes.dados.anotacoes_do_time) continuam existindo, mas FORA do chat: numa seção recolhível <details><summary>Anotações sobre o time (N)</summary>…</details> embaixo do campo de escrever, somente leitura, em ordem da mais recente para a mais antiga (use ordenarAnotacoes existente), com a frase "Observações sobre a loja toda, que ajudam a entender o contexto." Sem anotações do time → a seção mostra EstadoVazio curto.
7. Texto orientativo curto acima do chat: "Escreva aqui o que observar durante o mês. As anotações ficam guardadas e entram no feedback." (só afirme isso porque as fatias 6.6b/6.7b garantem; confira nos testes antes de manter a frase e me avise se não puder confirmar).
8. CSS (PaginaAnotacoes.css): balões com superfície, borda e raio dos tokens e contraste AA; separador de dia discreto; textarea com foco visível; layout confortável em 360px; nada de cores soltas; animações respeitam prefers-reduced-motion. Texto digitado e anotações são sempre texto simples do React.
9. Remova de PaginaAnotacoes o que ficar sem uso e atualize os comentários de cabeçalho (a página não é mais só uma lista de leitura).

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador (backend no ar + `npm run dev`): a aba Anotações da Bianca mostra as 4 anotações antigas em ordem cronológica, a mais recente (08/10/2026) embaixo; escrevo uma anotação e aperto Enter: ela aparece embaixo como "Hoje" e o campo esvazia; recarrego a página e a anotação continua lá; Shift+Enter quebra linha; texto vazio não envia; derrubo o backend e envio: aparece erro e o texto continua no campo; troco de colaborador e o campo esvazia. Se eu tiver gerado um feedback depois de anotar, peça-me para checar se o roteiro leva a nova anotação em conta.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, cada useEffect/ref/handler com o PORQUÊ, "role=log", "aria-live", "textarea", "isComposing" e "details/summary" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Transforma aba Anotações em chat com envio de novas anotações".


### Prompt 31
FATIA 6.8 — Documentação e validação final da Etapa 6

Parte 1 — Documentação (única alteração permitida nesta fatia). Leia apenas: COMO-RODAR.md (seção "Usar a API" e as seções do frontend) e backend/api.http.
Edite SOMENTE COMO-RODAR.md, em português simples:
- Na lista de rotas, acrescente POST /api/vendedores/{vendedor_id}/anotacoes (uma linha dizendo que grava uma anotação nova do gerente sobre o vendedor; a data é a de hoje, definida pelo servidor).
- Acrescente o aviso de que backend/data/anotacoes_novas.json é criado sozinho, não é versionado e guarda as anotações escritas no site; as anotações originais continuam no CSV, que não é alterado; e que apagar o arquivo apaga só as anotações escritas pelo site.
- Na descrição das telas do frontend, atualize: abas em fila (Feedback, Anotações, Dados) com o card do colaborador embaixo e a seta para trocar de pessoa; botão "Gerar feedback"; resultado em quatro cards de largura total; aba Anotações em formato de chat.
- Não altere outras seções.

Parte 2 — Validação (não altere código). Rode e mostre as saídas reais:
1. Backend, de dentro de backend/: suíte completa (total, falhas e "skipped"). Se as dependências não estiverem instaladas no ambiente, diga e não finja que rodou.
2. Frontend, de dentro de frontend/: `npm test` (total), `npm run lint`, `npm run build`.
3. Varreduras: `grep -rn "fetch(\|axios" frontend/src/pages frontend/src/components` sem resultados; `grep -rn "dangerouslySetInnerHTML" frontend/src` sem resultados; `grep -rn "Gerar roteiro\|dono da conversa\|ListaColaboradores" frontend/src` sem resultados; `grep -rn "sk-\|DEEPSEEK" frontend backend --include=*.js --include=*.jsx --include=*.py` sem chaves; cores soltas (#xxxxxx) fora de frontend/src/estilos/tokens.css (liste as que sobrarem); nenhuma regra de cálculo dentro de backend/endpoints/ (liste os imports de cada arquivo e confirme que não importam pandas).
4. `git status --short`: só arquivos de backend/, frontend/, COMO-RODAR.md, api.http e .gitignore; nenhum .env, venv, node_modules, dist, registro_feedbacks.json nem anotacoes_novas.json.
5. Se for possível, suba backend e frontend em background, confirme com curl que as rotas GET respondem e que http://localhost:5173 responde 200; faça um POST de anotação SOMENTE se o backend estiver usando um arquivo temporário de anotações (nunca grave no arquivo real durante a validação); encerre os processos. NÃO chame POST /api/feedback/gerar (gasta créditos) e NÃO peça, leia nem imprima a chave DEEPSEEK_API_KEY.

Ao final diga claramente: (a) o que foi validado de verdade pelos comandos; (b) o que só eu consigo validar no navegador, com o roteiro do cenário da demo: abrir o app → Feedback já ativo com a Bianca → abas em fila e card embaixo → seta mostra os outros 7 nomes → aba Anotações: escrever uma anotação nova e vê-la no chat → aba Dados → aba Feedback: "Gerar feedback" (sem aviso) → quatro cards em largura total na ordem Pontos positivos, Pontos de melhoria, Possíveis motivos, Roteiro de conversa sugerido → visão Regional: contagem de anotações e cobertura; (c) pendências reais (por exemplo: o histórico de roteiros preparados na aba Feedback não atualiza sozinho depois de gerar, se isso ainda for verdade; anotações do chat guardam só a data, não a hora).

Não declare a Etapa 6 concluída antes de eu colar o resultado do fluxo real. Lembre-me de registrar no DIARIO.md o que decidi, o que deu errado e o que aprendi, sem escrever por mim. Não faça commit. Mensagem de commit sugerida: "Documenta anotações do site e conclui ajustes da Etapa 6".

### Prompt 32
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de npm/pip install, criar pastas, rodar build que gere arquivos, git add/commit/checkout). Pode apenas LER arquivos e listar pastas.

Vou te passar uma sequência de prompts, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar. Não implemente nada por conta própria.

Projeto: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Um assistente de IA que ajuda o gerente Diego Furtado (C0030, loja L004) a preparar o feedback da vendedora Bianca Rocha (C0031) com base nos indicadores de vendas e nas anotações dele. A gerente regional Patrícia Lemos acompanha numa visão executiva.

Estado atual: as Etapas 0 a 6 estão prontas.
- backend/ (FastAPI + Pandas + DeepSeek): rotas GET /health, GET /api/vendedores/{loja_id}, GET /api/vendedores/{vendedor_id}/historico, POST /api/vendedores/{vendedor_id}/anotacoes, POST /api/feedback/gerar e GET /api/regional/desempenho-gerente. Os roteiros gerados ficam gravados em backend/data/registro_feedbacks.json (com o conteúdo completo das quatro listas).
- frontend/ (React + Vite, JavaScript): cliente Axios central, serviços, estado global em src/context/, tokens de design em src/estilos/, componentes em src/components/ (BarraLateral, NavegacaoAbas, SeletorColaborador, Cabecalho, AreaCentral, VisualizadorRoteiro etc.), páginas em src/pages/ e funções puras com testes em src/utilitarios/.
Vamos agora fazer a "Etapa 7", em fatias pequenas. O que vai mudar:
1. Aba Feedback, parte "Roteiros já preparados": hoje só mostra período e data, sem o conteúdo (o backend não manda o texto no histórico). Cada item passará a ter uma setinha; ao clicar, ele expande e mostra o roteiro completo daquela geração (os quatro cards). Isso exige o backend passar a mandar o conteúdo no histórico. Também, ao gerar um feedback novo, ele deve entrar na lista na hora, sem recarregar a página.
2. Barra lateral: fica grudada na lateral esquerda do site, como um pequeno menu que pode ser expandido ou recolhido; recolhida, mostra só os ícones. Todo o resto (o conteúdo) ocupa o restante da largura da página.
3. Header novo: nome "Feedback Inteligente" e subtítulo "Assistente de IA para feedback" (no lugar de "Co-piloto de feedback para a liderança da Rede Aurora"); do lado direito, o usuário que está vendo o sistema: nome (ex.: Diego) e, embaixo, o cargo (ex.: Gerente), com uma setinha que expande e mostra a outra opção (Patrícia, Regional). Só existem esses dois usuários e escolher um deles troca a visão (gerente ou regional) que já existe no app.
4. Footer novo: "Desenvolvido por Sarah Domingues" e o Instagram @sarahdev.css.

Leia agora, sem alterar:
1. README.md, BRIEFING.md (seção "Desafio 3 — O feedback que ninguém dá"), COMO-RODAR.md, DIARIO.md e .gitignore.
2. Frontend: package.json, index.html, src/App.jsx, App.css, main.jsx, constantes.js; todo src/context/ (AppProvider.jsx, appReducer.js, appReducer.test.js, useApp.js, appContext.js); src/components/ (Cabecalho, BarraLateral, NavegacaoAbas, SeletorColaborador, AreaCentral, VisualizadorRoteiro, Selo, EstadoCarregando, EstadoErro, EstadoVazio e os CSS ligados); src/pages/PaginaFeedback.jsx e PaginaFeedback.css (principalmente o bloco "Roteiros já preparados") e PaginaRegional.jsx (só o início); src/utilitarios/ (periodoDoRoteiro.js, formatadores.js, seletorColaborador.js e seus testes); src/estilos/tokens.css e base.css; e frontend/DESIGN.md (frontmatter, "Colors" e "Do's and Don'ts").
3. Backend: contracts/vendedores.py (FeedbackPreparadoDTO e HistoricoVendedorResposta), contracts/feedback.py (FeedbackRoteiroDTO e FeedbackGerarResposta), contracts/mapeadores.py (feedback_preparado_de e resposta_de_feedback), domain/registro_feedback.py, services/registro_feedback.py, endpoints/vendedores.py e os testes que falam de feedbacks_preparados (procure em backend/tests/).

Responda só com um resumo curto (máx. 15 linhas) do que entendeu, do estado atual e das dúvidas. Aponte em especial: (a) como o histórico de roteiros preparados chega à tela hoje e o que falta para o conteúdo chegar; (b) quais testes existentes dizem que o histórico NÃO traz o conteúdo (e que, portanto, precisarão mudar de propósito); (c) qualquer ponto em que o plano acima conflite com o código. Não escreva código e não crie arquivos.

Convenções que valem para TODOS os prompts seguintes:
- Separação de responsabilidades: nenhuma regra de negócio, nenhum cálculo de métrica e nenhuma chamada à LLM no frontend. Formatar para exibição é permitido. As telas NUNCA chamam fetch nem axios diretamente: leem o estado e chamam as ações do contexto com useApp(). Valor indisponível (null) aparece como "—", nunca "NaN", "null" ou "undefined".
- Onde cada coisa pode mudar: só mexa no backend na fatia 7.1; só mexa em src/context/ na fatia 7.3; só mexa em src/services/ se um prompt pedir (nenhum pede); só mexa em COMO-RODAR.md na fatia 7.10. Se faltar algo fora do que o prompt autoriza, PARE e me avise em vez de contornar.
- Sem dependências novas (nem react-router, Tailwind, testing-library, nem pacotes Python novos). Navegação por estado (visões e abas do contexto). O lucide-react instalado é a versão 1.x, que NÃO tem ícones de marcas (como o do Instagram): não use ícone de marca; confira com `npm run build` que cada ícone escolhido existe.
- Visual: siga o DESIGN.md e os tokens de src/estilos/tokens.css. Nada de cores soltas fora dos tokens. Contraste AA, foco visível, alvos de toque com pelo menos 44px, animações respeitando prefers-reduced-motion. Menus que abrem e fecham seguem o padrão "disclosure": um botão com aria-expanded e aria-controls que mostra/esconde um bloco; Esc fecha e devolve o foco ao botão. Não use role="menu" nem "listbox".
- Todo texto vindo da IA ou digitado pelo usuário é exibido como TEXTO simples do React. Nunca use dangerouslySetInnerHTML.
- Textos da interface em português (pt-BR), claros e sem jargão; mensagens de erro humanas.
- Nomes de arquivos e identificadores em português, seguindo o que já existe; um componente por arquivo, com o CSS ao lado e classes prefixadas.
- Lógica isolável vai em funções puras em src/utilitarios/*.js com testes .test.js (o frontend usa `node --test`, sem navegador e sem JSX). Componentes são validados com `npm run build` e `npm run lint`.
- Backend: imports absolutos a partir de backend/, endpoints finos, testes com unittest em backend/tests/, rodados de dentro de backend/ com o python do venv (`python -m unittest discover -s tests -t .`; Windows: backend/venv/Scripts/python). Testes nunca chamam a internet. NUNCA peça, leia ou imprima a chave DEEPSEEK_API_KEY.
- Comandos de validação do frontend (de dentro de frontend/): `npm run build`, `npm run lint`, `npm test`. A suíte existente deve continuar passando (se um teste antigo precisar mudar porque o comportamento mudou de propósito, diga qual e por quê).
- Regras do repositório: mudanças pequenas e coesas; NÃO faça git commit/add/push/amend/reset (eu faço os commits); nunca coloque chaves ou segredos em arquivos versionados; não modifique dados/, prompts/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md nem .claude/.
- Não invente dados nem fatos; confira no código, nos contratos e nos CSVs. Se algo do prompt contradisser o código, pare e me avise.
- Comandos de shell simples, um por vez, sem one-liners longos. Se a sessão for interrompida, na retomada verifique `git status --short` e só crie o que ainda não existir.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: todo código que você escrever ou alterar (JavaScript, JSX, CSS, Python e testes) deve ser bem comentado, em português (pt-BR) e em linguagem simples, para que qualquer pessoa, mesmo sem conhecer a linguagem, entenda o que acontece em cada parte. Regras:
  1. Todo arquivo novo começa com um comentário de 2 a 4 linhas dizendo, em palavras simples, para que serve e como se encaixa no projeto (JS/JSX: /** ... */ antes dos imports; CSS: /* ... */ no topo; Python: docstring no topo).
  2. Todo componente e toda função tem comentário de bloco (JS: /** ... */; Python: docstring) explicando o que faz, o que recebe (props ou parâmetros), o que devolve e, quando ajudar, um exemplo curto (ex.: "usuarioDaVisao('gerente') devolve { nome: 'Diego', cargo: 'Gerente' }").
  3. Dentro das funções e componentes, comente cada bloco lógico explicando o que está sendo feito e POR QUÊ, não só repetindo o código. Dentro do JSX use {/* comentário */}. Evite comentários óbvios linha a linha; prefira explicar a intenção.
  4. Explique termos técnicos na primeira vez em que aparecerem no arquivo, com palavras do dia a dia (ex.: "props: os dados que um componente recebe de quem o usa", "estado: informação que muda e faz a tela se atualizar", "hook: função do React que começa com 'use'", "useEffect: roda um código depois que a tela aparece", "ref: uma caixinha que guarda um elemento da tela sem redesenhar", "aria-expanded: avisa leitores de tela se um bloco está aberto ou fechado", "sticky: o elemento gruda numa posição enquanto a página rola", "flexbox: forma de organizar elementos em linha ou coluna", "DTO: o formato dos dados que a API recebe ou devolve", "reducer: função que recebe o estado e uma ação e devolve o novo estado").
  5. Em CSS, comente o que cada grupo de regras estiliza e por que o valor foi escolhido.
  6. Regras de exibição e de negócio escritas em palavras (ex.: "no celular a barra lateral começa recolhida para sobrar espaço ao conteúdo").
  7. Nos testes, comente o que cada teste verifica e por que aquele resultado é o esperado.
  8. Comentários devem ser corretos e estar sempre atualizados: ao alterar um trecho, atualize o comentário dele e o comentário de cabeçalho do arquivo (principalmente onde o texto antigo fala de "sem o conteúdo", "Co-piloto de feedback…", "botões Gerente/Regional" ou "grade de duas colunas", que deixam de ser verdade). Nada de comentários em inglês, jargão sem explicação ou textos longos demais.
  9. Não altere código de fatias anteriores só para adicionar comentários, a não ser que o prompt peça.
- Ao fim de cada prompt, informe: arquivos criados/alterados, comandos de validação executados e o resultado REAL. Não declare algo validado sem ter executado. O que só dá para ver no navegador (aparência, clique, teclado) você NÃO consegue confirmar: diga isso e me dê o passo a passo para eu conferir.

Aguarde o primeiro prompt. Agora responda só com o resumo e as dúvidas, sem modificar nada.

### Prompt 33
FATIA 7.1 — Backend: o histórico passa a trazer o conteúdo de cada roteiro preparado (Etapa 7)

Nesta fatia o backend pode ser alterado, mas só o que está listado aqui. Leia apenas: backend/contracts/vendedores.py (FeedbackPreparadoDTO e onde ele é usado), backend/contracts/feedback.py (FeedbackRoteiroDTO), backend/contracts/mapeadores.py (feedback_preparado_de e resposta_de_feedback), backend/domain/registro_feedback.py, backend/endpoints/vendedores.py (trecho do histórico) e, em backend/tests/, os testes que falam de feedbacks_preparados ou FeedbackPreparadoDTO (procure por esses nomes).

Objetivo: hoje GET /api/vendedores/{vendedor_id}/historico devolve em feedbacks_preparados só feedback_id, mes_referencia e gerado_em. O conteúdo (as quatro listas) já está gravado em registro_feedbacks.json, mas não sai pela API. Faça-o sair, para o frontend poder mostrar os roteiros anteriores.

Tarefas:
1. Em contracts/vendedores.py, acrescente ao FeedbackPreparadoDTO o campo roteiro: FeedbackRoteiroDTO (o mesmo DTO que o POST /api/feedback/gerar já usa, para não existirem dois formatos), com descrição em português. Atualize as docstrings que dizem "resumo, sem o conteúdo".
2. Em contracts/mapeadores.py, faça feedback_preparado_de preencher o roteiro reaproveitando a conversão que resposta_de_feedback já faz do dicionário do registro para FeedbackRoteiroDTO (não duplique código: extraia uma pequena função auxiliar compartilhada se for o caminho mais limpo). Atualize a docstring (que diz que o conteúdo NÃO entra) e o comentário em endpoints/vendedores.py ("O texto do roteiro não entra no histórico").
3. Se um registro antigo estiver com o roteiro num formato que o DTO não aceite, a rota NÃO pode quebrar o histórico inteiro com erro 500: siga o comportamento que o RegistroFeedbackService já tem para dados inválidos (ele levanta DadosIndisponiveisError ao ler o arquivo) e confirme em teste que o histórico responde com o erro amigável de sempre, e não com um erro técnico. Não invente um comportamento novo.
4. Ajuste os testes existentes que afirmavam que o conteúdo não aparece (diga exatamente quais mudaram e por quê) e acrescente testes: o histórico da Bianca depois de registrar um roteiro traz feedbacks_preparados[0].roteiro com as quatro listas iguais às gravadas; a ordem continua do mais novo para o mais antigo; sem roteiros a lista segue vazia; o JSON bruto não contém NaN; o POST /api/feedback/gerar continua com o mesmo formato de antes.
5. Não altere a rota regional nem o POST de geração. Não altere o frontend.

Validação (execute de verdade): suíte completa a partir de backend/ (total, falhas e "skipped"), `git status --short` (só arquivos de backend/, e nenhum registro_feedbacks.json) e, se as dependências estiverem instaladas, suba o uvicorn de dentro de backend/ e confira com curl em /api/vendedores/C0031/historico que a estrutura de feedbacks_preparados mudou como esperado (use um arquivo de registro temporário; NÃO chame o POST /api/feedback/gerar, que gasta créditos). Encerre o servidor.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código Python novo ou alterado ("DTO", "mapeador" e "registro" explicados em palavras simples; docstrings atualizadas).

Não faça commit. Mensagem de commit sugerida: "Inclui o conteúdo dos roteiros preparados no histórico".

### Prompt 34
FATIA 7.2 — Frontend: funções de apoio dos roteiros preparados, com testes (Etapa 7)

Pré-requisito: 7.1 concluída. Leia apenas: frontend/src/utilitarios/periodoDoRoteiro.js e seu teste (a função rotuloPeriodo já existe), frontend/src/utilitarios/formatadores.js (formatarDataHora, formatarMes), frontend/src/utilitarios/ordenarAnotacoes.test.js (só o estilo), backend/contracts/vendedores.py (FeedbackPreparadoDTO) e backend/contracts/feedback.py (FeedbackGerarResposta).

Objetivo: lógica pura para a lista de roteiros anteriores. Nada de React aqui.

Tarefas:
1. Crie frontend/src/utilitarios/roteirosPreparados.js com:
   - tituloDoRoteiroPreparado(item): usa o rotuloPeriodo que já existe (ex.: "outubro de 2026" ou "Todo o histórico"); item inválido → "—".
   - descricaoDoRoteiroPreparado(item): "Gerado em 11/11/2026 às 14:30" (use formatarDataHora); sem data → "Data indisponível".
   - roteiroTemConteudo(item): true só se item.roteiro tiver as quatro listas (pontos_positivos, pontos_melhoria, possiveis_motivos, roteiro_conversa) como arrays (podem estar vazios). Qualquer outra coisa → false.
   - itemPreparadoDeResposta(resposta): recebe a resposta do POST de geração (feedback_id, mes_referencia, gerado_em, roteiro...) e devolve { feedback_id, mes_referencia, gerado_em, roteiro } no formato dos itens de feedbacks_preparados; resposta sem feedback_id ou sem roteiro válido → null.
   - incluirNoInicio(lista, item): devolve uma NOVA lista com o item na primeira posição; se já existir um item com o mesmo feedback_id, ele é substituído (sem duplicar); lista inválida → só o item; item inválido (null) → a lista como veio, copiada. A lista original nunca é alterada.
2. Crie frontend/src/utilitarios/roteirosPreparados.test.js (node:test e node:assert) cobrindo todos os casos acima, incluindo período null, data inválida, roteiro faltando uma das listas, lista original intacta e ausência de duplicados.
3. Não crie componentes nem altere outros arquivos.

Validação (execute de verdade): `npm test` (total e testes novos), `npm run lint`, `npm run build`, `git status --short` (só 2 arquivos novos).

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS: cabeçalho, comentário de bloco com exemplo de entrada e saída em cada função, "função pura" e "imutável" explicados em palavras simples, e cada teste dizendo o que verifica e por que o resultado é o esperado.

Não faça commit. Mensagem de commit sugerida: "Adiciona funções de apoio dos roteiros preparados".

### Prompt 35
FATIA 7.3 — Contexto: um feedback recém-gerado entra na lista de preparados (Etapa 7)

Pré-requisito: 7.2 concluída. Nesta fatia você pode alterar frontend/src/context/. Leia apenas: frontend/src/context/appReducer.js (tratamento de FEEDBACK_SUCESSO, atualizarFeedback e a forma de estado.detalhes), appReducer.test.js, AppProvider.jsx (ação gerarFeedback) e frontend/src/utilitarios/roteirosPreparados.js.

Objetivo: hoje, depois de gerar um feedback, a lista "Roteiros já preparados" só se atualiza ao recarregar os dados do colaborador. Faça a lista atualizar na hora, sem nova chamada HTTP, reaproveitando a resposta que a geração já devolveu.

Tarefas:
1. No tratamento de FEEDBACK_SUCESSO do appReducer.js, além de guardar o feedback em estado.feedbacks[vendedorId] como já faz, use itemPreparadoDeResposta e incluirNoInicio para colocar o novo item no começo de estado.detalhes.dados.feedbacks_preparados, MAS só quando: os detalhes estiverem carregados com sucesso, detalhes.dados.vendedor_id for igual a acao.vendedorId (proteção contra resposta de outra pessoa) e a resposta for válida. Caso contrário o estado dos detalhes não muda (e nada quebra). Crie novos objetos em vez de alterar os existentes (estado imutável).
2. Não mude AppProvider.jsx nem a forma de nenhum outro pedaço do estado, a menos que seja indispensável; se for, explique antes.
3. Em appReducer.test.js acrescente testes (sem alterar os existentes; se algum precisar mudar, diga qual e por quê) para: sucesso com detalhes da mesma pessoa → item novo no início e os antigos mantidos; sucesso repetido com o mesmo feedback_id → sem duplicar; sucesso de outra pessoa → detalhes intactos; detalhes ainda não carregados → nada quebra e o feedback continua guardado; resposta sem roteiro → detalhes intactos; o estado anterior não é alterado.

Validação (execute de verdade): `npm test` (total e testes novos), `npm run lint`, `npm run build`, `git status --short`.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e atualize o comentário de cabeçalho do reducer e do FEEDBACK_SUCESSO (que passa a atualizar também a lista de preparados), explicando o porquê em palavras simples.

Não faça commit. Mensagem de commit sugerida: "Faz feedback novo entrar na lista de roteiros preparados".

### Prompt 36
FATIA 7.4 — Aba Feedback: roteiros anteriores com seta para expandir (Etapa 7)

Pré-requisito: 7.1, 7.2 e 7.3 concluídas. Leia apenas: frontend/src/pages/PaginaFeedback.jsx e PaginaFeedback.css (principalmente o bloco "Roteiros já preparados"), frontend/src/components/VisualizadorRoteiro.jsx e VisualizadorRoteiro.css, frontend/src/components/EstadoVazio.jsx, frontend/src/components/SeletorColaborador.jsx e .css (para repetir o padrão de seta e foco), frontend/src/utilitarios/roteirosPreparados.js, frontend/src/estilos/tokens.css e base.css.

Objetivo: cada roteiro preparado passa a ter uma setinha; ao clicar, o item expande e mostra o roteiro completo daquela geração, com os quatro cards (Pontos positivos, Pontos de melhoria, Possíveis motivos, Roteiro de conversa sugerido, em largura total, um embaixo do outro, como no resultado atual).

Tarefas:
1. Crie frontend/src/components/ListaRoteirosPreparados.jsx (+ .css). Props: roteiros (a lista feedbacks_preparados, já do mais novo para o mais antigo; mantenha essa ordem) e vendedorNome.
   - Lista (ul) com um item por roteiro. Cada item tem uma linha de cabeçalho com o título (tituloDoRoteiroPreparado), a descrição (descricaoDoRoteiroPreparado) e, à direita, um botão só com ícone de seta (ChevronDown; ChevronUp quando aberto) com aria-label "Mostrar roteiro de <título>" / "Esconder roteiro de <título>", aria-expanded e aria-controls apontando para o bloco do conteúdo. Área de clique mínima de 44x44px; foco visível. A linha inteira pode ser clicável como atalho, mas o botão da seta é o controle acessível principal.
   - Só um item aberto por vez (guarde em estado local o feedback_id aberto; abrir outro fecha o anterior; clicar no aberto fecha). Ao carregar, todos começam fechados.
   - Item aberto mostra o VisualizadorRoteiro daquele roteiro, dentro do próprio item, em largura total. O item ficará visualmente destacado quando aberto (borda ou fundo dos tokens, não só cor).
   - Item sem conteúdo (roteiroTemConteudo falso): botão desabilitado e o texto "Conteúdo indisponível para este roteiro." (caso de registros antigos).
   - Esc com o foco dentro de um item aberto fecha o item e devolve o foco ao botão da seta.
2. Em VisualizadorRoteiro.jsx acrescente a prop opcional ocultarCabecalho (padrão false). Com true, não mostra o cabeçalho ("Roteiro para…", período, "Gerado em…"), porque o item da lista já mostra essas informações. Comportamento padrão intacto. Confira a hierarquia de títulos (h2/h3/h4) dentro da página para não pular nível ou repetir h3 desnecessário; ajuste só o necessário e diga o que mudou.
3. Em PaginaFeedback.jsx, troque a lista atual de "Roteiros já preparados" (período e data, sem conteúdo) por <ListaRoteirosPreparados roteiros={preparados} vendedorNome={...} />. Mantenha o título "Roteiros já preparados", a frase explicando que "roteiro preparado" não significa "feedback realizado" e o EstadoVazio quando a lista vem vazia. Apague o CSS da lista antiga que ficou sem uso.
4. Todo texto do roteiro continua sendo texto simples do React. Sem dangerouslySetInnerHTML.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short`. NÃO gere feedback real (gasta créditos). Passo a passo para eu conferir no navegador (backend no ar, com pelo menos um roteiro já gravado em backend/data/registro_feedbacks.json — se não houver nenhum, me diga que preciso gerar um): a lista mostra os roteiros do mais novo para o mais antigo, todos fechados; clicar na seta abre o roteiro completo com os quatro cards; abrir outro fecha o primeiro; Esc fecha; depois de gerar um feedback novo, ele aparece no topo da lista sem recarregar a página; a navegação por teclado funciona.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco com as props, cada estado e handler explicado com o PORQUÊ, "aria-expanded", "acordeão" e "estado local" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Permite expandir roteiros anteriores na aba Feedback".

### Prompt 37
FATIA 7.5 — Rodapé (Etapa 7)

Leia apenas: frontend/src/constantes.js, frontend/src/components/Cabecalho.jsx e Cabecalho.css (para combinar com o visual do topo), frontend/src/estilos/tokens.css e base.css e frontend/DESIGN.md (Colors e Do's and Don'ts).

Objetivo: criar o componente do rodapé. Ele ainda NÃO entra no App (isso é a fatia 7.6).

Tarefas:
1. Em constantes.js ACRESCENTE, sem alterar o que existe: AUTORA_NOME = 'Sarah Domingues' e AUTORA_INSTAGRAM = 'sarahdev.css' (só o nome de usuário, sem o @), com comentário explicando que são os créditos do projeto.
2. Crie frontend/src/components/Rodape.jsx (+ Rodape.css): um <footer> com o texto "Desenvolvido por Sarah Domingues" e, ao lado ou embaixo (conforme a largura), o link "@sarahdev.css". O link aponta para https://www.instagram.com/sarahdev.css/ (monte a URL a partir da constante), abre em nova aba com target="_blank" e rel="noopener noreferrer", e tem aria-label "Instagram de Sarah Domingues (abre em nova aba)". Sem ícone de marca (o lucide-react 1.x não tem); se quiser um ícone neutro, use um do lucide que exista e confirme no build, com aria-hidden.
3. Visual: mesma família visual do cabeçalho (superfície escura do DESIGN.md com texto claro, ou o par que o cabeçalho já usa), contraste AA no texto e no link, link com sublinhado ou outro indicador além da cor, foco visível, alvo de toque de pelo menos 44px de altura no link, texto centralizado em telas estreitas e distribuído em linha em telas largas. Só tokens.
4. Não altere App.jsx nem outros componentes.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short` (constantes.js alterado + 2 arquivos novos). Diga que a conferência visual fica para a fatia 7.6.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, "rel=noopener noreferrer" e "target=_blank" explicados em palavras simples, e por que o link tem aria-label).

Não faça commit. Mensagem de commit sugerida: "Cria rodapé com créditos da autora".


### Prompt 38
FATIA 7.6 — Casca do app: cabeçalho no topo, rodapé embaixo e o conteúdo ocupando o resto (Etapa 7)

Pré-requisito: 7.5 concluída. Leia apenas: frontend/src/App.jsx, App.css, index.css, main.jsx, frontend/src/components/BarraLateral.jsx e BarraLateral.css, AreaCentral.jsx e AreaCentral.css, Cabecalho.jsx e Cabecalho.css, Rodape.jsx e Rodape.css, SeletorColaborador.css e NavegacaoAbas.css (só larguras), frontend/src/estilos/base.css e tokens.css.

Objetivo: mudar a estrutura geral da página. Hoje há um container centralizado com largura máxima de 1200px e margens em volta. Passa a ser: cabeçalho em toda a largura no topo; no meio, a barra lateral COLADA na borda esquerda da tela e o conteúdo ocupando TODO o restante da largura; rodapé em toda a largura embaixo, sempre no fim da tela mesmo quando o conteúdo é curto. A parte recolhível da lateral vem na fatia 7.7; aqui ela só passa a ficar colada na lateral.

Tarefas:
1. App.jsx: estrutura <div class="app"> com, em ordem, <Cabecalho />, um <div class="app__corpo"> contendo <BarraLateral /> (só na visão do gerente, como hoje) e <AreaCentral />, e <Rodape />. Remova o uso de "app-layout" e das áreas de grade antigas.
2. App.css: a página ocupa no mínimo a altura da tela (min-height: 100dvh) organizada em coluna (flexbox ou grid de 3 linhas: cabeçalho, corpo que cresce, rodapé). Remova o max-width: 1200px e o padding externo do container. O corpo é uma linha: barra lateral à esquerda com largura própria e área central com flex: 1 e min-width: 0 (para tabelas largas rolarem dentro do próprio container em vez de estourar a página).
3. BarraLateral.css: a lateral encosta na borda esquerda (sem margem externa, sem arredondar o lado esquerdo), com borda só no lado direito, ocupando toda a altura do corpo (do fim do cabeçalho ao começo do rodapé; use align-self: stretch). O conteúdo interno pode ficar "sticky" no topo (position: sticky) para acompanhar a rolagem em páginas longas; escolha a solução mais simples que funcione e explique em comentário. Largura atual (260px) por enquanto.
4. AreaCentral.css: a área central recebe o espaçamento interno (padding dos tokens) que antes vinha do container e passa a ocupar todo o espaço restante. Sem largura máxima. Na visão regional (sem barra lateral) o conteúdo ocupa a largura inteira.
5. Cabeçalho e rodapé: ocupam a largura toda, com o espaçamento interno nas laterais (para o texto não colar na borda), e sem cantos arredondados nas pontas da tela.
6. Mobile (menos de 768px): por enquanto mantenha a barra lateral empilhada acima do conteúdo como já é hoje (a fatia 7.7 muda isso).
7. Remova regras de layout que ficaram sem uso (confirme com grep) e atualize os comentários de cabeçalho de App.jsx e App.css.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador: em tela larga a lateral encosta na borda esquerda e o conteúdo preenche o resto; o rodapé fica no fim da tela mesmo com pouco conteúdo e desce junto quando o conteúdo é longo; na visão Regional (por enquanto pelos botões atuais do cabeçalho) o conteúdo ocupa a largura toda; nenhuma barra de rolagem horizontal na página; sem erros no console.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho de arquivo, cada grupo de regras CSS explicado com o PORQUÊ, "flexbox", "sticky", "min-height: 100dvh" e "min-width: 0" explicados em palavras simples).

Não faça commit. Mensagem de commit sugerida: "Reestrutura a página com cabeçalho, corpo em largura total e rodapé".

### Prompt 39
FATIA 7.7 — Barra lateral recolhível: expandida com texto ou recolhida só com ícones (Etapa 7)

Pré-requisito: 7.6 concluída. Leia apenas: frontend/src/components/BarraLateral.jsx e .css, NavegacaoAbas.jsx e .css, SeletorColaborador.jsx e .css, frontend/src/App.css, frontend/src/estilos/base.css (classe ui-visualmente-oculto) e frontend/src/utilitarios/seletorColaborador.js.

Objetivo: a barra lateral vira um pequeno menu fixo na lateral que o usuário expande ou recolhe. Recolhida, mostra apenas ícones; expandida, mostra ícones e textos como hoje. O resto da página ocupa o espaço que sobrar.

Tarefas:
1. BarraLateral.jsx: estado local expandida (booleano). Valor inicial: expandida em telas com 768px ou mais e RECOLHIDA em telas menores (use window.matchMedia dentro do inicializador do useState, com proteção caso matchMedia não exista; comente o porquê: no celular o conteúdo precisa do espaço). No topo da barra, um botão de alternar com ícone (PanelLeftClose quando expandida e PanelLeftOpen quando recolhida; se algum nome não existir na versão instalada, use ChevronsLeft/ChevronsRight e me conte), aria-label "Recolher menu" / "Expandir menu", aria-expanded e aria-controls apontando para o conteúdo da barra, 44x44px, foco visível. Passe uma prop recolhida para NavegacaoAbas e SeletorColaborador.
2. NavegacaoAbas.jsx/.css: com recolhida=true cada aba mostra só o ícone, centralizado, e o nome continua disponível para leitores de tela (mantenha o texto no DOM com a classe ui-visualmente-oculto) e como dica ao passar o mouse (atributo title). A aba ativa continua claramente destacada (não só por cor). O comportamento de tablist, setas e foco não muda.
3. SeletorColaborador.jsx/.css: com recolhida=true mostra só o círculo com as iniciais do colaborador (aria-label com o nome e o cargo, title com o nome); a seta e a lista dos outros nomes não aparecem. Clicar no círculo EXPANDE a barra (pede isso por uma função recebida por prop, por exemplo aoExpandir) em vez de abrir a lista. Se a lista estava aberta quando a barra é recolhida, ela fecha. O carregamento da lista e a seleção automática da Bianca continuam funcionando mesmo com a barra recolhida (o componente continua montado).
4. BarraLateral.css: largura de 260px expandida e 64px recolhida, com transição de largura suave (desligada por prefers-reduced-motion); textos que não cabem somem sem quebrar o layout (não use overflow que corte o foco); a lateral continua colada na borda esquerda e a área central continua com flex: 1, então ocupa todo o espaço restante quando a barra muda de largura.
5. Mobile: REMOVA o empilhamento da barra acima do conteúdo (a regra da fatia anterior para menos de 768px). Em telas pequenas a barra continua na lateral (começa recolhida, 64px) e o conteúdo ocupa o resto. Confirme que as páginas continuam utilizáveis em 360px de largura.
6. Esta fatia NÃO guarda a preferência (expandida/recolhida) entre visitas; isso fica como possível melhoria futura. Anote no relatório.
7. Atualize comentários de cabeçalho dos arquivos alterados.

Validação (execute de verdade): `npm test`, `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador (backend no ar + `npm run dev`): em tela larga a barra abre expandida; o botão do topo recolhe para só ícones (64px) e o conteúdo se alarga; passar o mouse num ícone mostra o nome; clicar no círculo do colaborador com a barra recolhida a expande; com a barra expandida a seta mostra os outros colaboradores; na janela estreita (F12, modo dispositivo, 360px) a barra começa recolhida na lateral; navegação por teclado completa; sem erros no console.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco com as novas props, "matchMedia", "transition", "title" e "aria-label" explicados em palavras simples; explique por que o nome continua no DOM mesmo recolhido).

Não faça commit. Mensagem de commit sugerida: "Torna a barra lateral recolhível, só com ícones quando recolhida".

### Prompt 40
FATIA 7.8 — Cabeçalho: nome, novo subtítulo e organização do topo (Etapa 7)

Pré-requisito: 7.7 concluída. Leia apenas: frontend/src/components/Cabecalho.jsx e Cabecalho.css, frontend/index.html, frontend/src/estilos/tokens.css e base.css e frontend/DESIGN.md (Colors e Do's and Don'ts).

Objetivo: ajustar o cabeçalho. O menu de usuário (Diego/Patrícia) vem na fatia 7.9; por enquanto os botões atuais "Gerente" e "Regional" continuam funcionando, só reposicionados.

Tarefas:
1. O título continua "Feedback Inteligente" (único h1 da página) e o subtítulo passa a ser exatamente "Assistente de IA para feedback" (no lugar de "Co-piloto de feedback para a liderança da Rede Aurora").
2. Layout do cabeçalho em toda a largura: identidade (título + subtítulo) à esquerda e, à direita, uma região reservada para a área do usuário, onde por enquanto ficam os botões Gerente/Regional atuais. Em telas estreitas o conteúdo quebra para duas linhas sem sobrepor nem cortar nada. Use a mesma superfície escura/contraste já usados (tokens), sem cantos arredondados nas pontas da tela e com o espaçamento lateral definido na fatia 7.6. Se o cabeçalho for fixo no topo (sticky) ou não, mantenha como está.
3. Procure com grep por "Co-piloto" em todo frontend/ (inclusive index.html, comentários e testes) e atualize onde fizer sentido para o texto novo, listando no relatório cada lugar alterado. Não altere o título da aba do navegador, a menos que ele traga o subtítulo antigo.
4. Atualize os comentários de cabeçalho de Cabecalho.jsx e Cabecalho.css.

Validação (execute de verdade): `grep -rn "Co-piloto" frontend --include=*.jsx --include=*.js --include=*.html --include=*.css` (sem resultados, exceto node_modules), `npm test`, `npm run lint`, `npm run build`, `git status --short`. Passo a passo para eu conferir no navegador: título e novo subtítulo à esquerda, botões à direita, tudo legível em 360px e em tela larga.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS e mantenha os comentários corretos.

Não faça commit. Mensagem de commit sugerida: "Atualiza subtítulo e organização do cabeçalho".

### Prompt 41
FATIA 7.9 — Menu de usuário no cabeçalho: Diego e Patrícia (Etapa 7)

Pré-requisito: 7.8 concluída. Leia apenas: frontend/src/constantes.js (VISOES e as constantes do rodapé), frontend/src/components/Cabecalho.jsx e Cabecalho.css, frontend/src/components/SeletorColaborador.jsx e .css (padrão de seta, foco e Esc), frontend/src/utilitarios/seletorColaborador.js (iniciaisDoNome) e seu teste, frontend/src/context/AppProvider.jsx (mudarVisao) e appReducer.js (MUDAR_VISAO).

Objetivo: no lado direito do cabeçalho, mostrar quem está usando o sistema: o nome (ex.: Diego) e embaixo o cargo (ex.: Gerente), com uma setinha ao lado. Ao clicar na seta, aparece a outra opção (Patrícia, Regional); escolhê-la troca o usuário e, com isso, a visão do app. Só existem esses dois usuários. Os dois botões "Gerente/Regional" da fatia anterior são REMOVIDOS.

Tarefas:
1. Em constantes.js ACRESCENTE USUARIOS: uma lista com dois itens, { visao: VISOES.GERENTE, nome: 'Diego', cargo: 'Gerente' } e { visao: VISOES.REGIONAL, nome: 'Patrícia', cargo: 'Regional' }. Comente que o sistema não tem login: são os dois perfis da demonstração, e que o usuário escolhido define a visão do app (a visão já é guardada pelo contexto). Os nomes completos (Diego Furtado e Patrícia Lemos) continuam vindo da API onde são exibidos; aqui só vai o primeiro nome do menu.
2. Crie frontend/src/utilitarios/usuarios.js com usuarioDaVisao(visao) (devolve o item de USUARIOS daquela visão; visão desconhecida → o primeiro usuário da lista) e outrosUsuarios(visao) (devolve uma NOVA lista sem o usuário da visão atual, na ordem da constante). Funções puras com testes em usuarios.test.js (visão do gerente, da regional, desconhecida, e a lista original intacta).
3. Crie frontend/src/components/MenuUsuario.jsx (+ .css), sem props, usando useApp() para ler estado.visao e chamar mudarVisao(visao):
   - Fechado: círculo com iniciais (iniciaisDoNome, aria-hidden), o nome em destaque e, EMBAIXO dele, o cargo em texto menor; ao lado, o botão só com ícone de seta (ChevronDown; ChevronUp quando aberto), aria-label "Trocar de usuário", aria-expanded e aria-controls, 44x44px, foco visível.
   - Aberto: um painel logo abaixo do botão, alinhado à direita do cabeçalho (position absolute dentro de um container relativo; garanta z-index acima do conteúdo e que não seja cortado nem estoure a tela em 360px), listando SÓ as outras opções (outrosUsuarios), cada uma um <button> com iniciais, nome e cargo. Escolher uma chama mudarVisao(visao), fecha o painel e devolve o foco ao botão da seta.
   - Esc fecha e devolve o foco à seta; clicar fora do menu também fecha (listener de clique no documento, removido ao desmontar ou ao fechar; explique em comentário); clicar de novo na seta alterna.
   - Cores e contraste conforme o cabeçalho (superfície escura com texto claro) e o painel com a superfície clara e texto escuro dos tokens; transição suave desligada por prefers-reduced-motion.
4. Em Cabecalho.jsx, troque os botões Gerente/Regional por <MenuUsuario /> na região da direita. Remova do Cabecalho.css as regras dos botões antigos que ficaram sem uso.
5. Quando a visão muda para Regional, a barra lateral some e o conteúdo ocupa a largura toda (comportamento que já existe); ao voltar para Gerente, o colaborador selecionado e a aba continuam como estavam (o contexto já guarda isso; confirme lendo o reducer e me diga se não for verdade).

Validação (execute de verdade): `npm test` (total e testes novos), `npm run lint`, `npm run build`, `grep -rn "aria-pressed" frontend/src/components/Cabecalho.jsx` sem resultados, `git status --short`. Passo a passo para eu conferir no navegador: no topo à direita aparece "Diego" com "Gerente" embaixo e a seta; ao clicar na seta aparece só "Patrícia / Regional"; escolher Patrícia troca para a visão regional (sem barra lateral) e o menu passa a mostrar "Patrícia / Regional" com "Diego / Gerente" como outra opção; Esc e clique fora fecham; funciona só com teclado; em 360px o painel não é cortado.

Lembrete de qualidade: siga a regra de COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS (cabeçalho, comentário de bloco, cada useEffect/ref/handler explicado com o PORQUÊ, "position absolute/relative", "z-index", "aria-expanded" e "clique fora" explicados em palavras simples, e testes dizendo o que verificam).

Não faça commit. Mensagem de commit sugerida: "Cria menu de usuário Diego/Patrícia no cabeçalho".

### Prompt 42
FATIA 7.10 — Documentação e validação final da Etapa 7

Parte 1 — Documentação (única alteração permitida nesta fatia). Leia apenas: COMO-RODAR.md (seções que descrevem a rota do histórico e as telas do frontend).
Edite SOMENTE COMO-RODAR.md, em português simples:
- Na descrição de GET /api/vendedores/{vendedor_id}/historico, diga que feedbacks_preparados agora traz também o conteúdo (as quatro listas) de cada roteiro já gerado.
- Na descrição das telas: cabeçalho com o nome do projeto, o subtítulo "Assistente de IA para feedback" e o menu de usuário (Diego/Gerente e Patrícia/Regional, que troca a visão); barra lateral colada na lateral esquerda, que pode ser recolhida (só ícones) ou expandida; conteúdo ocupando o resto da página; rodapé com os créditos; aba Feedback com a lista de roteiros anteriores que se expandem pela seta.
- Não altere outras seções.

Parte 2 — Validação (não altere código). Rode e mostre as saídas reais:
1. Backend, de dentro de backend/: suíte completa (total, falhas e "skipped"). Se as dependências não estiverem instaladas, diga e não finja que rodou.
2. Frontend, de dentro de frontend/: `npm test` (total), `npm run lint`, `npm run build`.
3. Varreduras: `grep -rn "fetch(\|axios" frontend/src/pages frontend/src/components` sem resultados; `grep -rn "dangerouslySetInnerHTML" frontend/src` sem resultados; `grep -rn "Co-piloto\|aria-pressed" frontend/src` sem resultados (aria-pressed só pode sobrar se for de outro componente: explique); `grep -rn "sk-\|DEEPSEEK" frontend backend --include=*.js --include=*.jsx --include=*.py` sem chaves; cores soltas (#xxxxxx) fora de frontend/src/estilos/tokens.css (liste as que sobrarem); nenhuma regra de cálculo dentro de backend/endpoints/ (liste os imports e confirme que não importam pandas).
4. `git status --short`: só arquivos de backend/, frontend/ e COMO-RODAR.md; nenhum .env, venv, node_modules, dist, registro_feedbacks.json nem anotacoes_novas.json.
5. Se for possível, suba backend e frontend em background, confirme com curl que as rotas GET respondem e que http://localhost:5173 responde 200; encerre os processos. NÃO chame POST /api/feedback/gerar (gasta créditos) e NÃO peça, leia nem imprima a chave DEEPSEEK_API_KEY.

Ao final diga claramente: (a) o que foi validado de verdade pelos comandos; (b) o que só eu consigo validar no navegador, com o roteiro da demo: abrir o app → cabeçalho com "Feedback Inteligente", "Assistente de IA para feedback" e "Diego / Gerente" → barra lateral colada à esquerda, recolher e expandir → aba Feedback → gerar feedback → ele aparece no topo de "Roteiros já preparados" → abrir pela seta um roteiro antigo e ver os quatro cards → trocar para "Patrícia / Regional" pelo menu → conteúdo ocupando a largura toda → voltar para Diego → rodapé com "Desenvolvido por Sarah Domingues" e "@sarahdev.css" (clicar abre o Instagram numa nova aba); (c) pendências reais (por exemplo: a preferência de barra recolhida/expandida não é guardada entre visitas; não há login, os dois usuários são fixos).

Não declare a Etapa 7 concluída antes de eu colar o resultado do fluxo real. Lembre-me de registrar no DIARIO.md o que decidi, o que deu errado e o que aprendi, sem escrever por mim. Não faça commit. Mensagem de commit sugerida: "Documenta novo layout e roteiros anteriores (Etapa 7)".

### Prompt 43
CONTEXTO DA ETAPA 8 (somente leitura, NÃO modifique, crie, apague ou renomeie nenhum arquivo, e não execute comandos que alterem o repositório).

Vou te passar uma sequência de prompts da Etapa 8, um por vez. Até eu colar um prompt de implementação, sua única tarefa é ler, entender e confirmar.

Tarefa agora:
1. Leia, sem alterar: AI-AGENTS.md, backend/config.py, backend/contracts/regional.py, backend/endpoints/regional.py, backend/services/consolidado_regional.py, frontend/src/App.jsx, frontend/src/constantes.js, frontend/src/components/BarraLateral.jsx, frontend/src/components/SeletorColaborador.jsx e frontend/src/pages/PaginaRegional.jsx.
2. Responda apenas com um resumo curto (máx. 15 linhas) do que entendeu e liste dúvidas, se houver. Não escreva código nem crie arquivos.

O que vamos construir na Etapa 8: evoluir a visão da Regional (Patrícia Lemos) para funcionar como o espaço de acompanhamento dela, no mesmo padrão visual e estrutural da visão do Gerente (Diego):
- Na barra lateral da regional: exibir as 3 abas (Feedback, Anotações, Dados) e trocar o seletor de vendedor por um seletor de loja (mostrando a loja L004 — Aurora Shopping Centro com botão de seta para expandir, preparado para outras lojas).
- Na aba Anotações da regional: exibir as anotações da regional em formato de chat (balões por dia) e permitir registrar novas anotações da regional no backend (JSON à parte, sem alterar o CSV original).
- Na aba Feedback da regional: permitir que Patrícia gere um roteiro de feedback com IA (DeepSeek, método SBI) voltado para o gerente da loja (Diego), usando os resultados da loja, a cobertura de feedbacks do time e as anotações da regional, além de listar os roteiros já preparados para o gerente.
- Na aba Dados da regional: exibir os indicadores consolidados da loja (resultado mês a mês e acompanhamento de feedbacks dos vendedores).

Convenções que valem para TODAS as fatias da Etapa 8:
- Separação de responsabilidades: zero cálculo de métricas ou montagem de prompt no frontend; tudo vem via contratos REST do backend.
- Comentários de código obrigatórios e didáticos em português (pt-BR).
- Não faça git commit/push/amend/reset; não altere CSVs originais em backend/data/ nem arquivos de dados/, prompts/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md ou .claude/.
- Ao fim de cada prompt, informe arquivos criados/alterados, comandos de validação executados e a saída real. Aguarde a Fatia 8.1a.

### Prompt 44
FATIA 8.1a — Persistência de novas anotações da regional (Backend)

Leia apenas: backend/config.py, backend/domain/anotacao_regional.py, backend/services/registro_anotacoes.py, backend/services/data_loader.py (trecho de anotações da regional) e backend/endpoints/dependencias.py.

Objetivo: permitir que a regional salve novas anotações em um arquivo JSON próprio, sem alterar backend/data/anotacoes_regional.csv, seguindo exatamente o padrão já usado para as anotações do gerente.

1. Em backend/config.py ACRESCENTE:
   - `ANOTACOES_REGIONAL_NOVAS_ARQUIVO = DATA_DIR / "anotacoes_regional_novas.json"`
   - `AUTORA_REGIONAL_PADRAO = "Patrícia Lemos"`
   (reaproveite `ANOTACAO_TEXTO_MAXIMO = 1000` para o limite de caracteres).
2. Crie backend/services/registro_anotacoes_regional.py com a classe `RegistroAnotacoesRegionalService(arquivo: Path = ANOTACOES_REGIONAL_NOVAS_ARQUIVO)`:
   - Mesma proteção de concorrência (`threading.Lock`) e escrita atômica (`.tmp` + `flush` + `os.fsync` + `os.replace`) de `RegistroAnotacoesService`.
   - Métodos públicos:
     - `listar() -> list[AnotacaoRegional]` (devolve lista vazia se o arquivo não existir; levanta `DadosIndisponiveisError` sem apagar o arquivo se estiver corrompido).
     - `registrar(texto: str, autora: str = AUTORA_REGIONAL_PADRAO, data_anotacao: date | None = None) -> AnotacaoRegional` (valida `texto.strip()` não vazio e tamanho <= `ANOTACAO_TEXTO_MAXIMO`, levantando `AnotacaoInvalidaError` em português; usa `date.today()` se `data_anotacao` for None).
3. Atualize `DataLoader.__init__` para aceitar `registro_anotacoes_regional: RegistroAnotacoesRegionalService | None = None` (padrão None mantém compatibilidade total com todos os testes antigos). Atualize `DataLoader.listar_anotacoes_regional()` para unir as anotações do CSV com as novas do serviço (quando informado), ordenadas por data crescente, sem cachear as novas em memória (para que uma anotação recém-gravada apareça imediatamente).
4. Em backend/endpoints/dependencias.py ACRESCENTE `obter_registro_anotacoes_regional()` com `@lru_cache(maxsize=1)` e passe-o para `DataLoader` dentro de `obter_data_loader()`.

Crie testes em backend/tests/test_registro_anotacoes_regional.py cobrindo: gravação e leitura em arquivo temporário, texto vazio/só espaços -> `AnotacaoInvalidaError`, texto > 1000 chars -> `AnotacaoInvalidaError`, arquivo JSON inválido -> `DadosIndisponiveisError` sem apagar o arquivo, e `DataLoader.listar_anotacoes_regional()` unindo as 5 anotações do CSV com uma nova gravada no serviço temporário.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: rode `pytest` completo a partir de backend/ e mostre a saída real. Não faça commit. Mensagem sugerida: "Adiciona persistência de novas anotações da regional".

### Prompt 45
FATIA 8.1b — Endpoint POST /api/regional/anotacoes (Backend)

Pré-requisito: 8.1a concluída. Leia apenas: backend/contracts/regional.py, backend/contracts/vendedores.py (AnotacaoNovaRequisicao), backend/endpoints/regional.py, backend/endpoints/vendedores.py (trecho de POST anotações, se existir, ou estilo) e backend/endpoints/dependencias.py.

1. Em backend/contracts/regional.py ACRESCENTE `AnotacaoRegionalNovaRequisicao(BaseModel)`:
   - `model_config = ConfigDict(str_strip_whitespace=True)`
   - `texto: str = Field(min_length=1, max_length=ANOTACAO_TEXTO_MAXIMO, description=...)`
2. Em backend/endpoints/regional.py ACRESCENTE:
   - `POST /api/regional/anotacoes`, status_code=201, `response_model=AnotacaoRegionalDTO`, documentando 400 e 500 com `ErroResposta`.
   - A rota é fina (`def`, não `async def`): recebe `requisicao: AnotacaoRegionalNovaRequisicao` e `registro: RegistroAnotacoesRegionalService = Depends(obter_registro_anotacoes_regional)`, chama `registro.registrar(requisicao.texto)` e devolve `AnotacaoRegionalDTO(data=criada.data, autora=criada.autora, texto=criada.texto)`.
3. Em backend/main.py confirme que `allow_methods` no CORS já inclui `"POST"`.

Crie testes em backend/tests/test_endpoints_regional_anotacoes.py com TestClient e dependency_overrides apontando para arquivo temporário:
- POST válido -> 201 com `data` de hoje, `autora == "Patrícia Lemos"` e `texto` preservado;
- GET /api/regional/desempenho-gerente logo em seguida inclui a nova anotação na lista `anotacoes_regional` (6 itens no total);
- POST com texto vazio `""` ou `"   "` -> 400 com `{"erro": ...}`;
- POST com texto acima de 1000 caracteres -> 400 com `{"erro": ...}`.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: rode `pytest` completo a partir de backend/ e mostre a saída real. Não faça commit. Mensagem sugerida: "Cria endpoint POST /api/regional/anotacoes".

### Prompt 46
FATIA 8.2a — Prompt da IA para feedback ao gerente da loja (Backend)

Leia apenas: backend/services/prompt_feedback.py, backend/services/consolidado_regional.py, backend/services/validador_feedback.py e backend/domain/feedback_roteiro.py.

Objetivo: construir o prompt puro (sistema + usuário) que prepara um roteiro de feedback da gerente regional (Patrícia) para o gerente da loja (Diego), aplicando o método SBI (Situação, Comportamento, Impacto) sobre os dados da loja e as anotações de visita da regional.

1. Crie backend/services/prompt_feedback_regional.py (módulo puro: zero rede, zero SDK openai, zero leitura de arquivo):
   - Defina `SISTEMA_PROMPT_REGIONAL`: instrui a IA como Co-piloto Executivo da Gerente Regional no Varejo. Ela apoia a gerente regional (Patrícia) a preparar uma conversa de feedback individual com o gerente da loja (Diego). Regras obrigatórias:
     - Método SBI (Situação, Comportamento, Impacto) ligado aos números da loja e às observações de visita;
     - Proibido mencionar nomes de outros gerentes ou outras lojas (apenas o gerente avaliado e sua loja);
     - Proibido inventar números fora do bloco de dados;
     - Linguagem direta, construtiva e em português (pt-BR);
     - Saída estritamente em JSON válido com as 4 listas já conhecidas: `pontos_positivos`, `pontos_melhoria`, `possiveis_motivos`, `roteiro_conversa` (com perguntas abertas para o gerente).
   - Implemente `montar_prompt_feedback_regional(consolidado: dict, mes_referencia: str | None = None) -> tuple[str, str]`:
     - Recebe o dicionário devolvido por `ConsolidadoRegional.obter_desempenho_gerente()` e `mes_referencia` opcional (`"AAAA-MM"` ou `None` para todo o histórico).
     - Se `mes_referencia` for informado e não existir em `consolidado["resultado_loja"]`, levanta `ValueError` em português.
     - Monta a mensagem de usuário contendo:
       1. Identidade: loja (`loja_id`, `loja_nome`), gerente avaliado (`gerente_nome`), período analisado (`formatar_mes(mes_referencia)` ou histórico completo).
       2. Resultados da loja: se `mes_referencia` foi escolhido, destaca aquele mês (sinalizando se `mes_parcial` é True) e resume os demais meses para contexto; se `mes_referencia` é None, lista todos os meses em ordem cronológica com meta da loja, vendas da loja, atingimento da loja, vendas dos vendedores, atingimento dos vendedores, vendas do gerente no caixa e participação do gerente.
       3. Liderança e acompanhamento de feedbacks do time: `total_vendedores`, `vendedores_com_roteiro`, `cobertura` formatada em percentual e `total_roteiros_preparados` (deixando claro que são roteiros preparados/gerados).
       4. Anotações da regional sobre a loja em ordem cronológica (data formatada + texto).
2. Verifique se `validar_roteiro_feedback` em backend/services/validador_feedback.py pode ser reutilizado passando `vendedor_nome=gerente_nome` e `nomes_colegas=()` (confirme e documente no docstring; se precisar de ajuste mínimo, explique).

Crie testes em backend/tests/test_prompt_feedback_regional.py testando:
- Montagem com todo o histórico (`mes_referencia=None`): inclui nome do gerente, nome da loja, valores formatados em reais/percentual de outubro, cobertura de feedbacks e todas as anotações da regional;
- Montagem com `mes_referencia="2026-10"` e com `mes_referencia="2026-11"` (aviso de mês parcial);
- Mês inexistente (ex.: `"2025-01"`) -> `ValueError`;
- `validar_roteiro_feedback` aprova um `FeedbackRoteiro` válido voltado ao gerente.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: rode `pytest` completo a partir de backend/ e mostre a saída real. Não faça commit. Mensagem sugerida: "Cria construtor de prompt de feedback da regional para o gerente".

###Prompt 47
FATIA 8.2b — Contratos Pydantic do feedback da regional

Leia apenas: backend/contracts/regional.py, backend/contracts/feedback.py e backend/contracts/vendedores.py (apenas FeedbackPreparadoDTO).
Execute uma ferramenta por vez (não use `batch`).

1. Em `backend/contracts/regional.py` ACRESCENTE:
   - `FeedbackRegionalGerarRequisicao(BaseModel)`: `model_config = ConfigDict(str_strip_whitespace=True)` e `mes_referencia: str | None = Field(default=None, ...)` com o mesmo validador regex `^\d{4}-(0[1-9]|1[0-2])$` de `FeedbackGerarRequisicao`.
   - `FeedbackRegionalGerarResposta(BaseModel)`: `feedback_id: str`, `loja_id: str`, `loja_nome: str`, `gerente_id: str`, `gerente_nome: str`, `mes_referencia: str | None`, `gerado_em: datetime`, `roteiro: FeedbackRoteiroDTO`.
   - Em `DesempenhoGerenteResposta`, ACRESCENTE `feedbacks_preparados: list[FeedbackPreparadoDTO] = Field(default_factory=list, description="Roteiros de feedback já gerados pela regional para o gerente da loja.")`.
2. Crie `backend/tests/test_contratos_regional_feedback.py` validando:
   - `FeedbackRegionalGerarRequisicao` aceita `{}` e `{"mes_referencia": "2026-10"}` e recusa `"2026-13"`;
   - `DesempenhoGerenteResposta` continua aceitando dicts sem `feedbacks_preparados` (padrão `[]`) e também com itens preenchidos.

Siga os COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS. Validação: rode `pytest tests/test_contratos_regional_feedback.py -q` dentro de `backend/`. Não faça commit. Mensagem sugerida: "Define contratos de feedback da regional".

### Prompt 48
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de pip/npm install, git add/commit/checkout).

Projeto: "FullStore Feedback Inteligente" (Desafio 3, Rede Aurora). Backend FastAPI + Pandas, frontend React + Vite. O gerente Diego Furtado (C0030, loja L004) prepara feedback para os vendedores; a gerente regional Patrícia Lemos acompanha. Etapas 0 a 7 prontas. Estamos na ETAPA 8: transformar a visão da regional num espaço de trabalho igual ao do Diego, em fatias pequenas.

Objetivo da Etapa 8 (o que a Patrícia deve ver e fazer):
- Barra lateral como a do Diego, mas em vez de escolher o colaborador ela escolhe a LOJA. O card mostra a loja analisada (L004, Aurora Shopping Centro, gerente Diego Furtado) e a seta abre a lista das OUTRAS lojas. Hoje só existe uma loja com dados, então a lista aberta mostra um aviso de que não há outras lojas; o componente deve funcionar com N lojas.
- Três abas, as mesmas do gerente: Feedback, Anotações e Dados.
  - Dados: o que a página da regional mostra hoje (resultado da loja mês a mês e acompanhamento dos feedbacks dos vendedores).
  - Anotações: conversa em formato de chat, onde a Patrícia escreve e vê as anotações dela sobre a loja e o gerente (as 5 do CSV anotacoes_regional.csv + as novas digitadas na interface).
  - Feedback: ela escolhe o período, gera um roteiro de feedback PARA O GERENTE da loja (SBI + perguntas abertas empáticas) e vê os roteiros já preparados.
- Vocabulário: o sistema só sabe que o roteiro foi GERADO/PREPARADO; nunca escreva "realizado".

Leia SOMENTE estes arquivos (não explore o resto):
- backend: config.py, main.py, endpoints/regional.py, endpoints/dependencias.py, contracts/regional.py, services/consolidado_regional.py, services/registro_anotacoes.py, services/registro_feedback.py, domain/registro_feedback.py, domain/anotacao_regional.py, services/data_loader.py (só construtor e os métodos de anotações regional/gerente), services/llm_service.py (só gerar_roteiro_feedback) e a lista de arquivos de backend/tests/.
- frontend/src: App.jsx, constantes.js, context/appReducer.js, context/AppProvider.jsx, components/BarraLateral.jsx, NavegacaoAbas.jsx, SeletorColaborador.jsx, AreaCentral.jsx, pages/PaginaRegional.jsx, PaginaAnotacoes.jsx, PaginaFeedback.jsx, services/regionalService.js e a lista de arquivos de utilitarios/.

Responda em no máximo 12 linhas: o que entendeu, o que será reaproveitado e dúvidas. Não escreva código.

Decisões de arquitetura já tomadas (valem para TODAS as fatias):
1. Roteiros para o gerente ficam num registro SEPARADO (backend/data/registro_feedbacks_regional.json). Motivo: o consolidado da regional conta todos os registros de registro_feedbacks.json como "roteiros de vendedores"; misturar falsearia a cobertura.
2. Anotações novas da regional ficam em backend/data/anotacoes_regional_novas.json, no mesmo padrão de anotacoes_novas.json. O CSV de origem nunca é alterado.
3. A autora da anotação NÃO vem do frontend: o servidor grava "Patrícia Lemos" (constante em config.py) e a data de hoje no servidor.
4. O endpoint atual GET /api/regional/desempenho-gerente continua existindo, sem mudanças de comportamento.
5. Novos endpoints (todos sob /api/regional): GET /lojas; GET /lojas/{loja_id}/historico; POST /lojas/{loja_id}/anotacoes; POST /feedback/gerar. Loja desconhecida => 404 pelo LojaNaoEncontradaError que já existe.
6. Reaproveitar ao máximo: FeedbackRoteiro, LLMService (cliente, retry, validação), VisualizadorRoteiro, ListaRoteirosPreparados, montarOpcoesDePeriodo, CartaoIndicador, Selo, Estado*, agruparPorDia, rotuloDoDia, ordenarAnotacoes.

Regras para TODOS os prompts seguintes:
- Leia apenas os arquivos que cada prompt citar; não explore o repositório por conta própria. Se algo do prompt contradisser o código real, pare e me avise antes de seguir.
- Mudanças pequenas e coesas. NÃO faça git commit/add/push/amend/reset (eu faço os commits). Nunca coloque segredos em arquivos versionados e NUNCA peça, leia ou imprima DEEPSEEK_API_KEY. Testes nunca chamam a internet (use cliente fake).
- Fatias de BACKEND não tocam o frontend. Fatias de FRONTEND não tocam o backend. Não modifique dados/, prompts/, apresentacao/, DIARIO.md, README.md, BRIEFING.md, AGENTS.md, AI-AGENTS.md, CLAUDE.md nem .claude/, a menos que o prompt peça.
- Backend: imports absolutos a partir de backend/; testes com unittest em backend/tests/, rodados de dentro de backend/ com o python do venv: `python -m unittest discover -s tests -t .` (Windows: backend/venv/Scripts/python). A suíte existente deve continuar passando. Endpoints finos: sem regra de negócio nem métrica nas rotas. Taxas são fração 0–1; indisponível é null, nunca NaN.
- Frontend: de dentro de frontend/ rode `npm test`, `npm run lint` e `npm run build`. Nenhuma regra de negócio, cálculo de métrica ou chamada à LLM no frontend: só consumir a API. Sem dependências novas e sem router.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo código novo (backend, frontend e testes): português simples; cabeçalho de 2 a 4 linhas em todo arquivo; docstring/comentário de bloco em toda função e componente (o que faz, recebe, devolve, exemplo curto quando ajudar); comentar cada passo explicando o PORQUÊ; explicar termos técnicos na primeira vez com palavras do dia a dia; fórmulas escritas em palavras; testes comentados dizendo o que verificam. Não altere código antigo só para comentar.
- Comandos de shell simples, um por vez. Se a sessão for interrompida, na retomada rode `git status --short` e só crie o que ainda não existir.
- Ao final de cada prompt informe: arquivos criados/alterados, comandos de validação rodados e o resultado REAL. Não declare nada validado sem ter executado.

Aguarde o primeiro prompt de implementação.

### Prompt 49
FATIA 8.1a — Configuração e entidade RegistroFeedbackGerente (Etapa 8, backend)

Leia apenas: backend/config.py, backend/domain/registro_feedback.py, backend/tests/test_registro_feedback_entidade.py (só o estilo) e .gitignore.

Contexto: a regional vai gerar roteiros de feedback para o gerente da loja. Precisamos guardar isso à parte dos roteiros dos vendedores (decisão 1 do contexto).

1. Em backend/config.py ACRESCENTE, sem alterar o que existe: REGIONAL_NOME = "Patrícia Lemos" (comente: sem login no projeto, a regional é fixa), REGISTRO_FEEDBACKS_REGIONAL_ARQUIVO = DATA_DIR / "registro_feedbacks_regional.json" e ANOTACOES_REGIONAL_NOVAS_ARQUIVO = DATA_DIR / "anotacoes_regional_novas.json" (comente: uso local, criados sozinhos, fora do git).
2. Em .gitignore (único arquivo de configuração que esta fatia pode alterar) adicione os dois arquivos JSON novos, com comentário curto.
3. Crie backend/domain/registro_feedback_gerente.py: `RegistroFeedbackGerente`, dataclass(frozen=True): loja_id, loja_nome, gerente_id, gerente_nome, gerado_em (datetime com fuso UTC), roteiro (dict com as 4 listas), mes_referencia (str | None = None), feedback_id (uuid4 por padrão). Mesmo padrão de RegistroFeedback: cópia defensiva das listas no __post_init__, para_dict() com data em ISO 8601 e @classmethod de_dict() que levanta ValueError se faltar campo ou o tipo estiver errado. Não altere RegistroFeedback.
4. Teste novo backend/tests/test_registro_feedback_gerente_entidade.py: ida e volta para_dict/de_dict preservando fuso; imutabilidade (FrozenInstanceError); alterar a lista original não muda o registro; de_dict com campo faltando e com data inválida => ValueError.

Validação: suíte completa com saída real; `git check-ignore -v backend/data/registro_feedbacks_regional.json backend/data/anotacoes_regional_novas.json` deve mostrar as regras.

Não faça commit. Mensagem sugerida: "Adiciona configuração e entidade RegistroFeedbackGerente".

### Prompt 50
FATIA 8.1b — Serviço de anotações novas da regional (Etapa 8, backend)

Pré-requisito: 8.1a concluída. Leia apenas: backend/services/registro_anotacoes.py, backend/domain/anotacao_regional.py, backend/domain/excecoes.py, backend/config.py e backend/tests/test_registro_anotacoes.py (só o estilo).

Crie backend/services/registro_anotacoes_regional.py com `RegistroAnotacoesRegionalService`, copiando o PADRÃO de RegistroAnotacoesService (lock, leitura que não apaga arquivo corrompido, escrita atômica com arquivo temporário + os.replace, arquivo inexistente = lista vazia), mas com AnotacaoRegional (data, autora, texto):
- construtor com `arquivo: Path = ANOTACOES_REGIONAL_NOVAS_ARQUIVO`;
- `registrar(texto: str, autora: str = REGIONAL_NOME, data: date | None = None) -> AnotacaoRegional`: texto vazio/só espaços, acima de ANOTACAO_TEXTO_MAXIMO ou data inválida => AnotacaoInvalidaError com as MESMAS mensagens amigáveis do serviço do gerente; data padrão = hoje NO SERVIDOR; só as pontas do texto são aparadas;
- `listar() -> tuple[AnotacaoRegional, ...]` na ordem do arquivo.
Reaproveite AnotacaoInvalidaError e DadosIndisponiveisError existentes (não crie exceções novas).

Teste novo backend/tests/test_registro_anotacoes_regional.py com diretório temporário: arquivo inexistente => (); registrar grava e listar devolve; texto vazio, só espaços e acima do limite => AnotacaoInvalidaError; JSON corrompido => DadosIndisponiveisError e o arquivo NÃO é apagado; duas threads gravando ao mesmo tempo não perdem registros.

Não altere o serviço do gerente. Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria serviço de anotações novas da regional".

### Prompt 51
FATIA 8.1c — DataLoader enxerga as anotações novas da regional (Etapa 8, backend)

Pré-requisito: 8.1b concluída. Leia apenas: backend/services/data_loader.py (construtor, o trecho que mescla registro_anotacoes com o CSV do gerente e listar_anotacoes_regional), backend/endpoints/dependencias.py e backend/tests/test_data_loader_regional.py.

1. No construtor do DataLoader ACRESCENTE o parâmetro opcional `registro_anotacoes_regional: RegistroAnotacoesRegionalService | None = None` (padrão None: comportamento atual intacto).
2. `listar_anotacoes_regional()` passa a devolver CSV + anotações novas, em ordem cronológica estável (empate de data: CSV primeiro). Siga a MESMA exceção ao cache já documentada para registro_anotacoes: o CSV continua em cache, mas as novas são lidas do serviço a cada chamada. Sem o serviço, o retorno é idêntico ao de hoje.
3. Em endpoints/dependencias.py crie `obter_registro_anotacoes_regional()` (lru_cache(maxsize=1), singleton) e passe o serviço ao DataLoader em `obter_data_loader()`. Não altere as outras dependências.

Testes (acrescente a backend/tests/test_data_loader_regional.py ou crie test_data_loader_anotacoes_regional_novas.py): sem serviço continua com 5 anotações; com serviço fake/temporário, registrar uma nova faz listar_anotacoes_regional() devolver 6, a nova por último; ordem cronológica; as 5 originais não mudam. Confirme que test_endpoints_regional.py continua passando.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "DataLoader passa a incluir as anotações novas da regional".

### Prompt 52
FATIA 8.1d — Serviço RegistroFeedbackRegionalService (Etapa 8, backend)

Pré-requisito: 8.1a concluída. Leia apenas: backend/services/registro_feedback.py, backend/domain/registro_feedback_gerente.py, backend/tests/test_registro_feedback.py (só o estilo).

Crie backend/services/registro_feedback_regional.py com `RegistroFeedbackRegionalService`, mesmo padrão de RegistroFeedbackService (lock, escrita atômica, leitura que não apaga arquivo corrompido, arquivo inexistente = lista vazia), com RegistroFeedbackGerente e o arquivo REGISTRO_FEEDBACKS_REGIONAL_ARQUIVO:
- `registrar(loja_id, loja_nome, gerente_id, gerente_nome, mes_referencia, roteiro: FeedbackRoteiro) -> RegistroFeedbackGerente` (usa roteiro.para_dict());
- `listar(loja_id: str | None = None) -> list[RegistroFeedbackGerente]` do MAIS NOVO para o mais antigo (confirme no serviço atual a ordem que o histórico do vendedor usa e mantenha a mesma convenção);
- `ultimo_de(loja_id) -> RegistroFeedbackGerente | None`.
Em endpoints/dependencias.py crie `obter_registro_feedbacks_regional()` (lru_cache, singleton). Não altere RegistroFeedbackService nem o consolidado.

Teste novo backend/tests/test_registro_feedback_regional.py (diretório temporário): arquivo inexistente => []; registrar/listar; filtro por loja_id; ordem do mais novo para o mais antigo; JSON corrompido => DadosIndisponiveisError sem apagar; gravação concorrente sem perda. Inclua um teste que prova que registrar aqui NÃO altera o arquivo de registro dos vendedores.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria registro de roteiros da regional para o gerente".

### Prompt 53
FATIA 8.2a — Prompt do feedback da regional para o gerente (Etapa 8, backend)

Leia apenas: backend/services/prompt_feedback.py (SISTEMA_PROMPT, formatadores e _montar_mensagem_usuario), backend/services/consolidado_regional.py, backend/domain/anotacao_regional.py e backend/tests/test_prompt_feedback.py (só o estilo).

Crie backend/services/prompt_feedback_regional.py com `montar_mensagens_regional(desempenho: dict, mes_referencia: str | None = None) -> list[dict]`, onde `desempenho` é o dict de ConsolidadoRegional.obter_desempenho_gerente(). Reaproveite os formatadores de prompt_feedback.py (importe, não copie).

Mensagem de sistema NOVA (constante SISTEMA_PROMPT_REGIONAL), na mesma estrutura e tom do prompt atual (papel, SBI, honestidade, justiça e cuidado, tom, saída JSON com as 4 chaves e exemplo): você é o Co-piloto de Liderança e Feedback no Varejo apoiando a GERENTE REGIONAL a preparar uma conversa de feedback individual e privada com o GERENTE DA LOJA. A regional é dona da conversa; a IA prepara, não fala com o gerente. Regras específicas: usar APENAS os números e as anotações fornecidos; resultado da loja deve separar vendas dos vendedores e vendas do gerente (o gerente também atende no caixa; a meta da loja não inclui o gerente); respeitar mês parcial e meta ausente; não comparar com outras lojas nem citar vendedores pelo nome para expor ou comparar; sem rótulos, ironia ou diagnóstico psicológico; começar reconhecendo o que é bom; mesmas 4 listas e mesmos limites de itens; pelo menos 3 perguntas abertas empáticas; combinado de uma ação pequena e data de acompanhamento.

Mensagem do usuário: identidade (loja, gerente), período analisado (um mês ou todo o histórico), tabela textual de resultado_loja (meta, vendas da loja, atingimento, vendas dos vendedores, vendas do gerente, participação do gerente, mês parcial), acompanhamento dos feedbacks (cobertura e quantos vendedores sem roteiro preparado, lembrando que "preparado" não é "realizado") e as anotações da regional em ordem cronológica. Valores None viram "sem dado"; nenhuma conta nova (só formatar o que já veio calculado).

Teste novo backend/tests/test_prompt_feedback_regional.py com dict sintético: duas mensagens (system/user); o sistema cita SBI, JSON e as 4 chaves; o usuário traz loja, gerente, números formatados, anotações e a frase sobre "preparado"; mês pedido filtra o resultado ao mês; None vira "sem dado"; nenhum dado inventado.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria o prompt do feedback da regional para o gerente".

### Prompt 54
FATIA 8.2b — LLMService gera o roteiro para o gerente (Etapa 8, backend)

Pré-requisitos: 8.2a e 8.1d. Leia apenas: backend/services/llm_service.py inteiro, backend/services/validador_feedback.py, backend/services/consolidado_regional.py (assinaturas) e backend/tests/test_llm_service.py (só o estilo com cliente fake).

Em LLMService ACRESCENTE, sem mudar o comportamento atual, `gerar_roteiro_feedback_gerente(self, desempenho: dict, mes_referencia: str | None = None) -> FeedbackRoteiro`: monta as mensagens com montar_mensagens_regional e reaproveita o MESMO caminho de chamada que o método atual usa (cliente, timeout, modo JSON, max_tokens, interpretação, validação e nova tentativa com mensagem de correção, exceções de LLM). Extraia para um helper privado apenas o que for realmente comum, SEM alterar o comportamento nem as assinaturas existentes; se isso exigir mexer demais, pare e me avise.

Atenção ao validador: leia como ele bloqueia nomes (de colegas) e frases genéricas e confirme se as regras servem para o roteiro do gerente. Se precisar de um parâmetro opcional (por exemplo, quais nomes bloquear), acrescente-o com padrão que preserva o comportamento atual e me explique a decisão.

Testes com cliente fake em um arquivo novo backend/tests/test_llm_service_regional.py: resposta válida vira FeedbackRoteiro; JSON inválido => exceção de LLM já existente; resposta reprovada na validação provoca UMA nova tentativa e depois passa; as mensagens enviadas ao fake são as do prompt regional. Nenhuma chamada de rede.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "LLMService gera roteiro de feedback para o gerente".

### Prompt 55
FATIA 8.3a — Contratos da regional por loja (Etapa 8, backend)

Leia apenas: backend/contracts/regional.py, backend/contracts/vendedores.py (AnotacaoNovaRequisicao), backend/contracts/feedback.py, backend/contracts/mapeadores.py (feedback_preparado_de, roteiro_do_registro) e backend/tests/test_contratos_regional.py (só o estilo).

Em backend/contracts/regional.py ACRESCENTE (sem alterar os modelos existentes), todos com Field(description=...) em português:
- `LojaResumoDTO`: loja_id, loja_nome, gerente_id, gerente_nome;
- `ListaLojasResposta`: lojas: list[LojaResumoDTO];
- `FeedbackGerenteGeradoDTO` (um roteiro já preparado): feedback_id, mes_referencia (str | None), gerado_em (datetime), roteiro (FeedbackRoteiroDTO reaproveitado);
- `HistoricoLojaResposta(DesempenhoGerenteResposta)`: herda tudo e acrescenta feedbacks_preparados: list[FeedbackGerenteGeradoDTO] (do mais novo para o mais antigo);
- `AnotacaoRegionalNovaRequisicao`: texto (min 1, max ANOTACAO_TEXTO_MAXIMO, mesmas regras e mensagem 400 já usadas pela requisição do gerente);
- `FeedbackRegionalGerarRequisicao`: loja_id (obrigatório, sem espaços nas pontas) e mes_referencia (None ou "AAAA-MM", mesmo padrão);
- `FeedbackRegionalGerarResposta`: feedback_id, loja_id, loja_nome, gerente_id, gerente_nome, mes_referencia, gerado_em, roteiro.
Em contracts/mapeadores.py acrescente `feedback_gerente_de(registro: RegistroFeedbackGerente)` e `resposta_regional_de(registro)`. Vocabulário: "preparado" nas descrições, nunca "realizado".

Testes em arquivo novo backend/tests/test_contratos_regional_loja.py: validação dos campos, limites do texto, mês inválido, herança do histórico, mapeadores com registro sintético, JSON sem NaN.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Cria contratos da regional por loja".

### Prompt 56
FATIA 8.3b — GET /api/regional/lojas e GET /api/regional/lojas/{loja_id}/historico (Etapa 8, backend)

Pré-requisitos: 8.1c, 8.1d e 8.3a. Leia apenas: backend/endpoints/regional.py, backend/endpoints/dependencias.py, backend/services/consolidado_regional.py, backend/domain/excecoes.py (LojaNaoEncontradaError), backend/config.py e backend/tests/test_endpoints_regional.py (só o estilo).

1. Em ConsolidadoRegional ACRESCENTE `listar_lojas() -> list[dict]`: hoje devolve UM item com loja_id/loja_nome da configuração e gerente_id/gerente_nome do gerente carregado. Comente que a lista existe para suportar mais lojas no futuro. Não altere os métodos atuais.
2. Em endpoints/regional.py ACRESCENTE (mantendo a rota atual intacta):
   - `GET /regional/lojas` => ListaLojasResposta;
   - `GET /regional/lojas/{loja_id}/historico` => HistoricoLojaResposta: loja diferente de LOJA_ID (sem diferenciar maiúsculas e espaços nas pontas) => LojaNaoEncontradaError (404, como a rota de vendedores já faz); senão junta obter_desempenho_gerente() com os roteiros de obter_registro_feedbacks_regional().listar(loja_id), mapeados por feedback_gerente_de.
   Rotas finas: nenhuma conta nova aqui. Declare responses 404/500 com ErroResposta.

Testes (arquivo novo backend/tests/test_endpoints_regional_lojas.py, com dependency_overrides e registros em diretório temporário): lista tem 1 loja L004/Diego; histórico traz os mesmos números da rota antiga + feedbacks_preparados vazio; depois de registrar um roteiro fake ele aparece; "l004" e " L004 " funcionam; "L999" => 404 {"erro": "..."}; a rota antiga continua respondendo igual.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Adiciona rotas de lojas e histórico da regional".

### Prompt 57
FATIA 8.3c — POST /api/regional/lojas/{loja_id}/anotacoes (Etapa 8, backend)

Pré-requisitos: 8.1b, 8.1c e 8.3b. Leia apenas: backend/endpoints/vendedores.py (a rota POST de anotações, como modelo), backend/endpoints/regional.py, backend/contracts/regional.py e backend/tests/test_endpoints_anotacoes.py (só o estilo).

Em endpoints/regional.py ACRESCENTE `POST /regional/lojas/{loja_id}/anotacoes` (status 201), corpo AnotacaoRegionalNovaRequisicao (só o texto), resposta AnotacaoRegionalDTO (já existe). Fluxo: loja desconhecida => 404; serviço registra com autora REGIONAL_NOME e data de hoje no servidor (o cliente NÃO manda autora nem data); texto inválido => 400 pelo tratador global existente (AnotacaoInvalidaError). Rota fina, só orquestra.

Testes em backend/tests/test_endpoints_regional_anotacoes.py (arquivo temporário): 201 com autora "Patrícia Lemos" e data de hoje; a nova anotação aparece em GET /regional/lojas/L004/historico e em /regional/desempenho-gerente; texto vazio/só espaços/acima do limite => 400; loja L999 => 404; corpo malformado => 400 no formato {"erro": ...}; tentar enviar "autora" ou "data" no corpo não muda o resultado.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Adiciona POST de anotações da regional".

### Prompt 58
FATIA 8.3d — POST /api/regional/feedback/gerar (Etapa 8, backend)

Pré-requisitos: 8.1d, 8.2b e 8.3b. Leia apenas: backend/endpoints/feedback.py (rota atual, como modelo), backend/endpoints/regional.py, backend/endpoints/dependencias.py e backend/tests/test_endpoints_feedback.py e test_endpoints_feedback_falhas.py (só o estilo).

Em endpoints/regional.py ACRESCENTE `POST /regional/feedback/gerar`: corpo FeedbackRegionalGerarRequisicao, resposta FeedbackRegionalGerarResposta. Use `def` (não async), como a rota atual, pelo mesmo motivo (chamada lenta à IA). Fluxo: 1) valida a loja (desconhecida => 404, SEM chamar a IA); 2) obtém o desempenho do consolidado; 3) pede o roteiro a llm.gerar_roteiro_feedback_gerente(desempenho, mes_referencia); 4) SÓ se o roteiro for válido, grava no registro da regional; 5) devolve a resposta mapeada. Se a IA falhar nada é gravado e o erro sobe para o tratador global (500/502/503). Documente 400/404/500/502/503 como na rota atual.

Testes em backend/tests/test_endpoints_regional_feedback.py com LLM fake via dependency_overrides e registro em diretório temporário: caminho feliz (200, roteiro com as 4 listas, gravado, aparece no histórico da loja); mês inválido => 400; loja L999 => 404 sem chamar o fake; falha da IA (as mesmas exceções da rota atual) => status certo e NADA gravado; o registro dos vendedores e a cobertura do acompanhamento NÃO mudam depois de gerar para o gerente.

Validação: suíte completa com saída real. Não faça commit. Mensagem sugerida: "Adiciona POST de feedback da regional para o gerente".

### Prompt 59
FATIA 8.3e — api.http, documentação e validação do backend da Etapa 8

Leia apenas: backend/api.http, backend/endpoints/regional.py e a seção da API em frontend/README.md (só para saber onde a API é documentada).

1. Em backend/api.http ACRESCENTE exemplos dos 4 novos endpoints (listar lojas, histórico da loja L004, registrar anotação, gerar feedback para o gerente com e sem mes_referencia). Não altere os exemplos existentes.
2. NÃO altere README.md nem COMO-RODAR.md. Se algo da documentação ficou desatualizado, apenas liste.
3. Validação final do backend (execute de verdade): suíte completa; suba o uvicorn e rode `curl` em GET /api/regional/lojas, GET /api/regional/lojas/L004/historico e GET /api/regional/lojas/L999/historico (esperado 404 com {"erro": ...}); POST de uma anotação de teste e, depois, REMOVA o arquivo anotacoes_regional_novas.json criado pelo teste manual (confirme com git status que nada novo ficou versionável). NÃO chame o POST /api/regional/feedback/gerar com a IA real: isso eu faço.
4. Mostre `git status --short` e confirme que só há arquivos de backend/ e do .gitignore.

Diga claramente se o backend da Etapa 8 está concluído ("pronto quando: os 4 endpoints respondem, a suíte passa e a cobertura dos vendedores não é afetada") e liste pendências reais. Mensagem sugerida: "Documenta e valida a API regional por loja".

### Prompt 60
FATIA 8.4a — Estado da visão regional: constantes e reducer (Etapa 8, frontend)

A partir daqui as fatias tocam SÓ o frontend. Leia apenas: frontend/src/constantes.js, context/appReducer.js, context/appReducer.test.js (estilo) e utilitarios/roteirosPreparados.js.

1. constantes.js (ACRESCENTE): nada de nomes de pessoas novos além do necessário; reaproveite STATUS, ABAS, VISOES e ANOTACAO_TEXTO_MAXIMO.
2. appReducer.js: acrescente ao estado inicial `lojas: { status, dados: [], erro }`, `lojaSelecionadaId: null`, `detalhesLoja: { status, dados: null, erro }`, `feedbacksRegional: {}` (por loja_id, como `feedbacks` é por vendedor) e `novaAnotacaoRegional: { status, erro }`. Novos tipos: LOJAS_CARREGANDO/SUCESSO/ERRO, SELECIONAR_LOJA, DETALHES_LOJA_CARREGANDO/SUCESSO/ERRO, FEEDBACK_REGIONAL_CARREGANDO/SUCESSO/ERRO, ANOTACAO_REGIONAL_ENVIANDO/SUCESSO/ERRO. Siga os padrões do reducer atual: respostas atrasadas de uma loja que não é mais a selecionada são ignoradas; SELECIONAR_LOJA limpa detalhesLoja e novaAnotacaoRegional; ANOTACAO_REGIONAL_SUCESSO acrescenta a anotação ao fim de detalhesLoja.dados.anotacoes_regional; FEEDBACK_REGIONAL_SUCESSO guarda a resposta e inclui o item no INÍCIO de detalhesLoja.dados.feedbacks_preparados (reaproveite itemPreparadoDeResposta e incluirNoInicio). O estado da regional atual (`regional`) e todos os tipos existentes continuam intactos; MUDAR_ABA e MUDAR_VISAO não mudam.

Testes novos em context/appReducer.test.js (acrescente, sem apagar os existentes): estado inicial novo; cada transição de lojas e detalhesLoja; resposta de loja antiga ignorada; anotação nova entra no fim; feedback novo entra no início e é guardado por loja; trocar de loja limpa os detalhes; ações antigas continuam funcionando.

Validação: `npm test`, `npm run lint` e `npm run build` com saída real. Não faça commit. Mensagem sugerida: "Adiciona estado da regional por loja ao reducer".

### Prompt 61
FATIA 8.4b — Serviços HTTP da regional por loja (Etapa 8, frontend)

Leia apenas: frontend/src/services/regionalService.js, regionalService.test.js, vendedorService.js, anotacaoService.js, feedbackService.js (TIMEOUT_GERACAO_MS) e erroApi.js.

Em regionalService.js ACRESCENTE ao serviço existente (mantendo obterDesempenhoGerente igual e a fábrica com cliente injetável): 
- `listarLojas({ signal })` => GET /api/regional/lojas;
- `obterHistoricoLoja(lojaId, { signal })` => GET /api/regional/lojas/{id}/historico, com id validado (vazio => ErroApi tipo "validacao") e encodeURIComponent, como vendedorService faz;
- `registrarAnotacaoRegional(lojaId, texto, { signal })` => POST /api/regional/lojas/{id}/anotacoes com { texto } já aparado; texto vazio/não-string => ErroApi de validação com as mesmas mensagens do anotacaoService;
- `gerarFeedbackRegional(lojaId, { mesReferencia, signal })` => POST /api/regional/feedback/gerar com { loja_id } (+ mes_referencia só se informado) e timeout TIMEOUT_GERACAO_MS.
Exporte também as funções soltas, no padrão do arquivo.

Testes em regionalService.test.js (acrescente) com cliente fake: URL, corpo, timeout e signal corretos; validações antes de chamar a rede; mes_referencia omitido quando vazio; as funções antigas seguem passando.

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Adiciona serviços HTTP da regional por loja".

### Prompt 62
FATIA 8.4c — Ações da regional no AppProvider (Etapa 8, frontend)

Pré-requisitos: 8.4a e 8.4b. Leia apenas: frontend/src/context/AppProvider.jsx e appReducer.js.

No AppProvider ACRESCENTE, seguindo os padrões das ações atuais (AbortController, ignorar cancelamento, bloqueio de duplo clique):
- `carregarLojas()`;
- `selecionarLoja(lojaId)`: aborta o pedido anterior, despacha SELECIONAR_LOJA, DETALHES_LOJA_CARREGANDO e busca obterHistoricoLoja;
- `adicionarAnotacaoRegional(lojaId, texto)`: devolve true/false como adicionarAnotacao, sem envio duplicado;
- `gerarFeedbackRegional(lojaId, { mesReferencia })`: bloqueia segunda geração da mesma loja enquanto uma está em andamento.
Registre os novos serviços em SERVICOS_REAIS, entregue as funções no valor do contexto (e no useMemo) e aborte tudo no cleanup do efeito. NÃO remova `carregarRegional` nem o estado `regional`: serão aposentados na fatia 8.7.

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Adiciona ações da regional por loja ao AppProvider".

### Prompt 63
FATIA 8.5a — Seletor de loja (Etapa 8, frontend)

Leia apenas: frontend/src/components/SeletorColaborador.jsx e .css, utilitarios/seletorColaborador.js e seletorColaborador.test.js.

1. Crie utilitarios/seletorLoja.js com funções puras e comentadas: `encontrarLoja(lista, id)`, `outrasLojas(lista, id)` (todas menos a selecionada; sem seleção devolve a lista inteira) e `iniciaisDaLoja(nome)` (ignora "Aurora" e "Shopping"; "Aurora Shopping Centro" => "C"; sem nome => "?"). Teste em utilitarios/seletorLoja.test.js (lista vazia, id inexistente, não muda a lista original, nomes com acento).
2. Crie components/SeletorLoja.jsx e SeletorLoja.css, copiando o COMPORTAMENTO de acessibilidade do SeletorColaborador (card não clicável; botão de seta com aria-label "Trocar de loja", aria-expanded e aria-controls; lista logo abaixo, no fluxo normal; Esc fecha e devolve o foco; ↑/↓ percorrem; versão recolhida só com o círculo e aoExpandir). Do contexto lê estado.lojas, estado.lojaSelecionadaId, carregarLojas e selecionarLoja (use o mesmo padrão jaPediuLista para o StrictMode). Card mostra a loja e o gerente ("Gerente: Diego Furtado"). Quando a lista carrega e nada está selecionado, seleciona a primeira loja (cenário atual: L004). Quando a lista aberta não tem outras lojas, mostre "Não há outras lojas com dados nesta regional.". Estados carregando/erro/vazio com os componentes Estado*.
Não altere SeletorColaborador nem a BarraLateral nesta fatia (o componente ainda não é usado).

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria seletor de loja da regional".

### Prompt 64
FATIA 8.5b — Barra lateral e abas também na visão regional (Etapa 8, frontend)

Pré-requisito: 8.5a. Leia apenas: frontend/src/App.jsx, components/BarraLateral.jsx, NavegacaoAbas.jsx, utilitarios/usuarios.js e constantes.js (VISOES, USUARIOS).

1. App.jsx: a coluna lateral passa a existir nas DUAS visões (remova a condição que a restringe ao gerente) e atualize o comentário.
2. BarraLateral.jsx: o conteúdo depende da visão. Gerente: igual a hoje. Regional: `<SeletorLoja recolhida aoExpandir />` e, quando houver loja selecionada, `<NavegacaoAbas recolhida />`. O título oculto vira "Menu do colaborador" (gerente) ou "Menu da loja" (regional). O estado expandida/recolhida continua local e funcionando.
3. NavegacaoAbas.jsx: remova o bloqueio que devolve null fora do gerente; o aria-label do tablist vira "Seções do colaborador" (gerente) ou "Seções da loja" (regional). As abas, a ordem (Feedback, Anotações, Dados), os ícones e o teclado não mudam. A aba ativa é a MESMA do estado global.
Importante: ao trocar de visão a aba escolhida permanece; confirme que isso não quebra o gerente.

Como ainda não há páginas regionais por aba, o AreaCentral continua mostrando a PaginaRegional atual na visão regional (a troca vem na 8.7).

Validação: `npm test`, `npm run lint`, `npm run build`; suba `npm run dev` com a API e confirme visualmente que o gerente continua igual e a regional mostra o seletor e as três abas. Não faça commit. Mensagem sugerida: "Mostra barra lateral e abas na visão regional".

### Prompt 65
FATIA 8.6a — Aba Dados da regional (Etapa 8, frontend)

Leia apenas: frontend/src/pages/PaginaRegional.jsx e .css, components/AnotacoesRegional.jsx, utilitarios/visaoRegional.js.

Crie pages/PaginaDadosRegional.jsx e PaginaDadosRegional.css a partir do conteúdo de PaginaRegional (mesmas seções: cabeçalho da loja, resultado da loja por mês, acompanhamento dos feedbacks com a frase de esclarecimento), com estas diferenças:
- lê `estado.detalhesLoja` (status/dados/erro) em vez de `estado.regional`; carregando/erro/vazio com os componentes Estado*; "tentar de novo" chama selecionarLoja(lojaSelecionadaId);
- NÃO dispara o carregamento sozinha (quem carrega é a seleção da loja); sem useEffect de busca;
- NÃO mostra as anotações da regional (agora são a aba Anotações) e remove a seção correspondente;
- mantém as classes de tabela acessível (caption, th scope, container com tabIndex/role/aria-label) e o uso de seloDoAtingimento, tomDoAcompanhamento e formatadores, sem cálculo novo.
Copie o CSS necessário em vez de importar o da PaginaRegional (ela será removida na 8.7). Não altere PaginaRegional.jsx ainda e não ligue a página no AreaCentral nesta fatia.

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria aba Dados da regional".

### Prompt 66
FATIA 8.6b — Extrair o chat de anotações em componente reutilizável (Etapa 8, frontend)

Leia apenas: frontend/src/pages/PaginaAnotacoes.jsx e PaginaAnotacoes.css. REFATORAÇÃO SEM MUDAR COMPORTAMENTO nem aparência.

Crie components/ChatAnotacoes.jsx (+ ChatAnotacoes.css, movendo para ele os estilos do chat) com TUDO o que é apresentação do chat: título, área de mensagens com role="log", separador de dia (rotuloDoDia), balões, rolagem automática até o fim respeitando prefers-reduced-motion, formulário com textarea (Enter envia, Shift+Enter quebra linha, respeita composição IME), contador, botão Enviar e mensagem de erro com role="alert". Props: `titulo`, `nome` (para placeholder e vazio), `anotacoes` (lista { data, texto }), `aoEnviar(texto) => Promise<boolean>`, `enviando`, `erroEnvio`, `textoMaximo`, `rotuloAcessivel`, `idCampo` (para não repetir ids) e `children` opcional exibido depois do formulário. O rascunho (texto digitado) fica DENTRO do ChatAnotacoes e é limpo quando aoEnviar devolve true.
Refatore PaginaAnotacoes.jsx para usar o ChatAnotacoes, mantendo: estados carregando/erro/vazio, orientação, `<details>` das anotações do time (passe como children) e a chave por vendedor no AreaCentral. Os textos e classes visíveis ao usuário permanecem iguais; mova o CSS sem alterá-lo.

Validação: `npm test`, `npm run lint`, `npm run build`; confira visualmente, com a API rodando, que a aba Anotações do Diego continua idêntica (enviar anotação, rolagem, Esc/Enter). Descreva o que foi conferido. Não faça commit. Mensagem sugerida: "Extrai ChatAnotacoes da página de anotações".

### Prompt 67
FATIA 8.6c — Aba Anotações da regional em formato de chat (Etapa 8, frontend)

Pré-requisito: 8.6b. Leia apenas: frontend/src/components/ChatAnotacoes.jsx, pages/PaginaAnotacoes.jsx (como modelo de estados) e components/AnotacoesRegional.jsx.

Crie pages/PaginaAnotacoesRegional.jsx: lê estado.detalhesLoja e estado.novaAnotacaoRegional; carregando/erro/vazio como a PaginaAnotacoes; usa ChatAnotacoes com titulo "Anotações sobre a loja {loja_nome}", nome = gerente_nome (placeholder "Escreva uma observação sobre a loja e o Diego…" gerado a partir dos dados, sem nome fixo no código), anotacoes = detalhesLoja.dados.anotacoes_regional (ordenadas da mais antiga para a mais recente com ordenarDaMaisAntigaParaMaisRecente; o campo é "texto" e "data" como na API), aoEnviar = adicionarAnotacaoRegional(lojaSelecionadaId, texto), enviando = estado.novaAnotacaoRegional.status === CARREGANDO, erroEnvio = estado.novaAnotacaoRegional.erro, textoMaximo = ANOTACAO_TEXTO_MAXIMO e idCampo próprio. Orientação no topo: "Escreva aqui o que observar nas visitas à loja. As anotações ficam guardadas e entram no feedback para o gerente." Não mostrar a autora em cada balão (é sempre a regional); ela aparece no acessível do log. Não ligue ainda no AreaCentral.

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria aba Anotações da regional em formato de chat".

### Prompt 68
FATIA 8.6d — Aba Feedback da regional (Etapa 8, frontend)

Leia apenas: frontend/src/pages/PaginaFeedback.jsx e .css, components/VisualizadorRoteiro.jsx, ListaRoteirosPreparados.jsx e utilitarios/opcoesDePeriodo.js.

Crie pages/PaginaFeedbackRegional.jsx (+ CSS próprio, copiando o necessário de PaginaFeedback.css): espelha a PaginaFeedback do gerente, mas:
- dados de estado.detalhesLoja e do feedback de estado.feedbacksRegional[lojaSelecionadaId]; ação gerarFeedbackRegional(lojaId, { mesReferencia });
- seletor de período montado com montarOpcoesDePeriodo(detalhesLoja.dados.resultado_loja) (os itens têm mes e mes_parcial); mesmo padrão de período solicitado para "tentar de novo";
- título "Gerar feedback para o gerente" e textos que falem do gerente da loja (nome vindo de gerente_nome), nunca "colaborador";
- resultado com VisualizadorRoteiro (vendedorNome={gerente_nome}) e seção "Roteiros já preparados para o gerente" com ListaRoteirosPreparados (feedbacks_preparados);
- manter a frase "Roteiro preparado não significa feedback realizado: é só o rascunho gerado pela IA.";
- aria-live no resultado e botão desabilitado enquanto gera, como no original.
Se o VisualizadorRoteiro ou a Lista tiverem texto fixo que só faça sentido para vendedor, parametrize com prop opcional (padrão = texto atual) sem mudar a aparência do gerente. Não ligue ainda no AreaCentral.

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Cria aba Feedback da regional".

### Prompt 69
FATIA 8.7 — Ligar as abas da regional e aposentar a página antiga (Etapa 8, frontend)

Pré-requisitos: 8.5b, 8.6a, 8.6c e 8.6d. Leia apenas: frontend/src/components/AreaCentral.jsx, App.jsx e a lista de arquivos de pages/ e components/.

1. AreaCentral.jsx: a visão regional passa a ter o MESMO esqueleto do gerente: sem loja selecionada, EstadoVazio "Escolha uma loja"; com loja, o tabpanel (role, id ID_PAINEL_ABAS, aria-labelledby "aba-{aba}", tabIndex 0) com PaginaFeedbackRegional, PaginaAnotacoesRegional ou PaginaDadosRegional conforme estado.aba, com `key={lojaSelecionadaId}` nas duas primeiras (o rascunho não vaza entre lojas). aria-label do main: "Conteúdo da loja".
2. Remova o que ficou sem uso: pages/PaginaRegional.jsx e .css, components/AnotacoesRegional.jsx e .css, e, no provider e no reducer, `carregarRegional`, o estado `regional`, os tipos REGIONAL_* e os testes correspondentes — SOMENTE depois de provar com `grep` que nada mais os referencia. Mantenha o serviço obterDesempenhoGerente (a API antiga continua existindo). Liste o que foi removido.
3. Ao abrir a visão regional pela primeira vez a loja L004 deve estar selecionada e a aba Feedback ativa (padrão do estado).

Validação: `npm test`, `npm run lint`, `npm run build`. Não faça commit. Mensagem sugerida: "Liga as abas da regional e remove a página antiga".

### Prompt 70
FATIA 8.8 — Validação final da Etapa 8 (não crie nem altere código, só valide e relate)

Leia apenas: backend/api.http (para os exemplos) e COMO-RODAR.md.

Execute de verdade e mostre as saídas:
1. Backend: suíte completa de unittest. Frontend: `npm test`, `npm run lint`, `npm run build`.
2. Suba backend (porta 8000) e frontend (porta 5173). Por curl, confirme: GET /api/regional/lojas, GET /api/regional/lojas/L004/historico e o 404 de L999.
3. Roteiro manual descrito passo a passo (marque cada item como OK/FALHOU com o que viu): trocar para a visão da Patrícia; seletor mostra Aurora Shopping Centro / Diego Furtado e a seta abre o aviso de que não há outras lojas; as 3 abas aparecem e o teclado (setas) navega entre elas; Dados mostra resultado mês a mês e acompanhamento; Anotações mostra as 5 anotações do CSV em balões por dia; enviar uma anotação nova a adiciona ao fim e ela sobrevive a recarregar a página; Feedback com a API em modo fake/sem chave mostra erro amigável e permite tentar de novo; voltar para o Diego e confirmar que as abas dele continuam iguais.
4. NÃO chame a IA real; se a chave não estiver configurada, relate o erro amigável exibido. A geração real eu testo.
5. Apague o arquivo backend/data/anotacoes_regional_novas.json criado pelos testes manuais e confirme com `git status --short` que só há arquivos de código e testes (nenhum JSON de dados de execução).

Diga claramente se a Etapa 8 está concluída ("pronta quando: a Patrícia escolhe a loja, vê Dados, conversa nas Anotações e gera um roteiro de feedback para o gerente, sem afetar a visão do Diego") e liste pendências reais. Lembre-me de registrar no DIARIO.md o que decidi e aprendi, sem escrever por mim. Mensagem de commit sugerida: "Conclui Etapa 8: espaço da regional por loja".


## 2026-11-13

### Prompt 1
CONTEXTO (somente leitura). NÃO modifique, crie, apague ou renomeie nenhum arquivo e não execute comandos que alterem o repositório ou o sistema (nada de npm install, git add/commit/checkout).

Projeto: a plataforma agora se chama **Return.Ai** (antes "Feedback Inteligente"). Etapas 0 a 8 prontas: o Diego (gerente) tem as abas Feedback, Anotações (chat) e Dados por vendedor; a Patrícia (regional) tem as mesmas abas por loja. Estamos na ETAPA 9: trocar SOMENTE a aparência para o novo `frontend/DESIGN.md` (já copiado por mim no projeto, substituindo o antigo). Hoje o visual é cartões CLAROS sobre página ROXA; o novo é página ESCURA com cartões escuros, verde e roxo como únicos destaques.

REGRA DE OURO DA ETAPA: nada da estrutura, da lógica ou dos fluxos muda. Tudo deve continuar funcionando exatamente igual.
- PODE mudar: arquivos .css; tokens; fontes; imagens/ícones (assets); no index.html só título, favicon e fonte; e nos .jsx SOMENTE acrescentar/trocar `className`, trocar o ícone decorativo e (no cabeçalho) trocar o texto do produto pela imagem da logo.
- NÃO PODE mudar: lógica, estado, reducer, services, utilitarios, props, handlers, hooks, ids, atributos aria-*, ordem dos elementos no DOM, textos visíveis ao usuário (exceto o nome do produto), rotas/endpoints, backend e testes de lógica. `npm test` deve passar SEM alterar nenhum teste.
- Se algo do DESIGN.md exigir mudar estrutura/texto/comportamento, NÃO faça: registre no relatório da fatia como "divergência" e siga adiante.

Leia SOMENTE: frontend/DESIGN.md (inteiro, é a fonte da verdade), frontend/src/estilos/tokens.css, estilos/base.css, App.css, index.html, a lista `find frontend/src -name '*.css' -o -name '*.jsx'` e, para cada fatia, só os arquivos que ela citar. A imagem de referência da tela Feedback (Diego) está em frontend/src/assets/referencia-feedback.png se eu a tiver copiado; se não estiver, use o DESIGN.md.

Responda em no máximo 14 linhas: (1) quais arquivos CSS/JSX existem hoje na Etapa 8 e quais ainda usam as cores claras/roxas; (2) quais classes do JSX atual correspondem a cada componente do DESIGN.md (barra lateral, item ativo, cartão do vendedor, botão primário, campos, cartão de conteúdo); (3) dúvidas. Sem código.

Decisões já tomadas (valem para TODAS as fatias):
1. Tokens em português, como o projeto já faz. Novos nomes: --cor-fundo #16151A, --cor-cartao #222029, --cor-linha #2E2C36, --cor-borda #4A4757, --cor-tinta #F2F0EA, --cor-texto #E2DFEA, --cor-texto-suave #BDBAC8, --cor-verde #3DDC97, --cor-sobre-verde #0B2E1F, --cor-roxo #A66BF2. Texto sobre o roxo sólido usa o tom do fundo (#16151A, contraste 5,2:1), nunca branco (3,5:1 reprova).
2. As cores antigas (--cor-primaria, --cor-superficie-suave, --cor-fundo-escuro, --cor-texto-sobre-fundo, --cor-texto-sobre-primaria, --cor-borda-controle, --cor-perigo-*, etc.) viram APELIDOS temporários dos tokens novos (fatia 9.2) para o app nunca quebrar no meio do caminho; a fatia 9.12 remove os apelidos depois de provar com grep que ninguém mais os usa.
3. Fonte Inter (400, 600, 700, 800) carregada por <link> do Google Fonts no index.html, com `sans-serif` de reserva, como diz o DESIGN.md. Sem dependência nova no package.json.
4. O DESIGN.md só tem verde e roxo. NÃO invente vermelho/amarelo: erro e alerta usam cartão com barra roxa, ícone e título (cor nunca é o único sinal).
5. O DESIGN.md pede que a tela de feedback mostre só o texto gerado. Os textos que o app já tem hoje (orientações, a frase "Roteiro preparado não significa feedback realizado" etc.) NÃO são removidos: ficam como "nota de apoio" discreta (14 px, --cor-texto-suave) e vão para a lista de divergências do relatório final para eu decidir.
6. Barra lateral começa recolhida em telas estreitas: isso já existe no código (matchMedia). Não mexa; só estilize os dois estados.
7. Sem imagens remotas, sem novas bibliotecas, sem alterar ícones além de tamanho/traço (lucide-react: 24 px, traço de 2 px).

Regras para TODOS os prompts seguintes:
- Mudanças pequenas e coesas, só no que a fatia pede. NÃO faça git commit/add/push/amend/reset (eu faço os commits). Nunca coloque segredos em arquivos versionados.
- Comandos de shell simples, um por vez. Se a sessão for interrompida, na retomada rode `git status --short` e só refaça o que faltar.
- COMENTÁRIOS OBRIGATÓRIOS E DIDÁTICOS em todo CSS/JSX tocado: português simples; cabeçalho de 2 a 4 linhas no arquivo explicando o papel dele no novo visual; comentário de bloco antes de cada grupo de regras explicando o PORQUÊ (de onde vem o valor no DESIGN.md); cada contraste citado com a razão REAL (calcule, não copie de memória); remova ou atualize comentários antigos que falem de "cartão claro" ou "fundo roxo". Não altere comentários de lógica.
- Todo valor de cor, fonte, tamanho de texto, raio e espaço usa token (var(--...)); proibido hex solto fora de tokens.css.
- Acessibilidade (DESIGN.md seção 8): foco visível de 3 px em --cor-verde com `outline-offset`, alvos de toque de pelo menos 44 px, texto mínimo 14 px (notas) e 17 px (corpo), `prefers-reduced-motion` respeitado (já existe; mantenha).
- Validação de cada fatia (de dentro de frontend/): `npm test`, `npm run lint`, `npm run build` com a saída REAL; e `git diff --name-only | grep -v -E '\.(css|md|png|svg|html)$'` — só podem aparecer os .jsx que a própria fatia autorizou. Não declare nada validado sem ter executado.
- Ao final de cada fatia informe: arquivos alterados, o que ficou diferente do DESIGN.md (divergências) e o resultado REAL dos comandos.

Aguarde o primeiro prompt de implementação.

### Prompt 2
FATIA 9.1 — Assets, nome no navegador, fonte e DESIGN.md (Etapa 9, frontend)

Antes: eu copiei `return-ai-logo.png` para frontend/src/assets/ e `favicon.png` para frontend/public/, e o novo DESIGN.md para frontend/DESIGN.md. Leia apenas: frontend/index.html, frontend/DESIGN.md (só a primeira linha e a seção 3 Tipografia), frontend/public/ (lista) e `grep -rn favicon frontend/src frontend/index.html`.

1. Confirme com `ls` que os dois arquivos existem e que o DESIGN.md começa com "# DESIGN.md — Return.Ai". Se algum faltar, PARE e me avise.
2. index.html: `<title>Return.Ai</title>`; favicon `<link rel="icon" type="image/png" href="/favicon.png" />`; adicione `<link rel="preconnect" href="https://fonts.googleapis.com">`, `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` e o `<link>` do Google Fonts da Inter com os pesos 400;600;700;800 e `display=swap`. Comente em HTML por que a fonte vem de fora e que, sem internet, o navegador usa a fonte de reserva.
3. Remova frontend/public/favicon.svg SOMENTE se `grep` provar que nada mais o referencia.
4. Não toque em nenhum .jsx, .css ou .js nesta fatia.

Validação: `npm run build`; confira no `dist/index.html` o título e o favicon. Não faça commit. Mensagem sugerida: "Adiciona logo, favicon, fonte Inter e título Return.Ai".

### Prompt 3
FATIA 9.2 — Tokens do novo design (Etapa 9, frontend)

Leia apenas: frontend/src/estilos/tokens.css e frontend/DESIGN.md (seções 2, 3, 4 e 5). Reescreva SOMENTE tokens.css.

1. Cores novas (decisão 1 do contexto), cada uma com comentário de uso tirado da tabela do DESIGN.md. Foco: `--cor-foco: var(--cor-verde)`. `--cor-sobre-roxo: var(--cor-fundo)`.
2. Tipografia: `--fonte-familia: 'Inter', sans-serif`; tamanhos `--texto-titulo-pagina: 40px`, `--texto-titulo-bloco: 22px`, `--texto-item: 17px`, `--texto-corpo: 17px`, `--texto-rotulo: 15px`, `--texto-nota: 14px`; pesos `--peso-regular: 400`, `--peso-semi: 600`, `--peso-forte: 700`, `--peso-extra: 800`; entrelinha do corpo `--entrelinha-corpo: 1.5`.
3. Raios: `--raio-campo: 12px`, `--raio-item: 14px`, `--raio-cartao: 18px`, `--raio-full: 9999px`. Layout: `--altura-cabecalho: 84px`, `--largura-lateral: 260px`, `--largura-lateral-recolhida: 88px`, `--largura-conteudo: 1160px`, `--altura-controle: 52px`, `--alvo-toque-minimo: 44px`, espaçamentos do DESIGN (12px entre itens, 24px entre blocos, padding do conteúdo 40px 48px, padding do cartão 26px 28px).
4. CAMADA DE COMPATIBILIDADE no fim do arquivo, com comentário "TEMPORÁRIA — removida na fatia 9.12": mantenha TODOS os nomes antigos ainda usados no projeto (confira com `grep -rhoE 'var\(--[a-z0-9-]+' frontend/src --include=*.css | sort -u`) apontando para os tokens novos equivalentes (ex.: --cor-primaria → var(--cor-verde); --cor-superficie-suave → var(--cor-cartao); --cor-fundo-escuro → var(--cor-fundo); --cor-texto-sobre-fundo → var(--cor-tinta); --cor-texto-sobre-primaria → var(--cor-sobre-verde); --cor-borda-controle → var(--cor-borda); --cor-perigo-fundo → var(--cor-cartao); --cor-perigo-borda → var(--cor-roxo)). Antigos de tamanho/espaço/raio continuam com valor atual se não houver equivalente. Nenhum nome usado pode ficar indefinido.
5. Substitua o bloco final de "combinações de contraste" por uma tabela de comentário com as razões REAIS calculadas por você (tinta/fundo, texto/cartão, texto-suave/cartão, verde/fundo, sobre-verde/verde, roxo/cartão, roxo/fundo, borda/fundo). Avise nesse comentário que a borda de campo #4A4757 tem cerca de 2:1 sobre o fundo (abaixo dos 3:1 que a WCAG pede para limites de controle) e que seguimos o DESIGN.md, ficando registrado como divergência para eu decidir.

Validação: `npm test`, `npm run lint`, `npm run build`. Rode `npm run dev` e confirme que o app abre ESCURO sem texto invisível (mesmo que ainda feio). Não faça commit. Mensagem sugerida: "Troca tokens pelo novo design Return.Ai".

### Prompt 4
FATIA 9.3 — Base global: corpo, títulos, foco e utilitários (Etapa 9, frontend)

Leia apenas: frontend/src/estilos/base.css, App.css e DESIGN.md (seções 3, 4, 5 "Botão primário" e "Campos", 8). Altere SOMENTE base.css e App.css.

1. `body`: fundo --cor-fundo, texto --cor-tinta, fonte/tamanho/entrelinha do corpo novos. Títulos: h1/h2/h3 só ajustam peso e tamanho por token; NÃO force 40 px em todo h2 (h2 é usado em várias seções): o 40/800 do título da aba será aplicado por CLASSE nas fatias de cada página. Mantenha margem 0 e herança de cor.
2. Foco visível global: `:focus-visible { outline: 3px solid var(--cor-foco); outline-offset: 2px; }` (revise o que já existe).
3. Utilitários "ui-" existentes (botão primário, secundário, campos, visualmente oculto, etc.): reescreva para o DESIGN. Botão primário: fundo --cor-verde, texto --cor-sobre-verde, altura 52 px, raio 12 px, peso 700, sem borda, hover levemente mais claro SEM cor nova (use `filter: brightness(1.08)`), desabilitado com opacidade reduzida + `cursor: not-allowed`. Botão secundário: fundo --cor-cartao, texto --cor-tinta, raio 12 px. Campos (select/textarea/input): select com fundo --cor-cartao e textarea com --cor-fundo, borda 1 px --cor-borda, raio 12 px, altura mínima 52 px, texto 17 px; `label` visível 15 px peso 600 em --cor-texto-suave. Mantenha os NOMES de classe existentes; só mude o que elas fazem.
4. App.css: `.app` com fundo --cor-fundo; `.app__corpo` sem mudar o comportamento flex; sem tocar em quebras de layout ainda.
Não altere nenhum .jsx.

Validação: `npm test`, `npm run lint`, `npm run build`; confira no navegador que botões e campos já aparecem escuros/verdes. Não faça commit. Mensagem sugerida: "Aplica base global do novo design".

### Prompt 5
FATIA 9.4 — Cabeçalho com a logo e menu do usuário (Etapa 9, frontend)

Leia apenas: frontend/src/components/Cabecalho.jsx e .css, MenuUsuario.jsx e .css, DESIGN.md (seção 4 "Cabeçalho" e 5 "Logo"), e a imagem de referência (topo: logo à esquerda; "Diego / Gerente" com círculo roxo "D" à direita).

Autorizado mexer em Cabecalho.jsx SOMENTE para trocar o conteúdo do bloco de identidade: dentro do `<h1 className="cabecalho__titulo">` coloque `<img src={logo} alt="Return.Ai" className="cabecalho__logo" />` (import da imagem de src/assets/return-ai-logo.png) e REMOVA o subtítulo "Assistente de IA para feedback" do visual, preservando o texto para leitor de tela com a classe de "visualmente oculto" já existente. Mantenha o h1 (a estrutura de títulos não muda) e a área do MenuUsuario intactos. MenuUsuario.jsx NÃO muda.

CSS:
- Cabeçalho: altura 84 px (`--altura-cabecalho`), fundo --cor-fundo, divisória inferior 1 px --cor-linha, padding horizontal igual ao da lateral, itens alinhados ao centro, logo com altura 56 px e largura automática (`height: 56px; width: auto`), sem caixa ao redor.
- MenuUsuario: avatar redondo (40 px) fundo --cor-roxo com a inicial em --cor-sobre-roxo, peso 700; nome em --cor-tinta peso 700 e cargo em --cor-texto-suave 14 px, alinhados à direita do texto como na referência (nome em cima, cargo embaixo, à esquerda do avatar). Botão da seta com alvo de 44 px e ícone de 20 px. Painel de troca de usuário: fundo --cor-cartao, borda 1 px --cor-linha, raio 14 px, sombra discreta SEM cor nova (`rgba` preto apenas se já existir token; senão sem sombra), opções com altura de 52 px e hover/foco em --cor-fundo.
Nenhuma regra antiga de cor clara/roxa pode sobrar nesses dois CSS.

Validação: `npm test`, `npm run lint`, `npm run build`; no navegador confirme que trocar de Diego para Patrícia pelo menu continua funcionando e que a logo aparece sem caixa. Não faça commit. Mensagem sugerida: "Aplica logo Return.Ai e novo visual do cabeçalho".

### Prompt 6
FATIA 9.5 — Barra lateral e navegação por abas (Etapa 9, frontend)

Leia apenas: frontend/src/components/BarraLateral.jsx e .css, NavegacaoAbas.jsx e .css, DESIGN.md (seção 5 "Barra lateral") e a referência (botão de recolher no topo ocupando a largura; itens Feedback/Anotações/Dados; cartão da pessoa logo abaixo dos itens). Não altere nenhum .jsx nesta fatia (se faltar uma classe, me avise).

BarraLateral.css: largura 260 px expandida e 88 px recolhida (tokens), divisória direita 1 px --cor-linha, fundo --cor-fundo, padding e espaçamento de 12 px entre itens. Botão de recolher/expandir: largura total, altura 52 px, fundo --cor-cartao, borda 1 px --cor-borda, raio 14 px, ícone de painel centralizado (24 px, traço 2 px), hover com borda --cor-verde. Recolhida: só ícones e avatar, tudo centralizado e sem corte de foco.
NavegacaoAbas.css: itens de 52 px de altura, raio 14 px, espaço de 12 px. Inativo: fundo --cor-cartao, texto --cor-tinta, peso 600. Ativo: fundo --cor-verde, texto --cor-sobre-verde, peso 700 (o ativo continua sinalizado por `aria-selected`, então o CSS deve usar o seletor de atributo/classe que já existe). Ícone 24 px, traço 2 px, com 12 px até o rótulo; recolhida mostra só o ícone centralizado (o `aria-label` já existe no JSX). Foco: contorno de 3 px --cor-verde (no item ativo use `outline-offset` positivo para o contorno aparecer sobre o verde com contraste: ele deve ser visível; se não for, use contorno --cor-tinta e registre).
Remova das duas folhas qualquer regra do visual antigo (borda escura, fundo claro, roxo).

Validação: `npm test`, `npm run lint`, `npm run build`; no navegador teste recolher/expandir e navegar pelas abas com teclado (setas, Home, End) — nada pode ter mudado no comportamento. Não faça commit. Mensagem sugerida: "Aplica novo visual à barra lateral e às abas".

### Prompt 7
FATIA 9.6 — Cartão da pessoa e da loja na lateral (Etapa 9, frontend)

Leia apenas: frontend/src/components/SeletorColaborador.jsx e .css, SeletorLoja.jsx e .css (se existir), DESIGN.md (seção 5: "Cartão do vendedor selecionado..."). Não altere nenhum .jsx.

Aplique o mesmo visual aos DOIS seletores (e use classes/regras iguais onde forem equivalentes, copiando em vez de importar CSS de outro componente):
- Cartão: fundo --cor-cartao, raio 14 px, borda superior de 4 px em --cor-roxo, padding confortável; nome em --cor-tinta peso 700 e função/gerente em --cor-texto-suave 14 px.
- Avatar redondo de 44 px (ou o tamanho atual, se maior) em --cor-verde com iniciais em --cor-sobre-verde, peso 800.
- Botão da seta: alvo mínimo de 44 px, ícone 20 px, sem fundo; hover/foco com contorno verde.
- Lista aberta (outros vendedores / outras lojas): fundo --cor-cartao, linhas de 52 px, item atual destacado só por texto/ícone (nunca só por cor), hover --cor-fundo; aviso de lista vazia em --cor-texto-suave, 14 px, com o mesmo padding.
- Recolhida: só o avatar centralizado, mantendo a borda roxa de 4 px.
- Remova qualquer regra do visual antigo (fundo claro, borda escura, roxo antigo, verde-menta antigo).

Validação: `npm test`, `npm run lint`, `npm run build`; no navegador, como Diego: expandir a lista do seletor e trocar de vendedor; como Patrícia: abrir a seta do seletor de loja e ver o aviso. Recolha a barra e confirme que o avatar fica centralizado. Não faça commit. Mensagem sugerida: "Aplica novo visual aos seletores de vendedor e de loja".

### Prompt 8
FATIA 9.7 — Aba Feedback do gerente (Etapa 9, frontend)

Leia apenas: frontend/src/pages/PaginaFeedback.jsx e .css, components/VisualizadorRoteiro.jsx e .css, ListaRoteirosPreparados.jsx e .css, a referência (tela completa) e DESIGN.md (seção 6).

Autorizado em .jsx SOMENTE: acrescentar uma classe-modificadora ao `className` de cada um dos 4 cartões do VisualizadorRoteiro (ex.: `visualizador__cartao--positivos`, `--melhorias`, `--motivos`, `--roteiro`) se hoje não existirem, e uma classe de variação ao título principal da página (ex.: `pagina-feedback__titulo--principal`) para diferenciar do título "Roteiros já preparados". Nenhuma outra mudança em JSX.

CSS (reproduza a referência):
- Título principal da aba: 40 px, peso 800, cor --cor-tinta. Título da seção "Roteiros já preparados": 22 px, peso 700.
- Linha Período + botão: rótulo "Período" 15 px/600 em --cor-texto-suave acima do select; select (--cor-cartao, borda --cor-borda, raio 12, altura 52) e botão primário lado a lado, com 16 px de espaço; em tela estreita empilham.
- Quatro cartões, na ordem atual, com fundo --cor-cartao, raio 18 px, padding 26 px 28 px, barra esquerda de 6 px (borda ou pseudo-elemento) nas cores: Pontos positivos = verde; Pontos de melhoria = roxo; Possíveis motivos = roxo; Roteiro de conversa sugerido = verde. Espaço de 24 px entre cartões.
- Título do cartão: ícone dentro de círculo de 36 px (fundo --cor-fundo, ícone na cor do cartão, traço 2 px) + título 22 px/700. Listas com 12 px entre itens, texto 17 px, entrelinha 1,5, cor --cor-texto; lista numerada do roteiro com os números visíveis. Nota "São hipóteses para investigar na conversa, não conclusões.": 14 px, --cor-texto-suave, logo abaixo do título do cartão.
- Textos extras que o app já mostra (orientações, data de geração, frase "Roteiro preparado não significa feedback realizado" etc.): MANTENHA e estilize como nota de apoio (14 px, --cor-texto-suave, sem moldura). Anote cada um deles na lista de divergências.
- ListaRoteirosPreparados: itens recolhíveis com fundo --cor-cartao, raio 14 px, borda esquerda de 4 px --cor-roxo, botão de expandir com alvo de 44 px; conteúdo expandido reaproveita o visual dos 4 cartões, sem duplicar CSS desnecessário (reaproveite as classes do Visualizador).
- Estados de erro ao gerar e de "gerando": veja a fatia 9.11; aqui apenas não deixe regra antiga clara.

Validação: `npm test`, `npm run lint`, `npm run build`; com a API rodando, gere um feedback (ou, sem chave da IA, confira só os estados) e compare lado a lado com a referência: título, linha Período, barras e cores dos cartões, círculos de ícone, espaçamentos. Descreva as diferenças. Não faça commit. Mensagem sugerida: "Aplica novo visual à aba Feedback".

### Prompt 9
FATIA 9.8 — Aba Anotações em formato de chat (Etapa 9, frontend)

Leia apenas: frontend/src/pages/PaginaAnotacoes.jsx e .css, components/ChatAnotacoes.jsx e .css (se existir), DESIGN.md (seção 7 e 5 "Campos") e a lista de classes usadas no chat.

O DESIGN.md descreve uma tela mais simples (cartão "Nova anotação" + lista), mas o projeto usa CHAT desde a Etapa 3: mantenha o chat e apenas traduza o visual (divergência a registrar). Autorizado em .jsx: só `className`.
- Título da aba: 40 px/800, como na 9.7. Orientação no topo como nota de apoio (14 px, --cor-texto-suave).
- Área de mensagens: fundo --cor-fundo, rolagem sem barra clara (use cores de tokens com `scrollbar-color` se já houver), separador de dia com linha --cor-linha e o rótulo em --cor-texto-suave 14 px.
- Balões: fundo --cor-cartao, raio 18 px, barra lateral esquerda de 6 px alternando conforme o DESIGN ("verde ou roxo": use roxo para as anotações do próprio usuário e verde para recém-enviadas, se hoje existir essa distinção; se não existir, use roxo em todas e me avise), texto 17 px --cor-texto, data/hora 14 px --cor-texto-suave.
- Campo de escrita: cartão com borda superior de 4 px --cor-verde, textarea (fundo --cor-fundo, borda --cor-borda, raio 12, mín. 52 px, 17 px), contador de caracteres 14 px, botão Enviar como botão primário com ícone (Send) de 20 px, mensagem de erro com o visual de erro da 9.11.
- Mantenha o `<details>` das anotações do time (se existir) como cartão recolhível no mesmo estilo.
- Remova qualquer cor/fundo claro antigo.

Validação: `npm test`, `npm run lint`, `npm run build`; no navegador envie uma anotação, veja a rolagem automática e teste Enter / Shift+Enter. Não faça commit. Mensagem sugerida: "Aplica novo visual à aba Anotações".

### Prompt 10
FATIA 9.9 — Aba Dados (Etapa 9, frontend)

Leia apenas: frontend/src/pages/PaginaDados.jsx e .css, components/CartaoIndicador.jsx e .css, Selo.jsx e .css, DESIGN.md ("Cartão de conteúdo", seção 2 "Regras") e `ls frontend/src/pages`. O DESIGN.md não descreve a tela Dados em detalhe ("serve de base para as demais"): derive dos mesmos componentes. Autorizado em .jsx: só `className`.
- Título 40/800; títulos de seção ("Indicadores", "Totais", "Mês a mês" ou equivalentes) 22/700.
- CartaoIndicador: fundo --cor-cartao, raio 18, padding 26x28, barra esquerda de 6 px (verde para o que vai bem, roxo para atenção — use a classe/tom que o componente já recebe; sem tom, verde), valor grande 28 px peso 800 em --cor-tinta, rótulo 15 px/600 em --cor-texto-suave, nota 14 px.
- Selo: pílula (--raio-full) com borda 1 px na cor do tom (verde ou roxo), fundo --cor-fundo, texto em --cor-tinta e SEMPRE com ícone ou texto que diga o significado (cor nunca é o único sinal); alvo não precisa de 44 px por não ser clicável.
- Tabelas: container com fundo --cor-cartao, raio 18 px, `overflow-x: auto` (mantenha o foco por teclado que já existe, com contorno verde); cabeçalho em --cor-texto-suave 14 px/600 maiúsculas apenas se já for assim; linhas separadas por --cor-linha; números alinhados à direita com `font-variant-numeric: tabular-nums`; célula do mês parcial com a marca textual já existente.
- Remova qualquer regra clara/roxa antiga.

Validação: `npm test`, `npm run lint`, `npm run build`; no navegador, como Diego: aba Dados de um vendedor e confira indicadores, selos e tabela com rolagem horizontal em janela estreita. Não faça commit. Mensagem sugerida: "Aplica novo visual à aba Dados".

### Prompt 11
FATIA 9.10 — Visão da regional nas três abas (Etapa 9, frontend)

Leia apenas: pages/PaginaDadosRegional.jsx/.css, PaginaAnotacoesRegional.jsx, PaginaFeedbackRegional.jsx/.css (confirme com `ls` os nomes reais), components/AreaCentral.jsx/.css e, se ainda existirem, PaginaRegional.css e AnotacoesRegional.css. Autorizado em .jsx: só `className`.

1. Reaproveite: as abas Feedback e Anotações da regional devem ficar IDÊNTICAS às do gerente (mesmas classes/tokens). Se elas já usam os componentes/CSS da 9.7 e 9.8, apenas confirme e corrija o que sobrar; se tiverem CSS próprio, converta usando as mesmas regras (copie, não importe CSS de outra página).
2. A aba Dados da regional segue a 9.9 (cartões, selos, tabelas). O bloco "acompanhamento dos feedbacks" (cobertura e tabela por vendedor) usa cartão com barra roxa quando houver atenção (cobertura baixa) e verde quando estiver bem, sempre com o texto explicando.
3. AreaCentral.css: largura máxima do conteúdo 1160 px (`--largura-conteudo`), padding 40 px 48 px, espaço de 24 px entre blocos, fundo --cor-fundo, painel de abas sem moldura clara; mesma regra para gerente e regional.
4. Se PaginaRegional.css/AnotacoesRegional.css ainda existirem e não forem usados, NÃO os apague aqui: liste-os para a fatia 9.12.

Validação: `npm test`, `npm run lint`, `npm run build`; no navegador, como Patrícia: as três abas, o seletor de loja e a troca de volta para o Diego. Compare as abas Feedback das duas visões lado a lado: devem parecer a mesma tela. Não faça commit. Mensagem sugerida: "Aplica novo visual à visão da regional".

### Prompt 12
FATIA 9.11 — Estados (carregando, vazio, erro) e rodapé (Etapa 9, frontend)

Leia apenas: components/EstadoCarregando.jsx/.css, EstadoVazio.jsx/.css, EstadoErro.jsx/.css, Rodape.jsx/.css e DESIGN.md (seções 1, 2 "Regras" e 8). Autorizado em .jsx: só `className`.
- Os três estados: cartão --cor-cartao, raio 18, padding 26x28, centralizados no espaço da página, texto 17 px. Carregando: barra esquerda verde, indicador animado com tokens, respeitando `prefers-reduced-motion` (sem animação nesse caso, só o texto). Vazio: barra esquerda roxa, ícone/título conforme o JSX. Erro: decisão 4 do contexto — barra esquerda roxa de 6 px, ícone CircleAlert em --cor-roxo, título e mensagem em --cor-tinta, botão "Tentar de novo" como botão primário. NÃO use vermelho.
- Rodapé: continua existindo e com o mesmo texto/link. Fundo --cor-fundo, divisória superior 1 px --cor-linha, texto 14 px --cor-texto-suave, link em --cor-verde sublinhado ao foco/hover, alvo de toque de 44 px no link. Ele não deve competir com o conteúdo nem aparecer sobre a barra lateral (a lateral continua até o fim da página, como na referência; se hoje o rodapé ocupa a largura toda, mantenha, mas me diga como ficou).
- Mensagens de erro inline (formulários, geração, anotações) com `role="alert"` seguem o mesmo visual do EstadoErro, em tamanho compacto.

Validação: `npm test`, `npm run lint`, `npm run build`; para ver os estados, desligue o backend e recarregue (erro), troque para um vendedor sem dados (vazio) e olhe o carregamento com a rede lenta do DevTools. Não faça commit. Mensagem sugerida: "Aplica novo visual aos estados e ao rodapé".

### Prompt 13
FATIA 9.12 — Limpeza: apelidos antigos, CSS morto e comentários (Etapa 9, frontend)

Leia apenas: estilos/tokens.css (camada de compatibilidade), a saída dos greps abaixo e os CSS citados por eles.

1. Prove com `grep -rhoE 'var\(--[a-z0-9-]+' frontend/src --include=*.css | sort | uniq -c` quais tokens ainda são usados. Para cada apelido da camada de compatibilidade da 9.2 que NINGUÉM usa mais, remova-o. Se ainda houver uso, ABRA o arquivo, troque pelo token novo correto e só então remova. A camada inteira deve sumir.
2. `grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsl' frontend/src --include=*.css --include=*.jsx` fora de tokens.css deve voltar vazio, exceto dentro de comentários de contraste (que devem citar a razão real). Corrija o que sobrar.
3. `grep -rniE 'roxo da marca|fundo roxo|cartão claro|superfície clara|F5EFFB|8328D9|00E6B8|1E1E24|Space Grotesk' frontend/src frontend/README.md` — atualize/remova todo comentário desatualizado. Em frontend/README.md só mexa em frases sobre aparência/cores/fonte, se existirem.
4. CSS morto: liste arquivos .css cujos componentes não existem mais (ex.: PaginaRegional.css, AnotacoesRegional.css) e apague SOMENTE os que `grep` provar que nenhum .jsx importa.
5. Verifique que o foco visível aparece em: botão de recolher, abas, seletores, select, textarea, botões e links do rodapé.

Validação: `npm test`, `npm run lint`, `npm run build` com saída real. Não faça commit. Mensagem sugerida: "Remove apelidos antigos e CSS morto do visual anterior".

### Prompt 14
FATIA 9.13 — Nome Return.Ai nos textos que não são tela (Etapa 9)

Esta fatia é só de NOMES em texto. Leia apenas: `grep -rn -i "feedback inteligente" . --include=*.py --include=*.md --include=*.http --include=*.json --include=*.jsx --include=*.js --include=*.html --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=prompts` e frontend/package.json.
- Troque "FullStore Feedback Inteligente" / "Feedback Inteligente" por "Return.Ai" em: backend/main.py (docstring e `title=` do FastAPI, que aparece em /docs), backend/domain/excecoes.py (docstring), backend/api.http (comentário do topo), COMO-RODAR.md (as 2 linhas que citam o nome; a linha que descreve o cabeçalho deve passar a dizer que o cabeçalho mostra a logo Return.Ai) e qualquer outra ocorrência do resultado do grep.
- NÃO renomeie pastas, o repositório, o `name` do package.json nem pacotes Python. NÃO altere lógica, rotas, nomes de classes/funções nem variáveis. NÃO mexa em README.md, BRIEFING.md, DIARIO.md, AGENTS.md, CLAUDE.md nem em prompts/ (histórico).
- Confirme com `grep -rn "title=" backend/tests` que nenhum teste depende do título antigo.

Validação: suíte completa do backend (de dentro de backend/: `python -m unittest discover -s tests -t .`), `npm test`, `npm run build`; suba o backend e confirme em /docs o novo título. Não faça commit. Mensagem sugerida: "Atualiza o nome do produto para Return.Ai nos textos".

### Prompt 15
FATIA 9.14 — Validação final da Etapa 9 (não altere código; só valide e relate)

Leia apenas: frontend/DESIGN.md e a imagem de referência.

1. Execute de verdade e mostre as saídas: backend (suíte de unittest), frontend (`npm test`, `npm run lint`, `npm run build`).
2. PROVA DE QUE NADA ESTRUTURAL MUDOU: `git diff --name-only <commit da Etapa 8>..HEAD` agrupado por tipo. Em arquivos .js/.py só podem aparecer main.py/excecoes.py (docstring/title) e NENHUM outro .js; em .jsx só os autorizados (Cabecalho.jsx, className nos componentes das fatias 9.7 a 9.11). Mostre `git diff` dos .jsx e confirme linha a linha que só há className, import de imagem e troca de h1. Se aparecer qualquer outra mudança, aponte.
3. Roteiro visual (marque OK/FALHOU com o que viu): cabeçalho com logo e "Diego / Gerente" com círculo roxo; fundo #16151A; lateral 260/88 px, botão de recolher, abas com ativo verde; cartão do vendedor com borda roxa; Feedback igual à referência (título 40 px, Período, botão verde, 4 cartões com barras verde/roxo/roxo/verde, nota das hipóteses, lista numerada); Anotações em chat; Dados com cartões, selos e tabela; visão da Patrícia com seletor de loja e as mesmas três abas; estados de carregando/vazio/erro; foco por teclado; janela estreita (lateral recolhida, blocos empilhados); título da aba do navegador "Return.Ai" com o favicon novo.
4. Acessibilidade: calcule e liste os contrastes REAIS de todos os pares texto/fundo usados (inclusive verde sobre cartão, roxo sobre cartão e texto-suave sobre cartão) e diga se algum fica abaixo de 4,5:1 (texto) ou 3:1 (limite de componente).
5. Liste TODAS as divergências em relação ao DESIGN.md e à referência, uma por linha, com a decisão que precisa de mim: textos extras mantidos na tela de feedback; chat no lugar de "Nova anotação + lista"; erro sem vermelho; borda de campo com cerca de 2:1; tela Dados derivada; rodapé mantido; qualquer outra.

Diga claramente se a Etapa 9 está concluída ("pronta quando: o app tem a aparência da referência em todas as telas, nenhum fluxo mudou e a suíte passa sem alterações 