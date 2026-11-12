/**
 * Testes do agrupamento de anotações por dia.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { agruparPorDia } from './agruparPorDia.js';

test('lista vazia devolve nenhum grupo', () => {
  // Sem anotações não há dia para separar.
  assert.deepEqual(agruparPorDia([]), []);
});

test('um único dia vira um grupo com todos os itens', () => {
  // Duas anotações no mesmo dia ficam juntas, na ordem recebida.
  const entrada = [
    { data: '2026-10-08', texto: 'primeira' },
    { data: '2026-10-08', texto: 'segunda' },
  ];

  const grupos = agruparPorDia(entrada);

  assert.equal(grupos.length, 1);
  assert.equal(grupos[0].data, '2026-10-08');
  assert.deepEqual(
    grupos[0].itens.map((anotacao) => anotacao.texto),
    ['primeira', 'segunda'],
  );
});

test('vários dias viram grupos separados, na ordem da lista', () => {
  // A função recebe a lista JÁ ordenada (a ordenação é da outra função).
  const entrada = [
    { data: '2026-08-06', texto: 'a' },
    { data: '2026-08-06', texto: 'b' },
    { data: '2026-09-15', texto: 'c' },
    { data: '2026-10-08', texto: 'd' },
  ];

  const grupos = agruparPorDia(entrada);

  assert.deepEqual(
    grupos.map((grupo) => grupo.data),
    ['2026-08-06', '2026-09-15', '2026-10-08'],
  );
  assert.deepEqual(
    grupos.map((grupo) => grupo.itens.length),
    [2, 1, 1],
  );
});

test('não altera a lista recebida', () => {
  // Os grupos e as listas internas são estruturas novas.
  const entrada = [
    { data: '2026-08-06', texto: 'a' },
    { data: '2026-09-15', texto: 'b' },
  ];
  const copiaDaEntrada = structuredClone(entrada);

  const grupos = agruparPorDia(entrada);

  assert.deepEqual(entrada, copiaDaEntrada);
  // Mexer no grupo não pode mexer na entrada.
  grupos[0].itens.push({ data: '2026-08-06', texto: 'inventada' });
  assert.equal(entrada.length, 2);
});

test('entrada que não é lista devolve nenhum grupo', () => {
  // Proteção simples: se a API mudar o formato, a tela mostra o vazio.
  assert.deepEqual(agruparPorDia(null), []);
  assert.deepEqual(agruparPorDia(undefined), []);
  assert.deepEqual(agruparPorDia({}), []);
});

test('anotação sem data válida entra num grupo sem dia', () => {
  // Decisão: o texto escrito pela pessoa não pode sumir só porque a data
  // veio estranha. Ele fica num grupo com data "" e a tela mostra "—".
  const entrada = [
    { data: '2026-08-06', texto: 'com data' },
    { texto: 'sem data' },
  ];

  const grupos = agruparPorDia(entrada);

  assert.deepEqual(
    grupos.map((grupo) => grupo.data),
    ['2026-08-06', ''],
  );
  assert.equal(grupos[1].itens[0].texto, 'sem data');
});
