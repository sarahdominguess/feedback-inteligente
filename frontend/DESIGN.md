# DESIGN.md — Return.Ai

Guia de design da plataforma Return.Ai, assistente de IA que ajuda líderes a transformar dados e observações do dia a dia em conversas de feedback humanas, justas e práticas.

Este documento descreve o visual das telas **Feedback** e **Anotações** e serve de base para as demais (ex.: **Dados**).

---

## 1. Princípios

- **Humano antes de tecnológico.** A IA entrega um roteiro; o gerente continua dono da conversa.
- **Simples e legível.** Pouco ruído visual, texto grande, blocos bem separados.
- **Consistente com a marca.** Fundo escuro, verde e roxo da logo como únicos destaques.
- **Sem jargões.** Rótulos e textos em português claro.

---

## 2. Cores

| Token | Hex | Uso |
|---|---|---|
| `--bg` | `#16151A` | Fundo da página (igual ao fundo da logo) |
| `--card` | `#222029` | Cartões, botões secundários, itens do menu |
| `--line` | `#2E2C36` | Divisórias do cabeçalho e da barra lateral |
| `--border` | `#4A4757` | Bordas de campos (select, textarea) |
| `--ink` | `#F2F0EA` | Texto principal |
| `--ink-soft` | `#E2DFEA` | Texto corrido dentro dos cartões |
| `--mute` | `#BDBAC8` | Texto secundário, rótulos, notas |
| `--green` | `#3DDC97` | Destaque principal: ação primária, item ativo, positivo |
| `--on-green` | `#0B2E1F` | Texto sobre verde |
| `--purple` | `#A66BF2` | Destaque secundário: melhorias, hipóteses, usuário |

**Regras**
- Verde = ação principal e o que está indo bem. Roxo = pontos de atenção e informação de apoio.
- Texto sempre com contraste mínimo de 4,5:1 sobre o fundo.
- Não usar branco puro nem preto puro.
- Cores nunca são o único sinal de significado: cada bloco tem ícone e título.

---

## 3. Tipografia

Fonte: **Inter** (Google Fonts), pesos 400, 600, 700 e 800. Fallback: `sans-serif`.

| Papel | Tamanho | Peso |
|---|---|---|
| Título da página (`h1`) | 40 px | 800 |
| Título de bloco (`h3`) | 21–22 px | 700 |
| Item do menu / botão / campo | 17 px | 600–700 |
| Texto corrido nos cartões | 17 px, entrelinha 1,5 | 400 |
| Rótulo de campo | 15 px | 600 |
| Nota de apoio | 14 px | 400 |

---

## 4. Layout

- **Cabeçalho** (84 px): logo Return.Ai à esquerda; nome e cargo do usuário (ex.: Diego, Gerente) com avatar redondo roxo à direita. Divisória inferior `--line`.
- **Barra lateral:** 260 px expandida, 88 px recolhida, à esquerda do conteúdo. Divisória direita `--line`.
- **Conteúdo:** largura máxima de 1160 px, padding de 40 px por 48 px, espaçamento de 24 px entre blocos.
- **Telas de página:** largura fluida a partir de 1280 px; em telas estreitas, a barra lateral começa recolhida e os blocos empilham.

---

## 5. Componentes

### Logo
Imagem completa da logo Return.Ai no cabeçalho, altura de 56 px, sobre o fundo `--bg` (o fundo da imagem é o mesmo da página, então não aparece caixa).

### Barra lateral
- Botão de **recolher/expandir** no topo, com ícone de painel. Quando recolhida, só ficam os ícones e o avatar.
- Itens: **Feedback**, **Anotações**, **Dados**, cada um com ícone de traço (24 px, traço de 2 px) e rótulo.
- Item ativo: fundo `--green`, texto `--on-green`, peso 700.
- Item inativo: fundo `--card`, texto `--ink`, peso 600.
- Altura de 52 px, raio de 14 px, espaço de 12 px entre itens.
- Cartão do vendedor selecionado no fim da barra: avatar redondo verde com iniciais, nome e função, borda superior roxa de 4 px. Recolhida, mostra só o avatar.
- Os ícones precisam de `aria-label` quando o rótulo está oculto.

### Botão primário
Fundo `--green`, texto `--on-green`, altura de 52 px, raio de 12 px, peso 700, sem borda. Ex.: **Gerar feedback**, **Salvar anotação**.

### Campos
Fundo `--card` (select) ou `--bg` (textarea), borda `--border` de 1 px, raio de 12 px, altura mínima de 52 px, texto 17 px. Todo campo tem `label` visível.

### Cartão de conteúdo
Fundo `--card`, raio de 18 px, padding de 26 px por 28 px, barra lateral esquerda de 6 px na cor do bloco.
- Título com ícone em círculo de 36 px (fundo `--bg`, ícone na cor do bloco).
- Listas com 12 px de espaço entre itens.

---

## 6. Tela Feedback

Ordem dos elementos:

1. Título **Gerar feedback**
2. Campo **Período** e botão **Gerar feedback**
3. Quatro cartões, nesta ordem:

| Cartão | Ícone | Cor | Formato |
|---|---|---|---|
| Pontos positivos | tendência de alta | verde | lista |
| Pontos de melhoria | alvo | roxo | lista |
| Possíveis motivos | lupa | roxo | lista, com nota "São hipóteses para investigar na conversa, não conclusões." |
| Roteiro de conversa sugerido | balão de mensagem | verde | lista numerada |

**Regra de conteúdo:** a tela mostra apenas o feedback gerado pelo sistema, a partir dos números reais e das anotações do gerente. Não inserir textos extras, avisos ou explicações da interface em volta dele.

---

## 7. Tela Anotações

1. Título **Anotações**
2. Cartão **Nova anotação** com campo de texto e botão **Salvar anotação** (borda superior verde)
3. Lista de anotações salvas, cada uma com data e texto, com barra lateral verde ou roxa

---

## 8. Acessibilidade

- Elementos reais: `button`, `a`, `select`, `textarea` e `label`, nunca `div` clicável.
- Foco visível: contorno de 3 px em `--green`.
- Alvos de toque com pelo menos 44 px.
- Ícones decorativos com `aria-hidden`; ícones sozinhos com `aria-label`.
- Texto mínimo de 14 px (notas) e 17 px (corpo).

---

## 9. Voz e texto

- Português do Brasil, direto e sem termos técnicos.
- Rótulos curtos: **Feedback**, **Anotações**, **Dados**, **Período**, **Gerar feedback**.
- O sistema trata o gerente como dono da conversa: sugere, nunca envia mensagem automática ao funcionário.
