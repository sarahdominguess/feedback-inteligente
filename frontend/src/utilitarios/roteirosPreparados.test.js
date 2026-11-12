/**
 * Testes das funções de apoio dos roteiros preparados.
 *
 * Rodam no Node puro (node --test), sem navegador e sem rede. Cada teste
 * explica o que verifica e por que aquele resultado é o esperado.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import {
  descricaoDoRoteiroPreparado,
  incluirNoInicio,
  itemPreparadoDeResposta,
  roteiroTemConteudo,
  tituloDoRoteiroPreparado,
} from './roteirosPreparados.js';

/**
 * Roteiro completo, com as quatro listas — o formato que a API devolve.
 * A lista vazia é válida: a IA pode não ter sugerido nada numa seção.
 */
function roteiroCompleto() {
  return {
    pontos_positivos: ['Bom atendimento'],
    pontos_melhoria: ['Oferecer mais peças'],
    possiveis_motivos: ['Correria no sábado'],
    roteiro_conversa: ['Como foi o sábado?'],
  };
}

// ---------------------------------------------------------------------------
// tituloDoRoteiroPreparado
// ---------------------------------------------------------------------------

test('título usa o período no formato "mês de ano"', () => {
  // O mesmo rótulo usado no resto do app: outubro de 2026.
  assert.equal(
    tituloDoRoteiroPreparado({ mes_referencia: '2026-10' }),
    'outubro de 2026',
  );
});

test('título com período null diz "Todo o histórico"', () => {
  // null é como a API diz que a geração olhou o histórico inteiro.
  assert.equal(
    tituloDoRoteiroPreparado({ mes_referencia: null }),
    'Todo o histórico',
  );
});

test('título de item sem o campo mes_referencia também é "Todo o histórico"', () => {
  // Campo ausente se comporta como null no JavaScript.
  assert.equal(tituloDoRoteiroPreparado({}), 'Todo o histórico');
});

test('título com mês inválido vira "—"', () => {
  // Melhor mostrar que o dado veio errado do que fingir que era o histórico.
  assert.equal(tituloDoRoteiroPreparado({ mes_referencia: '2026-13' }), '—');
});

test('título de item inválido vira "—"', () => {
  for (const invalido of [null, undefined, 'texto', 42]) {
    assert.equal(tituloDoRoteiroPreparado(invalido), '—');
  }
});

// ---------------------------------------------------------------------------
// descricaoDoRoteiroPreparado
// ---------------------------------------------------------------------------

test('descrição mostra quando o roteiro foi gerado', () => {
  // O formato vem de formatarDataHora: "DD/MM/AAAA às HH:MM".
  assert.equal(
    descricaoDoRoteiroPreparado({ gerado_em: '2026-11-11T14:30:00' }),
    'Gerado em 11/11/2026 às 14:30',
  );
});

test('descrição aceita data com fuso no fim', () => {
  // O backend manda a data em ISO; "Z" e "+00:00" significam o mesmo horário.
  assert.equal(
    descricaoDoRoteiroPreparado({ gerado_em: '2026-11-11T14:30:00Z' }),
    'Gerado em 11/11/2026 às 14:30',
  );
  assert.equal(
    descricaoDoRoteiroPreparado({
      gerado_em: '2026-11-11T14:30:00+00:00',
    }),
    'Gerado em 11/11/2026 às 14:30',
  );
});

test('descrição sem data válida diz "Data indisponível"', () => {
  // Nunca mostramos "null", "undefined" ou um traço solto no lugar da frase.
  assert.equal(
    descricaoDoRoteiroPreparado({ gerado_em: 'ontem' }),
    'Data indisponível',
  );
  assert.equal(descricaoDoRoteiroPreparado({}), 'Data indisponível');
  assert.equal(descricaoDoRoteiroPreparado(null), 'Data indisponível');
});

// ---------------------------------------------------------------------------
// roteiroTemConteudo
// ---------------------------------------------------------------------------

test('roteiro com as quatro listas tem conteúdo', () => {
  assert.equal(roteiroTemConteudo({ roteiro: roteiroCompleto() }), true);
});

test('listas vazias continuam valendo como conteúdo', () => {
  // A IA pode não sugerir nada numa seção; o roteiro continua completo.
  const roteiro = {
    pontos_positivos: [],
    pontos_melhoria: [],
    possiveis_motivos: [],
    roteiro_conversa: [],
  };

  assert.equal(roteiroTemConteudo({ roteiro }), true);
});

test('roteiro sem uma das listas não tem conteúdo', () => {
  // Basta faltar uma chave para a tela não conseguir desenhar os 4 cards.
  const roteiro = roteiroCompleto();
  delete roteiro.roteiro_conversa;

  assert.equal(roteiroTemConteudo({ roteiro }), false);
});

test('lista que não é array invalida o conteúdo', () => {
  const roteiro = { ...roteiroCompleto(), pontos_melhoria: 'texto' };

  assert.equal(roteiroTemConteudo({ roteiro }), false);
});

test('item sem roteiro ou inválido não tem conteúdo', () => {
  assert.equal(roteiroTemConteudo({}), false);
  assert.equal(roteiroTemConteudo({ roteiro: null }), false);
  assert.equal(roteiroTemConteudo(null), false);
  assert.equal(roteiroTemConteudo('texto'), false);
});

// ---------------------------------------------------------------------------
// itemPreparadoDeResposta
// ---------------------------------------------------------------------------

test('resposta do POST vira um item da lista', () => {
  // Só os quatro campos usados na lista; nada a mais, nada a menos.
  const resposta = {
    feedback_id: 'abc-123',
    vendedor_id: 'C0031',
    vendedor_nome: 'Bianca Rocha',
    mes_referencia: '2026-10',
    gerado_em: '2026-11-11T14:30:00Z',
    roteiro: roteiroCompleto(),
  };

  const item = itemPreparadoDeResposta(resposta);

  assert.deepEqual(Object.keys(item).sort(), [
    'feedback_id',
    'gerado_em',
    'mes_referencia',
    'roteiro',
  ]);
  assert.equal(item.feedback_id, 'abc-123');
  assert.equal(item.mes_referencia, '2026-10');
  assert.deepEqual(item.roteiro, roteiroCompleto());
});

test('resposta sem mês vira item com mes_referencia null', () => {
  // Assim o item fica igual aos que vêm do histórico.
  const item = itemPreparadoDeResposta({
    feedback_id: 'abc-123',
    gerado_em: '2026-11-11T14:30:00Z',
    roteiro: roteiroCompleto(),
  });

  assert.equal(item.mes_referencia, null);
});

test('resposta sem feedback_id vira null', () => {
  // Sem identificador não dá para saber qual item substituir na lista.
  assert.equal(itemPreparadoDeResposta({ roteiro: roteiroCompleto() }), null);
  assert.equal(
    itemPreparadoDeResposta({
      feedback_id: '   ',
      roteiro: roteiroCompleto(),
    }),
    null,
  );
});

test('resposta sem roteiro válido vira null', () => {
  assert.equal(
    itemPreparadoDeResposta({ feedback_id: 'abc-123', roteiro: {} }),
    null,
  );
  assert.equal(itemPreparadoDeResposta(null), null);
});

// ---------------------------------------------------------------------------
// incluirNoInicio
// ---------------------------------------------------------------------------

test('item novo entra no início e a lista original fica intacta', () => {
  // A lista é imutável: quem tem a referência antiga continua com ela.
  const lista = [
    { feedback_id: 'antigo-1' },
    { feedback_id: 'antigo-2' },
  ];
  const copiaDaLista = structuredClone(lista);

  const nova = incluirNoInicio(lista, { feedback_id: 'novo' });

  assert.deepEqual(
    nova.map((item) => item.feedback_id),
    ['novo', 'antigo-1', 'antigo-2'],
  );
  assert.deepEqual(lista, copiaDaLista);
  assert.notEqual(nova, lista);
});

test('item com o mesmo feedback_id substitui o antigo, sem duplicar', () => {
  // É o caso de reenviar o mesmo roteiro: não pode aparecer duas vezes.
  const lista = [{ feedback_id: 'abc', roteiro: 'velho' }];

  const nova = incluirNoInicio(lista, {
    feedback_id: 'abc',
    roteiro: 'novo',
  });

  assert.equal(nova.length, 1);
  assert.equal(nova[0].roteiro, 'novo');
});

test('lista inválida vira uma lista só com o item', () => {
  // Proteção simples: se o estado vier estranho, a tela não quebra.
  assert.deepEqual(incluirNoInicio(null, { feedback_id: 'novo' }), [
    { feedback_id: 'novo' },
  ]);
  assert.deepEqual(incluirNoInicio(undefined, { feedback_id: 'novo' }), [
    { feedback_id: 'novo' },
  ]);
});

test('item inválido devolve uma cópia da lista', () => {
  // Nada é acrescentado e o array devolvido é novo.
  const lista = [{ feedback_id: 'antigo' }];

  const nova = incluirNoInicio(lista, null);

  assert.deepEqual(nova, lista);
  assert.notEqual(nova, lista);
});

test('lista vazia recebe o item novo', () => {
  assert.deepEqual(incluirNoInicio([], { feedback_id: 'novo' }), [
    { feedback_id: 'novo' },
  ]);
});

test('item sem feedback_id é acrescentado sem remover ninguém', () => {
  // Sem identificador não há como comparar; nada é substituído.
  const lista = [{ feedback_id: 'antigo' }];

  const nova = incluirNoInicio(lista, { roteiro: 'sem id' });

  assert.equal(nova.length, 2);
  assert.equal(nova[0].roteiro, 'sem id');
  assert.equal(nova[1].feedback_id, 'antigo');
});
