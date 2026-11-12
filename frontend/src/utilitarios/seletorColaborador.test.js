/**
 * Testes das funções de apoio do seletor de colaborador.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  encontrarColaborador,
  iniciaisDoNome,
  outrosColaboradores,
} from './seletorColaborador.js';

/*
 * Lista pequena no formato da API (os campos que importam aqui são
 * vendedor_id, nome e cargo). Usada em vários testes abaixo.
 */
const LISTA = [
  { vendedor_id: 'C0031', nome: 'Bianca Rocha', cargo: 'vendedor' },
  { vendedor_id: 'C0032', nome: 'Marcelo Duarte', cargo: 'vendedor' },
  { vendedor_id: 'C0033', nome: 'Tatiane Lopes', cargo: 'vendedor' },
];

// ---------------------------------------------------------------------------
// iniciaisDoNome
// ---------------------------------------------------------------------------

test('nome com duas palavras vira a inicial do primeiro e do último nome', () => {
  // 'Bianca Rocha' → B de Bianca + R de Rocha. É o caso do card da demo.
  assert.equal(iniciaisDoNome('Bianca Rocha'), 'BR');
  assert.equal(iniciaisDoNome('Marcelo Duarte'), 'MD');
});

test('acentos não atrapalham as iniciais', () => {
  // A letra acentuada continua sendo a inicial daquela palavra; só sobe para
  // maiúscula ('Tatiane Lopes' é o caso real da loja).
  assert.equal(iniciaisDoNome('Tatiane Lopes'), 'TL');
  assert.equal(iniciaisDoNome('Íris Conceição'), 'ÍC');
});

test('nome de uma palavra só devolve uma letra', () => {
  // Sem sobrenome, não existe segunda inicial para mostrar.
  assert.equal(iniciaisDoNome('Cher'), 'C');
  assert.equal(iniciaisDoNome('X'), 'X');
});

test('nome com mais de duas palavras usa a primeira e a ÚLTIMA', () => {
  // 'Ana Maria Lima' → A de Ana + L de Lima (o "Maria" do meio é ignorado).
  assert.equal(iniciaisDoNome('Ana Maria Lima'), 'AL');
});

test('espaços extras e letras minúsculas são normalizados', () => {
  // trim + split jogam fora os espaços sobrando; toUpperCase sobe as letras.
  assert.equal(iniciaisDoNome('  bianca   rocha  '), 'BR');
  assert.equal(iniciaisDoNome('marcelo duarte'), 'MD');
});

test('nome vazio, só espaços ou que não é texto devolve "?"', () => {
  // "?" evita um avatar em branco na tela quando o dado vier incompleto.
  assert.equal(iniciaisDoNome(''), '?');
  assert.equal(iniciaisDoNome('   '), '?');
  assert.equal(iniciaisDoNome(null), '?');
  assert.equal(iniciaisDoNome(undefined), '?');
  assert.equal(iniciaisDoNome(123), '?');
  assert.equal(iniciaisDoNome({}), '?');
});

// ---------------------------------------------------------------------------
// encontrarColaborador
// ---------------------------------------------------------------------------

test('encontra o colaborador pelo código exato', () => {
  // Devolve o ITEM da lista (não uma cópia), para a tela ler nome e cargo.
  const encontrado = encontrarColaborador(LISTA, 'C0032');

  assert.equal(encontrado.vendedor_id, 'C0032');
  assert.equal(encontrado.nome, 'Marcelo Duarte');
});

test('código inexistente devolve null', () => {
  // null é o combinado da função para "não achei".
  assert.equal(encontrarColaborador(LISTA, 'C9999'), null);
});

test('a comparação do código diferencia maiúsculas de minúsculas', () => {
  // Os códigos da base são maiúsculos; 'c0031' não é o mesmo código.
  assert.equal(encontrarColaborador(LISTA, 'c0031'), null);
});

test('código vazio ou que não é texto devolve null', () => {
  // Evita busca acidental com valor em branco vindo de estado incompleto.
  assert.equal(encontrarColaborador(LISTA, ''), null);
  assert.equal(encontrarColaborador(LISTA, '   '), null);
  assert.equal(encontrarColaborador(LISTA, null), null);
  assert.equal(encontrarColaborador(LISTA, undefined), null);
  assert.equal(encontrarColaborador(LISTA, 31), null);
});

test('lista inválida devolve null, sem quebrar', () => {
  // Se a API mudar o formato, a tela mostra o vazio em vez de dar erro.
  assert.equal(encontrarColaborador(null, 'C0031'), null);
  assert.equal(encontrarColaborador(undefined, 'C0031'), null);
  assert.equal(encontrarColaborador({}, 'C0031'), null);
  assert.equal(encontrarColaborador([], 'C0031'), null);
});

// ---------------------------------------------------------------------------
// outrosColaboradores
// ---------------------------------------------------------------------------

test('tira o selecionado e mantém a ordem recebida da API', () => {
  // A ordem da API é a ordem da tela: a função não pode reordenar.
  const resultado = outrosColaboradores(LISTA, 'C0031');

  assert.deepEqual(
    resultado.map((colaborador) => colaborador.vendedor_id),
    ['C0032', 'C0033'],
  );
});

test('sem seleção válida devolve todos, na mesma ordem', () => {
  // "Ainda não escolhi ninguém" não pode esconder a equipe.
  for (const semSelecao of [null, undefined, '', '   ']) {
    const resultado = outrosColaboradores(LISTA, semSelecao);

    assert.deepEqual(
      resultado.map((colaborador) => colaborador.vendedor_id),
      ['C0031', 'C0032', 'C0033'],
    );
  }
});

test('código que não existe na lista devolve todos', () => {
  // Não há ninguém para tirar, então a lista continua completa.
  const resultado = outrosColaboradores(LISTA, 'C9999');

  assert.equal(resultado.length, 3);
});

test('lista inválida devolve lista vazia', () => {
  assert.deepEqual(outrosColaboradores(null, 'C0031'), []);
  assert.deepEqual(outrosColaboradores(undefined, 'C0031'), []);
  assert.deepEqual(outrosColaboradores({}, 'C0031'), []);
});

test('lista vazia continua vazia', () => {
  assert.deepEqual(outrosColaboradores([], 'C0031'), []);
});

test('não altera a lista recebida e devolve uma lista nova', () => {
  // A lista vem do estado do React: alterá-la embaralharia a tela.
  const copiaDaLista = structuredClone(LISTA);

  const resultado = outrosColaboradores(LISTA, 'C0031');

  // A original ficou intacta...
  assert.deepEqual(LISTA, copiaDaLista);
  // ...e o resultado é outro array (não o mesmo objeto da API).
  assert.notEqual(resultado, LISTA);
});

test('mesmo sem tirar ninguém, o retorno é um array novo', () => {
  // Assim quem chamar pode mexer no resultado sem afetar o estado original.
  const resultado = outrosColaboradores(LISTA, null);

  assert.notEqual(resultado, LISTA);
  assert.deepEqual(resultado, LISTA);
});
