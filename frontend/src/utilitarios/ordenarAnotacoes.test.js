/**
 * Testes da ordenação de anotações.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { ordenarAnotacoes } from './ordenarAnotacoes.js';

test('lista vazia continua vazia', () => {
  // Sem anotações não há o que ordenar; a função devolve uma lista vazia.
  assert.deepEqual(ordenarAnotacoes([]), []);
});

test('ordena da data mais recente para a mais antiga', () => {
  // A entrada está fora de ordem de propósito; a saída deve começar em
  // 2026-10-08 e terminar em 2026-08-06.
  const entrada = [
    { data: '2026-09-02', texto: 'setembro' },
    { data: '2026-10-08', texto: 'outubro' },
    { data: '2026-08-06', texto: 'agosto' },
  ];

  const resultado = ordenarAnotacoes(entrada);

  assert.deepEqual(
    resultado.map((anotacao) => anotacao.data),
    ['2026-10-08', '2026-09-02', '2026-08-06'],
  );
});

test('datas iguais mantêm a ordem em que chegaram', () => {
  // A ordenação é estável: no empate, vale a posição original da lista.
  const entrada = [
    { data: '2026-10-01', texto: 'primeira da lista' },
    { data: '2026-10-01', texto: 'segunda da lista' },
    { data: '2026-10-01', texto: 'terceira da lista' },
  ];

  const resultado = ordenarAnotacoes(entrada);

  assert.deepEqual(
    resultado.map((anotacao) => anotacao.texto),
    ['primeira da lista', 'segunda da lista', 'terceira da lista'],
  );
});

test('não altera a lista recebida e devolve uma lista nova', () => {
  // Quem chamou pode continuar usando a lista original como estava, e a
  // função nunca deve "embaralhar" o estado do React por acidente.
  const entrada = [
    { data: '2026-08-06', texto: 'mais antiga' },
    { data: '2026-10-08', texto: 'mais recente' },
  ];
  const copiaDaEntrada = structuredClone(entrada);

  const resultado = ordenarAnotacoes(entrada);

  assert.deepEqual(entrada, copiaDaEntrada);
  assert.notEqual(resultado, entrada);
});

test('entrada que não é lista devolve lista vazia', () => {
  // Proteção simples: se a API mudar o formato, a página mostra o vazio em
  // vez de quebrar.
  assert.deepEqual(ordenarAnotacoes(null), []);
  assert.deepEqual(ordenarAnotacoes(undefined), []);
  assert.deepEqual(ordenarAnotacoes({}), []);
});
