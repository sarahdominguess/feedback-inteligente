/**
 * Testes do rótulo do dia usado no chat de anotações.
 *
 * O "hoje" é sempre passado por parâmetro, nunca lido do relógio: assim o
 * resultado é previsível e os testes não quebram na virada da meia-noite.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { rotuloDoDia } from './rotuloDoDia.js';

test('mesma data de hoje vira "Hoje"', () => {
  // É o separador do dia em que a conversa está acontecendo.
  assert.equal(rotuloDoDia('2026-10-08', '2026-10-08'), 'Hoje');
});

test('dia anterior vira "Ontem"', () => {
  // 07/10 é um dia antes de 08/10.
  assert.equal(rotuloDoDia('2026-10-07', '2026-10-08'), 'Ontem');
});

test('outros dias mostram a data no padrão brasileiro', () => {
  // Fora de "hoje" e "ontem", a data completa é mais útil que uma palavra.
  assert.equal(rotuloDoDia('2026-08-06', '2026-10-08'), '06/08/2026');
  // Dois dias antes já não é "ontem".
  assert.equal(rotuloDoDia('2026-10-06', '2026-10-08'), '06/10/2026');
});

test('data futura não vira "Hoje" nem "Ontem"', () => {
  // Exibe a data: nada de palavras que sugerem passado.
  assert.equal(rotuloDoDia('2026-10-09', '2026-10-08'), '09/10/2026');
});

test('"Ontem" atravessa a virada de mês (01/11 → 31/10)', () => {
  // O dia 1 não tem "dia 0" no mesmo mês: a conta precisa voltar um mês.
  assert.equal(rotuloDoDia('2026-10-31', '2026-11-01'), 'Ontem');
});

test('"Ontem" atravessa a virada de ano (01/01 → 31/12)', () => {
  // Mesma ideia, agora voltando também o ano.
  assert.equal(rotuloDoDia('2025-12-31', '2026-01-01'), 'Ontem');
});

test('data inválida vira "—"', () => {
  // Texto errado, dia que não existe (30/02) ou valor que não é texto.
  assert.equal(rotuloDoDia('ontem', '2026-10-08'), '—');
  assert.equal(rotuloDoDia('2026-02-30', '2026-10-08'), '—');
  assert.equal(rotuloDoDia('', '2026-10-08'), '—');
  assert.equal(rotuloDoDia(null, '2026-10-08'), '—');
  assert.equal(rotuloDoDia(undefined, '2026-10-08'), '—');
});

test('"hoje" inválido também vira "—"', () => {
  // Sem uma data de hoje confiável não há como dizer "Hoje" nem "Ontem".
  assert.equal(rotuloDoDia('2026-10-08', 'hoje'), '—');
  assert.equal(rotuloDoDia('2026-10-08', null), '—');
});

test('não depende do relógio: o mesmo par devolve sempre o mesmo rótulo', () => {
  // A função é pura: duas chamadas seguidas com a mesma entrada coincidem.
  const primeira = rotuloDoDia('2026-10-07', '2026-10-08');
  const segunda = rotuloDoDia('2026-10-07', '2026-10-08');

  assert.equal(primeira, segunda);
  assert.equal(primeira, 'Ontem');
});
