/**
 * Testes do mapeamento situação → tom do selo.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica por que aquele tom é o esperado para a situação.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { tomDaSituacao } from './tomDaSituacao.js';

test('situação "acima" usa tom positivo', () => {
  // Acima da média do time é um bom sinal: tom positivo (verde de sucesso).
  assert.equal(tomDaSituacao('acima'), 'positivo');
});

test('situação "abaixo" usa tom de atenção, não de erro', () => {
  // Abaixo da média é um ponto de desenvolvimento para a conversa, não uma
  // falha. Por isso "atencao" e não "negativo".
  assert.equal(tomDaSituacao('abaixo'), 'atencao');
});

test('"na_media" e "indisponivel" usam tom neutro', () => {
  // Na média não é bom nem ruim; sem dados não há o que destacar. Os dois
  // ficam no tom discreto.
  assert.equal(tomDaSituacao('na_media'), 'neutro');
  assert.equal(tomDaSituacao('indisponivel'), 'neutro');
});

test('situação desconhecida vira neutro', () => {
  // Se a API mandar um texto novo (ou nada), a tela não deve inventar alerta
  // nem quebrar: cai no tom mais discreto.
  assert.equal(tomDaSituacao('situacao_nova'), 'neutro');
  assert.equal(tomDaSituacao(''), 'neutro');
  assert.equal(tomDaSituacao(null), 'neutro');
  assert.equal(tomDaSituacao(undefined), 'neutro');
  assert.equal(tomDaSituacao(42), 'neutro');
});
