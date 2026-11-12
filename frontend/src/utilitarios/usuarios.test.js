/**
 * Testes das funções de apoio do menu de usuário.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { USUARIOS, VISOES } from '../constantes.js';
import { outrosUsuarios, usuarioDaVisao } from './usuarios.js';

test('visão do gerente devolve o Diego', () => {
  // A visão inicial do app é a do gerente, então esse é o caso mais comum.
  const usuario = usuarioDaVisao(VISOES.GERENTE);

  assert.equal(usuario.nome, 'Diego');
  assert.equal(usuario.cargo, 'Gerente');
});

test('visão regional devolve a Patrícia', () => {
  const usuario = usuarioDaVisao(VISOES.REGIONAL);

  assert.equal(usuario.nome, 'Patrícia');
  assert.equal(usuario.cargo, 'Regional');
});

test('visão desconhecida devolve o primeiro usuário da lista', () => {
  // Melhor mostrar Diego do que deixar o canto do cabeçalho vazio.
  for (const invalida of ['financeiro', '', null, undefined]) {
    assert.equal(usuarioDaVisao(invalida).nome, 'Diego');
  }
});

test('outros usuários excluem quem está na visão atual', () => {
  // Só existe uma opção no menu: a outra pessoa.
  const outrosDoGerente = outrosUsuarios(VISOES.GERENTE);
  const outrosDaRegional = outrosUsuarios(VISOES.REGIONAL);

  assert.deepEqual(
    outrosDoGerente.map((usuario) => usuario.nome),
    ['Patrícia'],
  );
  assert.deepEqual(
    outrosDaRegional.map((usuario) => usuario.nome),
    ['Diego'],
  );
});

test('visão desconhecida devolve todos os usuários', () => {
  // Nenhum deles está em uso, então todos podem ser escolhidos.
  assert.equal(outrosUsuarios('financeiro').length, USUARIOS.length);
});

test('a lista original de usuários não é alterada', () => {
  // As funções devolvem listas novas; a constante do projeto fica intacta.
  const antes = structuredClone(USUARIOS);

  const resultado = outrosUsuarios(VISOES.GERENTE);
  resultado.push({ visao: 'inventado', nome: 'Teste', cargo: 'Teste' });

  assert.deepEqual(USUARIOS, antes);
  assert.notEqual(resultado, USUARIOS);
});

test('o usuário devolvido é o próprio item da constante', () => {
  // Não criamos cópias: o menu só lê nome e cargo.
  assert.equal(usuarioDaVisao(VISOES.REGIONAL), USUARIOS[1]);
});
