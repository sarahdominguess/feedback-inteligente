/**
 * Testes dos formatadores de exibição.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * mostra uma entrada e explica, no comentário, por que aquela saída é a
 * esperada.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  formatarData,
  formatarDataHora,
  formatarDiferencaPercentual,
  formatarInteiro,
  formatarMes,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
  rotuloMetrica,
  rotuloSituacaoAcompanhamento,
  rotuloSituacaoMetrica,
} from './formatadores.js';

/**
 * Troca espaços "não separáveis" por espaço comum.
 *
 * Por quê: o Intl.NumberFormat em pt-BR separa "R$" do número com um espaço
 * especial (U+00A0), que serve para o valor não quebrar em duas linhas.
 * Visualmente é um espaço normal, mas comparar o texto cru falharia por um
 * detalhe invisível. Normalizar deixa o teste focado no que importa.
 */
function normalizarEspacos(texto) {
  return texto.replace(/[\u00A0\u202F]/g, ' ');
}

// Mesmo travessão usado pelos formatadores quando falta o valor.
const TRAVESSAO = '—';

// Sinal de menos tipográfico (U+2212), igual ao usado pelos formatadores.
const MENOS = '\u2212';

// ---------------------------------------------------------------------------
// Moeda
// ---------------------------------------------------------------------------

test('formatarMoeda mostra reais com milhar, vírgula e duas casas', () => {
  // 1234.5 reais viram "R$ 1.234,50": ponto no milhar e vírgula no decimal,
  // que é o padrão brasileiro do Intl com style "currency".
  assert.equal(normalizarEspacos(formatarMoeda(1234.5)), 'R$ 1.234,50');
});

test('formatarMoeda mostra zero como valor, não como ausência', () => {
  // Zero é um número válido (a pessoa vendeu zero), então aparece "R$ 0,00";
  // travessão é reservado para dado ausente.
  assert.equal(normalizarEspacos(formatarMoeda(0)), 'R$ 0,00');
});

test('formatarMoeda mantém o sinal de menos do valor negativo', () => {
  // Em pt-BR o Intl escreve o sinal antes do "R$", então -50 vira "-R$ 50,00".
  assert.equal(normalizarEspacos(formatarMoeda(-50)), '-R$ 50,00');
});

test('formatarMoeda devolve travessão quando o valor não é número', () => {
  // null/undefined: a API não tinha o dado; NaN: conta inválida; "1234" é
  // texto; Infinity não existe em JSON. Nenhum deve virar "NaN" na tela.
  for (const valor of [null, undefined, Number.NaN, '1234', Infinity, {}]) {
    assert.equal(formatarMoeda(valor), TRAVESSAO);
  }
});

// ---------------------------------------------------------------------------
// Número decimal e inteiro
// ---------------------------------------------------------------------------

test('formatarNumero usa duas casas decimais por padrão', () => {
  // 1.2 precisa de um zero à direita para ficar "1,20", do jeito que se
  // escreve no Brasil.
  assert.equal(formatarNumero(1.2), '1,20');

  // Com uma casa, 1234.567 arredonda para "1.234,6".
  assert.equal(formatarNumero(1234.567, 1), '1.234,6');
});

test('formatarNumero aceita zero e quantidade zero de casas', () => {
  assert.equal(formatarNumero(0), '0,00');

  // 1.5 com zero casas arredonda para o inteiro mais próximo: "2".
  assert.equal(formatarNumero(1.5, 0), '2');
});

test('formatarNumero devolve travessão para valor inválido', () => {
  for (const valor of [null, undefined, Number.NaN, '1,2']) {
    assert.equal(formatarNumero(valor), TRAVESSAO);
  }
});

test('formatarInteiro separa milhares e não mostra casas decimais', () => {
  assert.equal(formatarInteiro(3250), '3.250');
  assert.equal(formatarInteiro(0), '0');

  // 999 não tem milhar para separar: fica "999".
  assert.equal(formatarInteiro(999), '999');

  // O sinal vem antes do milhar: -1234 vira "-1.234".
  assert.equal(formatarInteiro(-1234), '-1.234');
});

test('formatarInteiro devolve travessão para valor inválido', () => {
  for (const valor of [null, undefined, Number.NaN, '3250']) {
    assert.equal(formatarInteiro(valor), TRAVESSAO);
  }
});

// ---------------------------------------------------------------------------
// Porcentagem
// ---------------------------------------------------------------------------

test('formatarPercentual converte fração em texto de porcentagem', () => {
  // A API manda a taxa como fração (0 a 1). 0.325 vira "32,5%" porque a
  // multiplicação por 100 é só de exibição.
  assert.equal(formatarPercentual(0.325), '32,5%');
  assert.equal(formatarPercentual(0), '0,0%');
  assert.equal(formatarPercentual(1), '100,0%');
});

test('formatarPercentual respeita a quantidade de casas pedida', () => {
  // 0.25 com zero casas fica "25%", sem vírgula.
  assert.equal(formatarPercentual(0.25, 0), '25%');

  // 0.5 com duas casas fica "50,00%".
  assert.equal(formatarPercentual(0.5, 2), '50,00%');
});

test('formatarPercentual devolve travessão para valor inválido', () => {
  for (const valor of [null, undefined, Number.NaN, '0.5']) {
    assert.equal(formatarPercentual(valor), TRAVESSAO);
  }
});

// ---------------------------------------------------------------------------
// Diferença em relação à média
// ---------------------------------------------------------------------------

test('formatarDiferencaPercentual mostra sinal de mais quando está acima', () => {
  // O contrato do backend diz que diferenca_percentual é FRAÇÃO:
  // "(valor menos média) dividido pela média". Logo 0.123 = 12,3% acima.
  assert.equal(formatarDiferencaPercentual(0.123), '+12,3%');
  assert.equal(formatarDiferencaPercentual(0.2), '+20,0%');
});

test('formatarDiferencaPercentual usa o sinal de menos tipográfico', () => {
  // -0.08 é 8% abaixo; o texto usa "−" (U+2212), não o hífen do teclado.
  assert.equal(formatarDiferencaPercentual(-0.08), `${MENOS}8,0%`);
});

test('formatarDiferencaPercentual mostra zero sem sinal', () => {
  // Zero significa "na média do time": não é positivo nem negativo.
  assert.equal(formatarDiferencaPercentual(0), '0,0%');
});

test('formatarDiferencaPercentual devolve travessão para valor inválido', () => {
  for (const valor of [null, undefined, Number.NaN]) {
    assert.equal(formatarDiferencaPercentual(valor), TRAVESSAO);
  }
});

// ---------------------------------------------------------------------------
// Mês
// ---------------------------------------------------------------------------

test('formatarMes escreve o mês por extenso em português', () => {
  assert.equal(formatarMes('2026-10'), 'outubro de 2026');
  assert.equal(formatarMes('2026-01'), 'janeiro de 2026');
  assert.equal(formatarMes('2026-12'), 'dezembro de 2026');
});

test('formatarMes devolve travessão para mês inválido', () => {
  // 2026-13 não existe; 2026/10 e "outubro" não estão no formato AAAA-MM;
  // texto vazio, null, undefined, NaN e número não são mês em texto.
  for (const valor of [
    '2026-13',
    '2026/10',
    'outubro',
    '',
    null,
    undefined,
    Number.NaN,
    202610,
  ]) {
    assert.equal(formatarMes(valor), TRAVESSAO);
  }
});

// ---------------------------------------------------------------------------
// Datas
// ---------------------------------------------------------------------------

test('formatarData troca a ordem para dia/mês/ano', () => {
  assert.equal(formatarData('2026-10-10'), '10/10/2026');
});

test('formatarData não troca o dia por causa do fuso horário', () => {
  // "Fuso horário" é a diferença de horas entre países. O Brasil fica três
  // horas atrás do UTC. Se usássemos new Date("2026-01-01"), a meia-noite
  // UTC viraria 21h do dia 31/12 no Brasil e a tela mostraria o dia errado.
  // Montando a data pelas partes do texto, 01/01/2026 continua 01/01/2026.
  assert.equal(formatarData('2026-01-01'), '01/01/2026');
});

test('formatarData usa só a data quando o texto vem com hora', () => {
  // gerado_em é data e hora em ISO; para mostrar só o dia, aproveitamos a
  // parte inicial do texto.
  assert.equal(formatarData('2026-11-11T14:30:00'), '11/11/2026');
});

test('formatarData devolve travessão para data inválida', () => {
  // 30/02 não existe (o calendário "escorrega" para março e a validação pega);
  // 2026-13-01 tem mês 13; "10/10/2026" está no formato brasileiro, não no
  // AAAA-MM-DD; vazio, null, undefined e número não são datas em texto.
  for (const valor of [
    '2026-02-30',
    '2026-13-01',
    '10/10/2026',
    '',
    null,
    undefined,
    20261010,
  ]) {
    assert.equal(formatarData(valor), TRAVESSAO);
  }
});

test('formatarDataHora mostra data e hora no formato brasileiro', () => {
  assert.equal(
    formatarDataHora('2026-11-11T14:30:00'),
    '11/11/2026 às 14:30',
  );
});

test('formatarDataHora mantém os números mesmo com fuso ou fração no fim', () => {
  // "Z" e "-03:00" indicam o fuso do texto; microssegundos aparecem depois
  // dos segundos. Não convertemos nada: mostramos os números como vieram
  // para não trocar o dia nem a hora sem avisar.
  assert.equal(
    formatarDataHora('2026-11-11T14:30:00Z'),
    '11/11/2026 às 14:30',
  );
  assert.equal(
    formatarDataHora('2026-11-11T14:30:00-03:00'),
    '11/11/2026 às 14:30',
  );
  assert.equal(
    formatarDataHora('2026-11-11T14:30:00.123456+00:00'),
    '11/11/2026 às 14:30',
  );
});

test('formatarDataHora devolve travessão para texto sem hora ou inválido', () => {
  // "2026-11-11" não tem hora; 25:00 não existe; 30/02 não existe;
  // "agora" não é ISO; null e undefined não são texto.
  for (const valor of [
    '2026-11-11',
    '2026-11-11T25:00',
    '2026-02-30T10:00',
    'agora',
    null,
    undefined,
  ]) {
    assert.equal(formatarDataHora(valor), TRAVESSAO);
  }
});

// ---------------------------------------------------------------------------
// Rótulos
// ---------------------------------------------------------------------------

test('rotuloMetrica traduz os nomes conhecidos', () => {
  assert.equal(rotuloMetrica('ticket_medio'), 'Ticket médio');
  assert.equal(
    rotuloMetrica('pecas_por_atendimento'),
    'Peças por atendimento (P.A.)',
  );
  assert.equal(rotuloMetrica('conversao'), 'Taxa de conversão');
});

test('rotuloMetrica devolve o próprio texto quando não conhece', () => {
  // Mostrar o nome que a API mandou é melhor do que esconder o dado atrás
  // de um travessão.
  assert.equal(rotuloMetrica('nova_metrica'), 'nova_metrica');
});

test('rotuloMetrica não confunde nomes herdados do JavaScript', () => {
  // "constructor" existe em todo objeto por herança; sem Object.hasOwn, a
  // função devolveria uma função interna no lugar de texto. Aqui tratamos
  // como nome desconhecido e devolvemos o próprio texto.
  assert.equal(rotuloMetrica('constructor'), 'constructor');
});

test('rotuloMetrica devolve travessão sem texto útil', () => {
  for (const valor of [null, undefined, Number.NaN, '', '   ']) {
    assert.equal(rotuloMetrica(valor), TRAVESSAO);
  }
});

test('rotuloSituacaoMetrica traduz as quatro situações', () => {
  assert.equal(rotuloSituacaoMetrica('acima'), 'Acima da média do time');
  assert.equal(rotuloSituacaoMetrica('abaixo'), 'Abaixo da média do time');
  assert.equal(rotuloSituacaoMetrica('na_media'), 'Na média do time');
  assert.equal(
    rotuloSituacaoMetrica('indisponivel'),
    'Sem dados para comparar',
  );
});

test('rotuloSituacaoMetrica devolve o próprio texto ou travessão', () => {
  // Situação desconhecida volta como veio; sem texto útil, travessão.
  assert.equal(rotuloSituacaoMetrica('outra_coisa'), 'outra_coisa');
  assert.equal(rotuloSituacaoMetrica(null), TRAVESSAO);
  assert.equal(rotuloSituacaoMetrica(Number.NaN), TRAVESSAO);
});

test('rotuloSituacaoAcompanhamento traduz as duas situações', () => {
  assert.equal(rotuloSituacaoAcompanhamento('com_roteiro'), 'Roteiro preparado');
  assert.equal(rotuloSituacaoAcompanhamento('sem_roteiro'), 'Sem roteiro');
});

test('rotuloSituacaoAcompanhamento devolve o próprio texto ou travessão', () => {
  assert.equal(
    rotuloSituacaoAcompanhamento('situacao_nova'),
    'situacao_nova',
  );
  assert.equal(rotuloSituacaoAcompanhamento(undefined), TRAVESSAO);
});
