/**
 * Testes das funções de apoio do seletor de LOJA.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  encontrarLoja,
  iniciaisDaLoja,
  outrasLojas,
} from './seletorLoja.js';

/*
 * Lista pequena no formato da API (os campos que importam aqui são loja_id,
 * loja_nome, gerente_id e gerente_nome).
 */
const LISTA = [
  {
    loja_id: 'L004',
    loja_nome: 'Aurora Shopping Centro',
    gerente_id: 'C0030',
    gerente_nome: 'Diego Furtado',
  },
  {
    loja_id: 'L005',
    loja_nome: 'Aurora Shopping Évora',
    gerente_id: 'C0040',
    gerente_nome: 'Marina Alves',
  },
  {
    loja_id: 'L006',
    loja_nome: 'Aurora Shopping Norte',
    gerente_id: 'C0050',
    gerente_nome: 'Rui Barbosa',
  },
];

// ---------------------------------------------------------------------------
// encontrarLoja
// ---------------------------------------------------------------------------

test('encontra a loja pelo código exato', () => {
  // Devolve o ITEM da lista (não uma cópia), para a tela ler nome e gerente.
  const encontrada = encontrarLoja(LISTA, 'L005');

  assert.equal(encontrada.loja_id, 'L005');
  assert.equal(encontrada.loja_nome, 'Aurora Shopping Évora');
  assert.equal(encontrada.gerente_nome, 'Marina Alves');
});

test('código inexistente devolve null', () => {
  // null é o combinado da função para "não achei".
  assert.equal(encontrarLoja(LISTA, 'L999'), null);
});

test('a comparação do código diferencia maiúsculas de minúsculas', () => {
  // Os códigos da base são maiúsculos; 'l004' não é o mesmo código.
  assert.equal(encontrarLoja(LISTA, 'l004'), null);
});

test('código vazio ou que não é texto devolve null', () => {
  // Evita busca acidental com valor em branco vindo de estado incompleto.
  assert.equal(encontrarLoja(LISTA, ''), null);
  assert.equal(encontrarLoja(LISTA, '   '), null);
  assert.equal(encontrarLoja(LISTA, null), null);
  assert.equal(encontrarLoja(LISTA, undefined), null);
  assert.equal(encontrarLoja(LISTA, 4), null);
});

test('lista vazia ou inválida devolve null, sem quebrar', () => {
  // Se a API mudar o formato, a tela mostra o vazio em vez de dar erro.
  assert.equal(encontrarLoja([], 'L004'), null);
  assert.equal(encontrarLoja(null, 'L004'), null);
  assert.equal(encontrarLoja(undefined, 'L004'), null);
  assert.equal(encontrarLoja({}, 'L004'), null);
});

// ---------------------------------------------------------------------------
// outrasLojas
// ---------------------------------------------------------------------------

test('tira a selecionada e mantém a ordem recebida da API', () => {
  // A ordem da API é a ordem da tela: a função não pode reordenar.
  const resultado = outrasLojas(LISTA, 'L004');

  assert.deepEqual(
    resultado.map((loja) => loja.loja_id),
    ['L005', 'L006'],
  );
});

test('sem seleção válida devolve todas, na mesma ordem', () => {
  // "Ainda não escolhi nenhuma" não pode esconder as lojas.
  for (const semSelecao of [null, undefined, '', '   ']) {
    const resultado = outrasLojas(LISTA, semSelecao);

    assert.deepEqual(
      resultado.map((loja) => loja.loja_id),
      ['L004', 'L005', 'L006'],
    );
  }
});

test('código que não existe na lista devolve todas', () => {
  // Não há loja para tirar, então a lista continua completa.
  const resultado = outrasLojas(LISTA, 'L999');

  assert.equal(resultado.length, 3);
});

test('lista inválida devolve lista vazia', () => {
  assert.deepEqual(outrasLojas(null, 'L004'), []);
  assert.deepEqual(outrasLojas(undefined, 'L004'), []);
  assert.deepEqual(outrasLojas({}, 'L004'), []);
});

test('lista vazia continua vazia', () => {
  assert.deepEqual(outrasLojas([], 'L004'), []);
});

test('não altera a lista recebida e devolve uma lista nova', () => {
  // A lista vem do estado do React: alterá-la embaralharia a tela.
  const copiaDaLista = structuredClone(LISTA);

  const resultado = outrasLojas(LISTA, 'L004');

  // A original ficou intacta...
  assert.deepEqual(LISTA, copiaDaLista);
  // ...e o resultado é outro array (não o mesmo objeto da API).
  assert.notEqual(resultado, LISTA);
});

test('mesmo sem tirar nenhuma, o retorno é um array novo', () => {
  // Assim quem chamar pode mexer no resultado sem afetar o estado original.
  const resultado = outrasLojas(LISTA, null);

  assert.notEqual(resultado, LISTA);
  assert.deepEqual(resultado, LISTA);
});

// ---------------------------------------------------------------------------
// iniciaisDaLoja
// ---------------------------------------------------------------------------

test('ignora "Aurora" e "Shopping" e usa a primeira palavra útil', () => {
  // As duas primeiras palavras são genéricas da rede; "Centro" identifica a loja.
  assert.equal(iniciaisDaLoja('Aurora Shopping Centro'), 'C');
  assert.equal(iniciaisDaLoja('Aurora Shopping Norte'), 'N');
});

test('mantém o acento da letra escolhida', () => {
  // "Évora" começa com É; subir a caixa não pode perder o acento.
  assert.equal(iniciaisDaLoja('Aurora Shopping Évora'), 'É');
});

test('reconhece as palavras genéricas com acento ou minúsculas', () => {
  // "Áurora" e "shopping" também são ignoradas na comparação normalizada.
  assert.equal(iniciaisDaLoja('Áurora shopping Vidal'), 'V');
});

test('nome de uma palavra útil devolve a letra dela', () => {
  assert.equal(iniciaisDaLoja('Centro'), 'C');
  assert.equal(iniciaisDaLoja('  norte  '), 'N');
});

test('nome vazio, só genérico ou que não é texto devolve "?"', () => {
  // "?" evita um círculo em branco quando o dado vier incompleto.
  assert.equal(iniciaisDaLoja(''), '?');
  assert.equal(iniciaisDaLoja('   '), '?');
  assert.equal(iniciaisDaLoja('Aurora Shopping'), '?');
  assert.equal(iniciaisDaLoja(null), '?');
  assert.equal(iniciaisDaLoja(undefined), '?');
  assert.equal(iniciaisDaLoja(123), '?');
  assert.equal(iniciaisDaLoja({}), '?');
});
