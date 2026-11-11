/**
 * Testes das funções de apoio da aba Dados.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  acharComparativo,
  montarDetalheComparativo,
  textoPosicao,
} from './dadosDoVendedor.js';

// Lista parecida com a que a API devolve em detalhes.dados.comparativo.
const COMPARATIVO = [
  {
    nome: 'ticket_medio',
    valor: 150.2,
    media_time: 210,
    posicao: 7,
    total_vendedores: 8,
    situacao: 'abaixo',
  },
  {
    nome: 'conversao',
    valor: 0.62,
    media_time: 0.5,
    posicao: 1,
    total_vendedores: 8,
    situacao: 'acima',
  },
];

test('acharComparativo encontra a métrica pelo nome técnico', () => {
  // "conversao" existe na lista; a função deve devolver o objeto inteiro.
  const item = acharComparativo(COMPARATIVO, 'conversao');

  assert.equal(item.nome, 'conversao');
  assert.equal(item.situacao, 'acima');
});

test('acharComparativo devolve null quando a métrica não está na lista', () => {
  // "pecas_por_atendimento" não foi incluída: o cartão deve ficar sem selo,
  // sem quebrar a página.
  assert.equal(acharComparativo(COMPARATIVO, 'pecas_por_atendimento'), null);
});

test('acharComparativo devolve null para entrada que não é lista', () => {
  // Se a API mudar o formato (ou mandar null), a tela não pode quebrar.
  assert.equal(acharComparativo(null, 'conversao'), null);
  assert.equal(acharComparativo(undefined, 'conversao'), null);
  assert.equal(acharComparativo({}, 'conversao'), null);
});

test('textoPosicao monta "Posição X de Y" com números válidos', () => {
  // posicao 1 = melhor; total 8 = oito vendedores no time.
  assert.equal(
    textoPosicao({ posicao: 3, total_vendedores: 8 }),
    'Posição 3 de 8',
  );
});

test('textoPosicao devolve vazio quando não há posição válida', () => {
  // null (fora do ranking), zero, ausência ou texto não viram posição.
  assert.equal(textoPosicao({ posicao: null, total_vendedores: 8 }), '');
  assert.equal(textoPosicao({ posicao: 0, total_vendedores: 8 }), '');
  assert.equal(textoPosicao({ posicao: 3, total_vendedores: 0 }), '');
  assert.equal(textoPosicao({ posicao: 3 }), '');
  assert.equal(textoPosicao({ posicao: '3', total_vendedores: 8 }), '');
  assert.equal(textoPosicao(null), '');
});

test('montarDetalheComparativo junta média e posição com um separador', () => {
  // O cartão mostra as duas informações na mesma linha de detalhe.
  assert.equal(
    montarDetalheComparativo(
      { posicao: 3, total_vendedores: 8 },
      'R$ 210,00',
    ),
    'Média do time: R$ 210,00 · Posição 3 de 8',
  );
});

test('montarDetalheComparativo mostra só a média quando não há posição', () => {
  // Sem posição, não sobra separador solto no fim do texto.
  assert.equal(
    montarDetalheComparativo(
      { posicao: null, total_vendedores: 8 },
      '32,5%',
    ),
    'Média do time: 32,5%',
  );
});

test('montarDetalheComparativo devolve vazio sem item do comparativo', () => {
  // Sem item, o CartaoIndicador fica sem a linha de detalhe.
  assert.equal(montarDetalheComparativo(null, 'R$ 210,00'), '');
});

test('montarDetalheComparativo usa travessão quando a média não é texto', () => {
  // A média chega já formatada; se algo vier vazio, o app mostra "—" em vez
  // de "undefined" na tela.
  assert.equal(
    montarDetalheComparativo({ posicao: null }, undefined),
    'Média do time: —',
  );
});
