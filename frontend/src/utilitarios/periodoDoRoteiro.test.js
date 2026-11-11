/**
 * Testes do rótulo de período do roteiro.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { rotuloPeriodo } from './periodoDoRoteiro.js';

test('mês válido vira o nome do mês por extenso', () => {
  // "2026-10" é o formato da API; na tela vira "outubro de 2026".
  assert.equal(rotuloPeriodo('2026-10'), 'outubro de 2026');
});

test('sem mês vira "Todo o histórico"', () => {
  // null é o que a API manda quando a geração usou todo o histórico;
  // undefined e texto vazio são tratados do mesmo jeito.
  assert.equal(rotuloPeriodo(null), 'Todo o histórico');
  assert.equal(rotuloPeriodo(undefined), 'Todo o histórico');
  assert.equal(rotuloPeriodo(''), 'Todo o histórico');
  assert.equal(rotuloPeriodo('   '), 'Todo o histórico');
});

test('mês inválido não vira "Todo o histórico"', () => {
  // Um texto que não é mês não pode ser confundido com "todo o histórico":
  // o formatador devolve o travessão de dado indisponível.
  assert.equal(rotuloPeriodo('2026-13'), '—');
});
