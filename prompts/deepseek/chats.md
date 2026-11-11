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