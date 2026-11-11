/**
 * Testes das opções do seletor de período.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { montarOpcoesDePeriodo } from './opcoesDePeriodo.js';

test('sem meses, só existe a opção "Todo o histórico"', () => {
  // Sem histórico mensal não há mês para escolher; o padrão é o histórico
  // inteiro (valor vazio).
  const { opcoes, valorPadrao } = montarOpcoesDePeriodo([]);

  assert.deepEqual(opcoes, [{ valor: '', rotulo: 'Todo o histórico' }]);
  assert.equal(valorPadrao, '');
});

test('só mês parcial não é pré-selecionado', () => {
  // Mês em andamento não serve como padrão (os números ainda vão mudar);
  // ele aparece na lista com o aviso "(parcial)".
  const { opcoes, valorPadrao } = montarOpcoesDePeriodo([
    { mes: '2026-11', mes_parcial: true },
  ]);

  assert.deepEqual(opcoes, [
    { valor: '', rotulo: 'Todo o histórico' },
    { valor: '2026-11', rotulo: 'novembro de 2026 (parcial)' },
  ]);
  assert.equal(valorPadrao, '');
});

test('vários meses com o último parcial elegem o último completo', () => {
  // Novembro está em andamento; o padrão deve ser o último mês completo,
  // outubro, e não o último item da lista.
  const { opcoes, valorPadrao } = montarOpcoesDePeriodo([
    { mes: '2026-08', mes_parcial: false },
    { mes: '2026-09', mes_parcial: false },
    { mes: '2026-10', mes_parcial: false },
    { mes: '2026-11', mes_parcial: true },
  ]);

  assert.equal(valorPadrao, '2026-10');

  // A ordem recebida é preservada, e os rótulos saem por extenso.
  assert.deepEqual(
    opcoes.map((opcao) => opcao.rotulo),
    [
      'Todo o histórico',
      'agosto de 2026',
      'setembro de 2026',
      'outubro de 2026',
      'novembro de 2026 (parcial)',
    ],
  );
});

test('com todos os meses completos, o padrão é o último da lista', () => {
  // Sem nenhum mês parcial, o último item da ordem cronológica é o padrão.
  const { valorPadrao } = montarOpcoesDePeriodo([
    { mes: '2026-09', mes_parcial: false },
    { mes: '2026-10', mes_parcial: false },
  ]);

  assert.equal(valorPadrao, '2026-10');
});

test('entrada inválida não quebra e cai em "Todo o histórico"', () => {
  // Formato inesperado, itens nulos ou mês que não é texto são ignorados.
  const entradasInvalidas = [
    null,
    undefined,
    {},
    'outubro',
    [null, {}, { mes: 123 }, { mes: '' }],
  ];

  for (const entrada of entradasInvalidas) {
    const { opcoes, valorPadrao } = montarOpcoesDePeriodo(entrada);

    assert.deepEqual(opcoes, [{ valor: '', rotulo: 'Todo o histórico' }]);
    assert.equal(valorPadrao, '');
  }
});
