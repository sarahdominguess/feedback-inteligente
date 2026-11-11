/**
 * Testes do reducer e do estado inicial.
 *
 * Não usam React nem rede: só chamam appReducer com ações e conferem o
 * resultado. É por isso que a lógica do estado vive num arquivo separado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { ABAS, LOJA_PADRAO_ID, STATUS, VISOES } from '../constantes.js';
import { appReducer, criarEstadoInicial, TIPOS } from './appReducer.js';
import { ErroApi } from '../services/erroApi.js';

test('estado inicial tem a forma combinada', () => {
  const estado = criarEstadoInicial();

  assert.deepEqual(estado, {
    lojaId: LOJA_PADRAO_ID,
    visao: VISOES.GERENTE,
    aba: ABAS.DADOS,
    vendedores: { status: STATUS.OCIOSO, dados: [], erro: null },
    vendedorSelecionadoId: null,
    detalhes: { status: STATUS.OCIOSO, dados: null, erro: null },
    feedbacks: {},
    regional: { status: STATUS.OCIOSO, dados: null, erro: null },
  });
});

test('cada estado inicial é uma estrutura nova (sem compartilhar arrays)', () => {
  // Se os objetos fossem compartilhados, mudar um estado afetaria o outro.
  const primeiro = criarEstadoInicial();
  const segundo = criarEstadoInicial();

  assert.notEqual(primeiro, segundo);
  assert.notEqual(primeiro.vendedores, segundo.vendedores);
  assert.notEqual(primeiro.feedbacks, segundo.feedbacks);
});

test('lista de vendedores: carregando, sucesso e erro', () => {
  let estado = criarEstadoInicial();

  estado = appReducer(estado, { tipo: TIPOS.VENDEDORES_CARREGANDO });
  assert.equal(estado.vendedores.status, STATUS.CARREGANDO);
  assert.deepEqual(estado.vendedores.dados, []);
  assert.equal(estado.vendedores.erro, null);

  const lista = [{ vendedor_id: 'C0031', nome: 'Bianca Rocha' }];
  estado = appReducer(estado, {
    tipo: TIPOS.VENDEDORES_SUCESSO,
    dados: lista,
  });
  assert.equal(estado.vendedores.status, STATUS.SUCESSO);
  assert.deepEqual(estado.vendedores.dados, lista);

  estado = appReducer(estado, {
    tipo: TIPOS.VENDEDORES_ERRO,
    erro: new ErroApi('Não foi possível conectar ao servidor.', {
      tipo: 'rede',
    }),
  });
  assert.equal(estado.vendedores.status, STATUS.ERRO);
  // O estado guarda apenas o texto, nunca o objeto de erro inteiro.
  assert.equal(
    estado.vendedores.erro,
    'Não foi possível conectar ao servidor.',
  );
  assert.equal(typeof estado.vendedores.erro, 'string');
});

test('selecionar vendedor reinicia detalhes mas preserva feedbacks', () => {
  let estado = criarEstadoInicial();

  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0031',
  });
  estado = appReducer(estado, {
    tipo: TIPOS.DETALHES_SUCESSO,
    vendedorId: 'C0031',
    dados: { nome: 'Bianca Rocha' },
  });
  estado = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: { feedback_id: 'abc' },
  });

  assert.equal(estado.vendedorSelecionadoId, 'C0031');
  assert.equal(estado.detalhes.status, STATUS.SUCESSO);

  // Trocar de pessoa: histórico volta para ocioso...
  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0032',
  });

  assert.equal(estado.vendedorSelecionadoId, 'C0032');
  assert.deepEqual(estado.detalhes, {
    status: STATUS.OCIOSO,
    dados: null,
    erro: null,
  });

  // ...mas o roteiro já gerado da Bianca continua guardado.
  assert.deepEqual(estado.feedbacks.C0031, {
    status: STATUS.SUCESSO,
    dados: { feedback_id: 'abc' },
    erro: null,
  });
});

test('resposta de detalhes de outro vendedor é ignorada (corrida)', () => {
  // Cenário: a pessoa clicou em C0031 e logo em C0032. A resposta atrasada
  // de C0031 não pode sobrescrever os detalhes de C0032.
  let estado = criarEstadoInicial();
  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0032',
  });

  const antes = structuredClone(estado);

  const acoesAtrasadas = [
    { tipo: TIPOS.DETALHES_CARREGANDO, vendedorId: 'C0031' },
    {
      tipo: TIPOS.DETALHES_SUCESSO,
      vendedorId: 'C0031',
      dados: { nome: 'Bianca Rocha' },
    },
    {
      tipo: TIPOS.DETALHES_ERRO,
      vendedorId: 'C0031',
      erro: new ErroApi('Falhou.', { tipo: 'rede' }),
    },
  ];

  for (const acao of acoesAtrasadas) {
    const resultado = appReducer(estado, acao);
    // Devolve o MESMO estado (nem cria objeto novo), porque a ação é velha.
    assert.equal(resultado, estado);
  }

  assert.deepEqual(estado, antes);
});

test('feedbacks são guardados por vendedor e não se misturam', () => {
  let estado = criarEstadoInicial();

  estado = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: { feedback_id: 'da-bianca' },
  });
  estado = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0032',
    dados: { feedback_id: 'da-ana' },
  });
  estado = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_ERRO,
    vendedorId: 'C0033',
    erro: new ErroApi('A IA está indisponível.', { tipo: 'servidor' }),
  });

  assert.equal(estado.feedbacks.C0031.dados.feedback_id, 'da-bianca');
  assert.equal(estado.feedbacks.C0032.dados.feedback_id, 'da-ana');
  assert.equal(estado.feedbacks.C0033.status, STATUS.ERRO);
  assert.equal(estado.feedbacks.C0033.erro, 'A IA está indisponível.');

  // Carregar de novo um vendedor não mexe nos outros.
  estado = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_CARREGANDO,
    vendedorId: 'C0031',
  });
  assert.equal(estado.feedbacks.C0031.status, STATUS.CARREGANDO);
  assert.equal(estado.feedbacks.C0032.status, STATUS.SUCESSO);
});

test('aba e visão aceitam só valores conhecidos', () => {
  let estado = criarEstadoInicial();

  estado = appReducer(estado, { tipo: TIPOS.MUDAR_ABA, aba: ABAS.FEEDBACK });
  assert.equal(estado.aba, ABAS.FEEDBACK);

  estado = appReducer(estado, {
    tipo: TIPOS.MUDAR_VISAO,
    visao: VISOES.REGIONAL,
  });
  assert.equal(estado.visao, VISOES.REGIONAL);

  // Valores inventados devolvem o mesmo estado, sem alteração.
  const anterior = estado;
  assert.equal(
    appReducer(estado, { tipo: TIPOS.MUDAR_ABA, aba: 'financeiro' }),
    anterior,
  );
  assert.equal(
    appReducer(estado, { tipo: TIPOS.MUDAR_VISAO, visao: 'admin' }),
    anterior,
  );
});

test('todas as abas e visões previstas são aceitas', () => {
  let estado = criarEstadoInicial();

  for (const aba of Object.values(ABAS)) {
    estado = appReducer(estado, { tipo: TIPOS.MUDAR_ABA, aba });
    assert.equal(estado.aba, aba);
  }

  for (const visao of Object.values(VISOES)) {
    estado = appReducer(estado, { tipo: TIPOS.MUDAR_VISAO, visao });
    assert.equal(estado.visao, visao);
  }
});

test('o reducer não altera o estado recebido (imutabilidade)', () => {
  const estado = criarEstadoInicial();
  const copia = structuredClone(estado);

  const proximo = appReducer(estado, {
    tipo: TIPOS.VENDEDORES_SUCESSO,
    dados: [{ vendedor_id: 'C0031' }],
  });

  // O estado antigo permanece exatamente como estava...
  assert.deepEqual(estado, copia);
  // ...e o novo é outro objeto, inclusive na parte que mudou.
  assert.notEqual(proximo, estado);
  assert.notEqual(proximo.vendedores, estado.vendedores);
});

test('o mapa de feedbacks também é copiado, sem mutar o anterior', () => {
  let estado = criarEstadoInicial();
  estado = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: { feedback_id: 'antes' },
  });

  const anterior = structuredClone(estado);

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0032',
    dados: { feedback_id: 'depois' },
  });

  assert.deepEqual(estado, anterior);
  assert.notEqual(proximo.feedbacks, estado.feedbacks);
  assert.equal(proximo.feedbacks.C0031.dados.feedback_id, 'antes');
});

test('ação desconhecida devolve o mesmo estado', () => {
  const estado = criarEstadoInicial();

  const resultado = appReducer(estado, { tipo: 'acao/inexistente' });

  assert.equal(resultado, estado);
});

test('erro sem mensagem util vira texto genérico', () => {
  // Nunca deixamos "undefined" aparecer na tela.
  const estado = appReducer(criarEstadoInicial(), {
    tipo: TIPOS.VENDEDORES_ERRO,
    erro: {},
  });

  assert.equal(estado.vendedores.erro, 'Não foi possível concluir a operação.');
});
