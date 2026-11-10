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