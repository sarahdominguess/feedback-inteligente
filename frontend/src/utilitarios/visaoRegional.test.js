/**
 * Testes das funções da visão regional.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  seloDoAtingimento,
  textoPeriodo,
  tomDoAcompanhamento,
} from './visaoRegional.js';

test('atingimento acima de 1 gera selo "Meta batida" positivo', () => {
  // 1.12 = 112% da meta, que o backend já calculou.
  assert.deepEqual(seloDoAtingimento(1.12), {
    texto: 'Meta batida',
    tom: 'positivo',
  });
});

test('atingimento exatamente 1 também é "Meta batida"', () => {
  // A regra é maior OU IGUAL a 1: bater 100% conta como meta batida.
  assert.deepEqual(seloDoAtingimento(1), {
    texto: 'Meta batida',
    tom: 'positivo',
  });
});

test('atingimento abaixo de 1 gera selo de atenção', () => {
  // 0.8 = 80% da meta. É atenção, não erro: é um ponto para a conversa.
  assert.deepEqual(seloDoAtingimento(0.8), {
    texto: 'Abaixo da meta',
    tom: 'atencao',
  });
});

test('atingimento ausente ou inválido não gera selo', () => {
  // null/undefined = a API não tinha meta; NaN = conta inválida;
  // "1" é texto, não número. Nenhum vira selo.
  for (const valor of [null, undefined, Number.NaN, '1']) {
    assert.equal(seloDoAtingimento(valor), null);
  }
});

test('situação de acompanhamento vira tom positivo ou de atenção', () => {
  // Quem tem roteiro preparado aparece em tom positivo; quem não tem, em
  // atenção (um lembrete, não uma falha).
  assert.equal(tomDoAcompanhamento('com_roteiro'), 'positivo');
  assert.equal(tomDoAcompanhamento('sem_roteiro'), 'atencao');
});

test('situação de acompanhamento desconhecida vira neutro', () => {
  // Se a API inventar um valor novo, a tela não cria alerta sozinha.
  assert.equal(tomDoAcompanhamento('outra_coisa'), 'neutro');
  assert.equal(tomDoAcompanhamento(null), 'neutro');
  assert.equal(tomDoAcompanhamento(undefined), 'neutro');
});

test('período com início e fim vira "data a data"', () => {
  assert.equal(
    textoPeriodo('2026-08-01', '2026-11-01'),
    '01/08/2026 a 01/11/2026',
  );
});

test('período só com início começa com "A partir de"', () => {
  // A API manda null quando o período não foi limitado de um dos lados.
  assert.equal(textoPeriodo('2026-08-01', null), 'A partir de 01/08/2026');
});

test('período só com fim termina com "Até"', () => {
  assert.equal(textoPeriodo(null, '2026-11-01'), 'Até 01/11/2026');
});

test('período sem datas válidas é explicado em texto', () => {
  // Nenhuma data ou data malformada: o formatador devolve "—" e a função
  // troca isso por uma frase clara.
  assert.equal(textoPeriodo(null, null), 'Período não informado');
  assert.equal(textoPeriodo('', ''), 'Período não informado');
  assert.equal(textoPeriodo('2026-13-01', '2026-11-01'), 'Até 01/11/2026');
});
