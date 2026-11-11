
---
version: alpha
format: "DESIGN.md"
schema: "design-md"
name: "fullstore"
title: "FullStore - Cultura de alta performance em suas lojas físicas"
description: "DESIGN.md técnico extraído automaticamente de FullStore - Cultura de alta performance em suas lojas físicas. Use este arquivo como fonte de verdade para gerar interfaces consistentes em ferramentas de IA. Inclui papéis semânticos de cor, escala tipográfica, espaçamento, raios, componentes, aplicações e regras de uso. Foram detectados 60 cores, 24 estilos tipográficos e 6 componentes-base."
source: "https://fullstore.io/"
domain: "fullstore.io"
generatedAt: "2026-11-08T16:29:56+00:00"
generator: "CamaraUX DESIGN.md Generator"
compatibility:
  stitch: "https://stitch.withgoogle.com/docs/design-md/overview"
  intent: "Token-driven UI guidance for AI tools and design generators"
author:
  name: "CamaraUX"
  url: "https://camaraux.com.br"

colors:
  primary: "#00E6B8"
  primary-active: "#74F1CE"
  secondary: "#74F1CE"
  ink: "#17171C"
  body: "#2E2E38"
  muted: "#2E2E38"
  hairline: "#D1D5DB"
  canvas: "#8328D9"
  surface-soft: "#F5EFFB"
  surface-card: "#8328D9"
  on-primary: "#111111"
  on-dark: "#ffffff"
  scrim: "#000000"
  accent: "#74F1CE"
  background: "#6402B1"
  background-color: "#1E1E24"
  background-color-2: "#8601E4"
  background-color-3: "#9333EA"
  background-color-4: "#FEE2E2"
  background-color-5: "#3C3742"
  background-color-6: "#530194"
  background-color-7: "#A1A1AA"
  background-color-8: "#7E22CE"
  color: "#FFFFFF"
  border-color: "#9CA3AF"
  border-color-2: "#FECACA"
  border-color-3: "#48EDBA"
  background-color-9: "#171717"
  background-color-10: "#1B1B1F"
  background-color-11: "#37076E"
  background-color-12: "#3A3A40"
  background-color-13: "#42C9A2"
  background-color-14: "#6801B2"
  background-color-15: "#6929A9"
  background-color-16: "#D0D0D8"
  background-color-17: "#E8DEFB"

typography:
  display-xl:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "48px"
    fontWeight: "400"
    lineHeight: "1.1"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "h1"
  display-lg:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "36px"
    fontWeight: "400"
    lineHeight: "1.15"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "h2"
  display-md:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "28px"
    fontWeight: "400"
    lineHeight: "1.2"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "h3"
  display-sm:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "22px"
    fontWeight: "400"
    lineHeight: "1.25"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "h4"
  body-md:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "body"
  caption:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "12px"
    fontWeight: "500"
    lineHeight: "1.35"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "small"
  button-md:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "14px"
    fontWeight: "700"
    lineHeight: "1.2"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "button"
  link:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.4"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "a"
  input:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.25"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "input"
  label:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "14px"
    fontWeight: "700"
    lineHeight: "1.3"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "label"
  font-face-1:
    fontFamily: "'Space Grotesk', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: "300"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "system-ui"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "@font-face"
  font-face-2:
    fontFamily: "'Space Grotesk', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "system-ui"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "@font-face"
  font-face-3:
    fontFamily: "'Space Grotesk', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: "500"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "system-ui"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "@font-face"
  font-face-4:
    fontFamily: "'Space Grotesk', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: "600"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "system-ui"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "@font-face"
  font-face-5:
    fontFamily: "'Space Grotesk', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: "700"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "system-ui"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "@font-face"
  font-family-1:
    fontFamily: "'Space Grotesk', sans-serif"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "detected"
  font-family-2:
    fontFamily: "'Space Grotesk', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "system-ui"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "detected"
  font-family-3:
    fontFamily: "ui-sans-serif, system-ui, sans-serif, \"Apple Color Emoji\", \"Segoe UI Emoji\", Segoe UI Symbol"
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.5"
    letterSpacing: "0"
    fallback: "ui-sans-serif"
    fontSource: "system-or-public"
    isCustomFont: "false"
    sourceSelector: "detected"

rounded:
  none: "0px"
  xs: "2px"
  sm: "4px"
  md: "12px"
  lg: "1rem"
  xl: "16px"
  full: "9999px"

spacing:
  xxs: "0px"
  xs: "1px"
  sm: "3px"
  md: "5px"
  base: "7px"
  lg: "10px"
  xl: "12px"
  xxl: "1rem"
  section: "16px"

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm} {spacing.lg}"
    height: "44px"
  button-secondary:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.button-md}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm} {spacing.lg}"
    height: "44px"
    border: "1px solid {colors.hairline}"
  text-link:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    typography: "{typography.link}"
  text-input:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.input}"
    rounded: "{rounded.md}"
    padding: "{spacing.sm} {spacing.base}"
    height: "44px"
    border: "1px solid {colors.hairline}"
  surface-card:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
    border: "1px solid {colors.hairline}"
  badge-pill:
    backgroundColor: "{colors.surface-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "{spacing.xs} {spacing.sm}"
  top-nav:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.link}"
    height: "64px"
    border: "1px solid {colors.hairline}"
  hero-section:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.display-lg}"
    padding: "{spacing.section} {spacing.xl}"
  feature-card:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
    border: "1px solid {colors.hairline}"
  application-shell:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.xl}"
    padding: "{spacing.xl}"
  input-field:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.xs}"
    selector: "input, textarea, select"
  card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.xs}"
    selector: ".card, [class*=\"card\"], article"
  badge:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.xs}"
    selector: ".badge, .tag, [class*=\"badge\"], [class*=\"tag\"]"
  navigation:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.xs}"
    selector: "nav, header"

applications:
  landing-page:
    description: "Composição de hero, navegação, CTA e cards usando os tokens principais do arquivo."
    components:
      - "top-nav"
      - "hero-section"
      - "button-primary"
      - "feature-card"
  dashboard-card-grid:
    description: "Grid de cards para apresentar métricas, recursos ou módulos de produto."
    components:
      - "surface-card"
      - "badge-pill"
      - "button-secondary"
  form-flow:
    description: "Fluxo simples com input, link de apoio e CTA principal."
    components:
      - "text-input"
      - "button-primary"
      - "text-link"
  content-preview:
    description: "Página de conteúdo com navegação, card visual e ações rápidas."
    components:
      - "top-nav"
      - "application-shell"
      - "feature-card"

usage:
  instruction: "Use os tokens semânticos abaixo antes de criar novos valores. Preserve nomes, cores, fontes, espaçamentos e raios do arquivo."
  primaryAction: "{components.button-primary}"
  secondaryAction: "{components.button-secondary}"
  mainText: "{colors.ink}"
  pageBackground: "{colors.canvas}"
  cardSurface: "{colors.surface-card}"
  defaultRadius: "{rounded.md}"
  defaultSpacing: "{spacing.base}"
  accessibility:
    minimumTouchTarget: "44px"
    textContrast: "WCAG AA when possible"
    focusVisible: "Use a visible focus ring for keyboard navigation"
  aiRules:
    - "Use token references such as {colors.primary}, {typography.body-md}, {spacing.base} and {rounded.md}."
    - "Do not invent brand colors when an equivalent token exists."
    - "Use components from the components map before creating new components."
    - "Keep generated layouts responsive and accessible."

---

# FullStore - Cultura de alta performance em suas lojas físicas Design System

## Overview

**FullStore - Cultura de alta performance em suas lojas físicas** usa uma linguagem visual sóbria, escura e de alto contraste, com formas arredondadas e aparência amigável. O sistema abaixo organiza cores, tipografia, espaçamentos, raios, componentes e exemplos de aplicação para orientar criação de interfaces por humanos e ferramentas de IA.

**Resumo visual:**
- **Marca/ação:** `{colors.primary}` (`#00E6B8`) deve conduzir CTAs, estados ativos e elementos de maior prioridade.
- **Base da página:** `{colors.canvas}` (`#8328D9`) define o fundo principal.
- **Superfícies:** `{colors.surface-card}` (`#8328D9`) sustenta cards, painéis e blocos destacados.
- **Texto principal:** `{colors.ink}` (`#17171C`) mantém legibilidade em títulos, parágrafos e ícones.
- **Componentes:** use primeiro os tokens em `components` antes de criar variações novas.

**Dados analisados:**
- **Fonte:** https://fullstore.io/
- **Domínio:** `fullstore.io`
- **Cores normalizadas:** 36
- **Estilos tipográficos:** 18
- **Componentes-base:** 14

> Este DESIGN.md é uma base técnica gerada automaticamente. Revise nomes, papéis semânticos e componentes críticos antes de usar em produção.

## Colors

Use a paleta por papel semântico, não apenas por valor HEX. Isso evita que ferramentas de IA usem cores decorativas, semânticas ou de alerta como identidade principal.

### Core roles

- **Primary** (`#00E6B8`): CTAs, links importantes, foco, seleção e principais elementos interativos.
- **Primary active** (`#74F1CE`): Hover, pressed, active e variações de maior contraste do primário.
- **Secondary** (`#74F1CE`): Apoio visual, chips, ações secundárias e destaques complementares.
- **Accent** (`#74F1CE`): Destaques visuais, gradientes, ilustrações e elementos editoriais.
- **Canvas** (`#8328D9`): Fundo principal da página.
- **Surface** (`#8328D9`): Cards, painéis, modais e superfícies contidas.
- **Ink** (`#17171C`): Títulos, texto forte e ícones principais.
- **Body** (`#2E2E38`): Texto de leitura e conteúdo corrente.
- **Muted** (`#2E2E38`): Descrições, metadados, placeholders e textos de baixa ênfase.
- **Border** (`#D1D5DB`): Divisórias, bordas, outlines e separadores.

### Supporting tokens

- **`{colors.surface-soft}`** (`#F5EFFB`): Superfícies suaves e áreas secundárias.
- **`{colors.on-primary}`** (`#111111`): Texto sobre fundo primário.
- **`{colors.on-dark}`** (`#ffffff`): Cor detectada no site.
- **`{colors.scrim}`** (`#000000`): Cor detectada no site.
- **`{colors.background}`** (`#6402B1`): Cor detectada no site.
- **`{colors.background-color}`** (`#1E1E24`): Cor detectada no site.
- **`{colors.background-color-2}`** (`#8601E4`): Cor detectada no site.
- **`{colors.background-color-3}`** (`#9333EA`): Cor detectada no site.
- **`{colors.background-color-4}`** (`#FEE2E2`): Cor detectada no site.
- **`{colors.background-color-5}`** (`#3C3742`): Cor detectada no site.
- **`{colors.background-color-6}`** (`#530194`): Cor detectada no site.
- **`{colors.background-color-7}`** (`#A1A1AA`): Cor detectada no site.
- **`{colors.background-color-8}`** (`#7E22CE`): Cor detectada no site.
- **`{colors.color}`** (`#FFFFFF`): Cor detectada no site.
- **`{colors.border-color}`** (`#9CA3AF`): Cor detectada no site.
- **`{colors.border-color-2}`** (`#FECACA`): Cor detectada no site.
- **`{colors.border-color-3}`** (`#48EDBA`): Cor detectada no site.
- **`{colors.background-color-9}`** (`#171717`): Cor detectada no site.

### Usage rules

- Use `{colors.primary}` somente para ações e elementos de alta prioridade.
- Use `{colors.canvas}` como base e `{colors.surface-card}` para cards, painéis e áreas elevadas.
- Use `{colors.ink}` e `{colors.body}` para leitura; `{colors.muted}` para apoio e metadados.
- Use `{colors.success}`, `{colors.warning}` e `{colors.danger}` apenas para estados semânticos.
- Não transforme cores de alerta, erro ou decoração em cor principal da marca.

## Typography

A escala tipográfica foi consolidada por função para facilitar uso em prompts, protótipos e componentes. Preserve a pilha `fontFamily` detectada; quando a fonte for customizada, mantenha os fallbacks.

### Display & headings

| Token | Font | Size | Weight | Line | Tracking | Use |
|---|---|---:|---:|---:|---:|---|
| `{typography.display-xl}` | `'Space Grotesk', sans-serif` | `48px` | `400` | `1.1` | `0` | Títulos e chamadas |
| `{typography.display-lg}` | `'Space Grotesk', sans-serif` | `36px` | `400` | `1.15` | `0` | Títulos e chamadas |
| `{typography.display-md}` | `'Space Grotesk', sans-serif` | `28px` | `400` | `1.2` | `0` | Títulos e chamadas |
| `{typography.display-sm}` | `'Space Grotesk', sans-serif` | `22px` | `400` | `1.25` | `0` | Títulos e chamadas |

### Body & reading

| Token | Font | Size | Weight | Line | Tracking | Use |
|---|---|---:|---:|---:|---:|---|
| `{typography.body-md}` | `'Space Grotesk', sans-serif` | `16px` | `400` | `1.5` | `0` | Texto e interface |
| `{typography.caption}` | `'Space Grotesk', sans-serif` | `12px` | `500` | `1.35` | `0` | Texto e interface |

### Interface

| Token | Font | Size | Weight | Line | Tracking | Use |
|---|---|---:|---:|---:|---:|---|
| `{typography.button-md}` | `'Space Grotesk', sans-serif` | `14px` | `700` | `1.2` | `0` | Botões e CTAs |
| `{typography.label}` | `'Space Grotesk', sans-serif` | `14px` | `700` | `1.3` | `0` | Labels e microcopy |
| `{typography.input}` | `'Space Grotesk', sans-serif` | `16px` | `400` | `1.25` | `0` | Texto e interface |
| `{typography.link}` | `'Space Grotesk', sans-serif` | `16px` | `400` | `1.4` | `0` | Links e navegação |

### Additional detected styles

- **`{typography.font-face-1}`**: `16px` / weight `300` / line `1.5` using `'Space Grotesk', system-ui, sans-serif`.
- **`{typography.font-face-2}`**: `16px` / weight `400` / line `1.5` using `'Space Grotesk', system-ui, sans-serif`.
- **`{typography.font-face-3}`**: `16px` / weight `500` / line `1.5` using `'Space Grotesk', system-ui, sans-serif`.
- **`{typography.font-face-4}`**: `16px` / weight `600` / line `1.5` using `'Space Grotesk', system-ui, sans-serif`.
- **`{typography.font-face-5}`**: `16px` / weight `700` / line `1.5` using `'Space Grotesk', system-ui, sans-serif`.
- **`{typography.font-family-1}`**: `16px` / weight `400` / line `1.5` using `'Space Grotesk', sans-serif`.
- **`{typography.font-family-2}`**: `16px` / weight `400` / line `1.5` using `'Space Grotesk', system-ui, sans-serif`.
- **`{typography.font-family-3}`**: `16px` / weight `400` / line `1.5` using `ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol`.

### Typography principles

- Use display/headline tokens para hierarquia principal e body tokens para leitura contínua.
- Não adicione uma nova família se a fonte original não carregar; mantenha a pilha de fallback.
- Preserve pesos e alturas de linha detectados para evitar mudança de personalidade visual.
- Labels, badges e botões devem usar os tokens de interface para manter densidade e legibilidade.

## Layout

### Escala de espaçamento
| Token | Valor | Uso sugerido |
|---|---:|---|
| `{spacing.xxs}` | `0px` | Micro ajustes |
| `{spacing.xs}` | `1px` | Ícones e chips |
| `{spacing.sm}` | `3px` | Elementos compactos |
| `{spacing.md}` | `5px` | Inputs e grupos |
| `{spacing.base}` | `7px` | Ritmo base |
| `{spacing.lg}` | `10px` | Cards |
| `{spacing.xl}` | `12px` | Blocos |
| `{spacing.xxl}` | `1rem` | Seções grandes |
| `{spacing.section}` | `16px` | Separação entre seções |

### Escala de raios
| Token | Valor | Uso sugerido |
|---|---:|---|
| `{rounded.none}` | `0px` | Elementos retos |
| `{rounded.xs}` | `2px` | Pequenos controles |
| `{rounded.sm}` | `4px` | Botões compactos |
| `{rounded.md}` | `12px` | Inputs e cards pequenos |
| `{rounded.lg}` | `1rem` | Cards |
| `{rounded.xl}` | `16px` | Painéis grandes |
| `{rounded.full}` | `9999px` | Pills e círculos |

### Princípios de layout
- Use espaçamento consistente entre seções, cards e grupos de formulário.
- Reserve `{spacing.section}` para blocos grandes e `{spacing.lg}` / `{spacing.xl}` para cards.
- Use `{rounded.full}` apenas para pills, avatares e botões circulares.
- Não misture raios intermediários fora da escala documentada.

## Elevation & Depth

| Nível | Tratamento | Uso |
|---|---|---|
| Flat | Sem sombra | Fundos, seções e blocos editoriais |
| Hairline | `1px solid {colors.hairline}` | Inputs, cards e divisórias |
| Soft card | Borda leve + superfície `{colors.surface-card}` | Cards, painéis e módulos de conteúdo |
| Modal / overlay | `{colors.scrim}` com opacidade aplicada no CSS | Modais, drawers e estados focados |

A extração automática prioriza bordas, cores de superfície e raios. Sombras complexas devem ser revisadas manualmente quando forem essenciais para a identidade visual.

## Shapes

A linguagem de forma foi derivada dos raios detectados em botões, inputs, cards e superfícies.

| Token | Valor | Uso sugerido |
|---|---:|---|
| `{rounded.none}` | `0px` | Elementos retos |
| `{rounded.xs}` | `2px` | Pequenos controles |
| `{rounded.sm}` | `4px` | Botões compactos |
| `{rounded.md}` | `12px` | Inputs e cards pequenos |
| `{rounded.lg}` | `1rem` | Cards |
| `{rounded.xl}` | `16px` | Painéis grandes |
| `{rounded.full}` | `9999px` | Pills e círculos |

- Use a escala de raios documentada no frontmatter antes de criar novos valores.
- Preserve consistência entre botões, cards, inputs e pills.

## Components

Componentes são descritos como contratos reutilizáveis. Ao gerar uma tela, escolha primeiro um componente abaixo e depois aplique variações apenas quando necessário.

### Buttons & actions

#### `button-primary`

CTA principal com maior prioridade visual.

- **Background:** `{colors.primary}`
- **Text color:** `{colors.on-primary}`
- **Typography:** `{typography.button-md}`
- **Radius:** `{rounded.md}`
- **Padding:** `{spacing.sm} {spacing.lg}`
- **Height:** `44px`

#### `button-secondary`

Ação secundária ou alternativa.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.button-md}`
- **Radius:** `{rounded.md}`
- **Padding:** `{spacing.sm} {spacing.lg}`
- **Height:** `44px`
- **Border:** `1px solid {colors.hairline}`

#### `text-link`

Link textual para navegação ou ação discreta.

- **Background:** `transparent`
- **Text color:** `{colors.primary}`
- **Typography:** `{typography.link}`

### Forms

#### `text-input`

Campo de formulário padrão.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.input}`
- **Radius:** `{rounded.md}`
- **Padding:** `{spacing.sm} {spacing.base}`
- **Height:** `44px`
- **Border:** `1px solid {colors.hairline}`

### Cards & surfaces

#### `surface-card`

Superfície neutra para conteúdo agrupado.

- **Background:** `{colors.surface-card}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.lg}`
- **Padding:** `{spacing.lg}`
- **Border:** `1px solid {colors.hairline}`

#### `feature-card`

Card visual para recurso, produto ou chamada editorial.

- **Background:** `{colors.surface-card}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.lg}`
- **Padding:** `{spacing.lg}`
- **Border:** `1px solid {colors.hairline}`

#### `application-shell`

Container base para aplicações e previews.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.xl}`
- **Padding:** `{spacing.xl}`

#### `card`

Componente detectado automaticamente no site.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.xs}`
- **Detected selector:** `.card, [class*="card"], article`

### Navigation & badges

#### `top-nav`

Barra de navegação ou cabeçalho.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.link}`
- **Height:** `64px`
- **Border:** `1px solid {colors.hairline}`

#### `badge-pill`

Marcador compacto para status, categoria ou rótulo.

- **Background:** `{colors.surface-soft}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.label}`
- **Radius:** `{rounded.full}`
- **Padding:** `{spacing.xs} {spacing.sm}`

#### `badge`

Componente detectado automaticamente no site.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.xs}`
- **Detected selector:** `.badge, .tag, [class*="badge"], [class*="tag"]`

### Hero & composition

#### `hero-section`

Composição de abertura de página.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.display-lg}`
- **Padding:** `{spacing.section} {spacing.xl}`

### Additional detected components

#### `input-field`

Componente detectado automaticamente no site.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.xs}`
- **Detected selector:** `input, textarea, select`

#### `navigation`

Componente detectado automaticamente no site.

- **Background:** `{colors.canvas}`
- **Text color:** `{colors.ink}`
- **Typography:** `{typography.body-md}`
- **Radius:** `{rounded.xs}`
- **Detected selector:** `nav, header`

## Do's and Don'ts

### Do

- Use `{colors.primary}` apenas para ações, links importantes e elementos que precisam de atenção visual.
- Use `{colors.canvas}` para o fundo base e `{colors.surface-card}` para cards e painéis.
- Use a escala tipográfica do frontmatter antes de criar novos tamanhos.
- Mantenha contraste AA em textos e controles interativos.
- Preserve os tokens de componentes em `components` para botões, inputs, cards e navegação.

### Don't

- Não invente cores de marca fora do frontmatter.
- Não use cores de erro, alerta ou destrutivas como cor primária quando não forem a identidade do site.
- Não misture raios e espaçamentos que não aparecem na escala documentada.
- Não troque a fonte principal por outra família se a fonte custom não estiver disponível; preserve a pilha de fallback.

## Application Examples

Use estes exemplos para transformar tokens em telas. Cada aplicação combina componentes base e evita que a IA crie layouts sem aderência ao sistema.

### Landing Page

Composição de hero, navegação, CTA e cards usando os tokens principais do arquivo.

**Recommended components:**
- `{components.top-nav}`
- `{components.hero-section}`
- `{components.button-primary}`
- `{components.feature-card}`

**Implementation note:** preserve `{colors.primary}`, `{typography.body-md}`, `{spacing.base}` and the documented radius scale before adding custom values.

### Dashboard Card Grid

Grid de cards para apresentar métricas, recursos ou módulos de produto.

**Recommended components:**
- `{components.surface-card}`
- `{components.badge-pill}`
- `{components.button-secondary}`

**Implementation note:** preserve `{colors.primary}`, `{typography.body-md}`, `{spacing.base}` and the documented radius scale before adding custom values.

### Form Flow

Fluxo simples com input, link de apoio e CTA principal.

**Recommended components:**
- `{components.text-input}`
- `{components.button-primary}`
- `{components.text-link}`

**Implementation note:** preserve `{colors.primary}`, `{typography.body-md}`, `{spacing.base}` and the documented radius scale before adding custom values.

### Content Preview

Página de conteúdo com navegação, card visual e ações rápidas.

**Recommended components:**
- `{components.top-nav}`
- `{components.application-shell}`
- `{components.feature-card}`

**Implementation note:** preserve `{colors.primary}`, `{typography.body-md}`, `{spacing.base}` and the documented radius scale before adding custom values.

## Agent Prompt Guide

Use esta seção como instrução direta para ChatGPT, Claude, v0, Lovable, Bolt, Replit, Figma Make, Stitch e outras ferramentas de IA.

### Quick Token Reference

- **Primary CTA:** `{colors.primary}` (`#00E6B8`)
- **Primary text / headings:** `{colors.ink}` (`#17171C`)
- **Body text:** `{colors.body}` (`#2E2E38`)
- **Secondary text:** `{colors.muted}` (`#2E2E38`)
- **Background:** `{colors.canvas}` (`#8328D9`)
- **Card surface:** `{colors.surface-card}` (`#8328D9`)
- **Borders:** `{colors.hairline}` (`#D1D5DB`)
- **Focus / active states:** `{colors.primary-active}` (`#74F1CE`)

### Generation Rules

1. Use only tokens declared in the YAML frontmatter before creating new visual values.
2. Treat `{colors.primary}` as the main brand/action color. Do not replace it with warning, error, or decorative colors.
3. Use `{colors.canvas}` for page backgrounds and `{colors.surface-card}` for cards, modals, panels, and contained surfaces.
4. Use `{typography.display-*}` for major headings, `{typography.body-md}` for reading content, and `{typography.button-md}` for CTAs.
5. When a custom font is unavailable, keep the full `fontFamily` stack and let the fallback defined in the token resolve the rendering.
6. Use the documented spacing and radius scale. Do not invent arbitrary values unless the target component cannot be represented by the system.
7. Preserve contrast: pair `{colors.primary}` with `{colors.on-primary}`, and use `{colors.ink}` or `{colors.body}` on light surfaces.

### Component Defaults

- **`{components.button-primary}`**: use for ações principais, envio de formulários e CTAs de alta prioridade.
- **`{components.button-secondary}`**: use for ações secundárias e alternativas sem competir com o CTA principal.
- **`{components.text-link}`**: use for componentes de interface compatíveis com os tokens extraídos.
- **`{components.text-input}`**: use for campos de formulário, busca e entrada de dados.
- **`{components.surface-card}`**: use for cards, painéis e blocos de conteúdo.
- **`{components.badge-pill}`**: use for componentes de interface compatíveis com os tokens extraídos.
- **`{components.top-nav}`**: use for navegação principal e cabeçalhos.
- **`{components.hero-section}`**: use for componentes de interface compatíveis com os tokens extraídos.

## Quality Notes

Este arquivo foi gerado por análise técnica de HTML/CSS acessível ao WordPress. Ele foi normalizado para melhorar compatibilidade com ferramentas de IA, mas ainda deve ser revisado antes de uso em produção.

### O que foi normalizado
- Cores em `rgb()`, `rgba()`, `hsl()` e HEX curto foram convertidas para HEX de 6 dígitos quando possível.
- Cores de erro, alerta e perigo foram rebaixadas para evitar que virem cor primária por engano.
- Tipografia foi consolidada em papéis semânticos: display, body, caption, button, link, input e label.
- Fontes custom ou externas foram preservadas com fallback no próprio token.
- Espaçamentos e raios foram reduzidos para uma escala reutilizável.

### Possíveis limitações
- Sites que dependem de JavaScript pesado podem expor menos CSS para o WordPress do que para um navegador real.
- Fontes proprietárias podem não aparecer na prévia se não estiverem disponíveis no ambiente de destino.
- Tokens detectados em CSS de terceiros podem aparecer como apoio, mas não devem substituir a identidade principal sem revisão.
- Para maior fidelidade visual, uma etapa futura com navegador headless pode capturar estilos computados e screenshots reais.

## Notes

### Fontes analisadas

- HTML principal
- https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap
- https://fullstore.io/assets/index-clJVrwxt.css

