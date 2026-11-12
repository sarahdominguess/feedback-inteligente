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
    // O app abre na aba Feedback: é o fluxo principal do gerente.
    aba: ABAS.FEEDBACK,
    vendedores: { status: STATUS.OCIOSO, dados: [], erro: null },
    vendedorSelecionadoId: null,
    detalhes: { status: STATUS.OCIOSO, dados: null, erro: null },
    feedbacks: {},
    // O envio de anotação começa parado, sem erro.
    novaAnotacao: { status: STATUS.OCIOSO, erro: null },
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

// ---------------------------------------------------------------------------
// Anotação nova (aba Anotações)
// ---------------------------------------------------------------------------

/**
 * Monta um estado com o histórico da Bianca já carregado.
 *
 * Recebe a lista de anotações que o histórico deve conter (por padrão, uma
 * anotação "antiga" do CSV) e devolve o estado pronto, com a Bianca
 * selecionada e os detalhes em sucesso.
 */
function estadoComHistorico(
  anotacoes = [{ data: '2026-10-08', sobre: 'Bianca Rocha', texto: 'antiga' }],
) {
  let estado = criarEstadoInicial();

  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0031',
  });
  estado = appReducer(estado, {
    tipo: TIPOS.DETALHES_SUCESSO,
    vendedorId: 'C0031',
    dados: { nome: 'Bianca Rocha', anotacoes },
  });

  return estado;
}

// Anotação no formato que a API devolve (AnotacaoDTO).
const ANOTACAO_NOVA = {
  data: '2026-11-12',
  sobre: 'Bianca Rocha',
  texto: 'cliente elogiou o caixa',
  e_do_time: false,
};

test('envio de anotação: começa ocioso e vai para carregando', () => {
  // O formulário precisa saber que o pedido está em andamento.
  const inicial = criarEstadoInicial();
  assert.deepEqual(inicial.novaAnotacao, {
    status: STATUS.OCIOSO,
    erro: null,
  });

  const enviando = appReducer(inicial, { tipo: TIPOS.ANOTACAO_ENVIANDO });

  assert.equal(enviando.novaAnotacao.status, STATUS.CARREGANDO);
  assert.equal(enviando.novaAnotacao.erro, null);
});

test('envio de anotação: limpa o erro anterior ao tentar de novo', () => {
  // Se a tentativa anterior falhou, o aviso não pode ficar na tela enquanto
  // a nova tentativa acontece.
  let estado = appReducer(criarEstadoInicial(), {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0031',
  });
  estado = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_ERRO,
    vendedorId: 'C0031',
    erro: new ErroApi('A anotação não foi salva.', { tipo: 'rede' }),
  });
  assert.equal(estado.novaAnotacao.status, STATUS.ERRO);

  estado = appReducer(estado, { tipo: TIPOS.ANOTACAO_ENVIANDO });

  assert.equal(estado.novaAnotacao.status, STATUS.CARREGANDO);
  assert.equal(estado.novaAnotacao.erro, null);
});

test('sucesso acrescenta a anotação NO FIM e não altera o estado anterior', () => {
  // A lista do histórico é copiada: o React precisa de uma referência nova,
  // e o estado antigo tem de continuar intacto.
  const estado = estadoComHistorico();
  const antes = structuredClone(estado);

  const proximo = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_SUCESSO,
    vendedorId: 'C0031',
    dados: ANOTACAO_NOVA,
  });

  assert.equal(proximo.novaAnotacao.status, STATUS.SUCESSO);
  assert.equal(proximo.novaAnotacao.erro, null);

  // Duas anotações: a antiga e a nova, nesta ordem.
  assert.equal(proximo.detalhes.dados.anotacoes.length, 2);
  assert.equal(
    proximo.detalhes.dados.anotacoes[0].texto,
    'antiga',
  );
  assert.deepEqual(proximo.detalhes.dados.anotacoes[1], ANOTACAO_NOVA);

  // O estado recebido não muda e a lista é outro array.
  assert.deepEqual(estado, antes);
  assert.notEqual(
    proximo.detalhes.dados.anotacoes,
    estado.detalhes.dados.anotacoes,
  );
});

test('sucesso de outro vendedor é ignorado (resposta antiga)', () => {
  // A pessoa trocou de colaborador no meio do envio: a resposta que chega
  // depois não pode mexer no histórico de quem está na tela agora.
  const estado = estadoComHistorico();

  const resultado = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_SUCESSO,
    vendedorId: 'C0032',
    dados: ANOTACAO_NOVA,
  });

  // Devolve o MESMO estado, sem criar objeto novo.
  assert.equal(resultado, estado);
});

test('sucesso sem histórico carregado não quebra e ainda marca sucesso', () => {
  // Decisão: a anotação FOI gravada no servidor; sem uma lista onde
  // acrescentar, registramos sucesso mesmo assim (marcar erro seria mentira).
  // Ela aparece quando o histórico for carregado.
  let estado = criarEstadoInicial();
  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0031',
  });

  const proximo = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_SUCESSO,
    vendedorId: 'C0031',
    dados: ANOTACAO_NOVA,
  });

  assert.equal(proximo.novaAnotacao.status, STATUS.SUCESSO);
  assert.equal(proximo.detalhes.dados, null);
});

test('erro do envio guarda só o texto, nunca o objeto de erro', () => {
  // O estado é serializável e a tela só precisa de uma frase pronta.
  const estado = estadoComHistorico();

  const proximo = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_ERRO,
    vendedorId: 'C0031',
    erro: new ErroApi('Não foi possível conectar ao servidor.', {
      tipo: 'rede',
    }),
  });

  assert.equal(proximo.novaAnotacao.status, STATUS.ERRO);
  assert.equal(
    proximo.novaAnotacao.erro,
    'Não foi possível conectar ao servidor.',
  );
  assert.equal(typeof proximo.novaAnotacao.erro, 'string');
});

test('erro de outro vendedor é ignorado (resposta antiga)', () => {
  // Mesma proteção do sucesso: o aviso não é sobre a pessoa da tela.
  const estado = estadoComHistorico();

  const resultado = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_ERRO,
    vendedorId: 'C0032',
    erro: new ErroApi('Falhou.', { tipo: 'rede' }),
  });

  assert.equal(resultado, estado);
});

test('trocar de vendedor limpa o estado do envio de anotação', () => {
  // Um "enviando" ou um erro da pessoa anterior não pode aparecer na tela
  // da próxima.
  let estado = estadoComHistorico();
  estado = appReducer(estado, {
    tipo: TIPOS.ANOTACAO_ERRO,
    vendedorId: 'C0031',
    erro: new ErroApi('Falhou.', { tipo: 'rede' }),
  });

  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0032',
  });

  assert.deepEqual(estado.novaAnotacao, {
    status: STATUS.OCIOSO,
    erro: null,
  });
});

// ---------------------------------------------------------------------------
// Feedback novo entrando na lista de roteiros preparados
// ---------------------------------------------------------------------------

/**
 * Monta um estado com o histórico da Bianca carregado.
 *
 * Diferente do helper de anotações, aqui os detalhes trazem "vendedor_id" —
 * é esse campo que o reducer usa para saber de quem é a lista de roteiros
 * preparados. Recebe os itens que a lista já deve conter.
 */
function estadoComPreparados(itens = []) {
  let estado = criarEstadoInicial();

  estado = appReducer(estado, {
    tipo: TIPOS.SELECIONAR_VENDEDOR,
    vendedorId: 'C0031',
  });
  estado = appReducer(estado, {
    tipo: TIPOS.DETALHES_SUCESSO,
    vendedorId: 'C0031',
    dados: {
      vendedor_id: 'C0031',
      nome: 'Bianca Rocha',
      anotacoes: [],
      feedbacks_preparados: itens,
    },
  });

  return estado;
}

/**
 * Resposta da geração de feedback, no formato da API (FeedbackGerarResposta).
 */
function respostaGerada(extra = {}) {
  return {
    feedback_id: 'novo-id',
    vendedor_id: 'C0031',
    vendedor_nome: 'Bianca Rocha',
    mes_referencia: '2026-10',
    gerado_em: '2026-11-12T14:00:00Z',
    roteiro: {
      pontos_positivos: ['Bom atendimento'],
      pontos_melhoria: ['Oferecer mais peças'],
      possiveis_motivos: ['Correria no sábado'],
      roteiro_conversa: ['Como foi o sábado?'],
    },
    ...extra,
  };
}

test('geração com sucesso põe o roteiro novo no INÍCIO dos preparados', () => {
  // A lista mostra o mais recente primeiro; os antigos continuam lá.
  const estado = estadoComPreparados([
    { feedback_id: 'antigo-1' },
    { feedback_id: 'antigo-2' },
  ]);

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: respostaGerada(),
  });

  const preparados = proximo.detalhes.dados.feedbacks_preparados;

  assert.equal(preparados.length, 3);
  assert.equal(preparados[0].feedback_id, 'novo-id');
  assert.equal(preparados[1].feedback_id, 'antigo-1');
  assert.equal(preparados[2].feedback_id, 'antigo-2');

  // O item novo tem só os quatro campos da lista, com o roteiro completo.
  assert.deepEqual(Object.keys(preparados[0]).sort(), [
    'feedback_id',
    'gerado_em',
    'mes_referencia',
    'roteiro',
  ]);
  assert.deepEqual(
    preparados[0].roteiro.pontos_positivos,
    ['Bom atendimento'],
  );
});

test('a geração continua guardando o roteiro em estado.feedbacks', () => {
  // O painel de destaque da aba usa esse pedaço do estado; ele não pode
  // deixar de ser preenchido só porque a lista também mudou.
  const estado = estadoComPreparados();

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: respostaGerada(),
  });

  assert.equal(proximo.feedbacks.C0031.status, STATUS.SUCESSO);
  assert.equal(proximo.feedbacks.C0031.dados.feedback_id, 'novo-id');
});

test('geração repetida com o mesmo feedback_id não duplica o item', () => {
  // Reenviar/atualizar o mesmo roteiro não pode criar duas linhas iguais.
  let estado = estadoComPreparados([{ feedback_id: 'antigo-1' }]);

  const acao = {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: respostaGerada(),
  };

  estado = appReducer(estado, acao);
  estado = appReducer(estado, acao);

  const preparados = estado.detalhes.dados.feedbacks_preparados;

  assert.equal(preparados.length, 2);
  assert.equal(preparados[0].feedback_id, 'novo-id');
  assert.equal(preparados[1].feedback_id, 'antigo-1');
});

test('geração de OUTRA pessoa não mexe nos detalhes da tela', () => {
  // Resposta atrasada de uma troca de colaborador: o histórico na tela é da
  // Bianca, então nada nele pode mudar.
  const estado = estadoComPreparados([{ feedback_id: 'antigo-1' }]);

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0032',
    dados: respostaGerada({ feedback_id: 'de-outra-pessoa' }),
  });

  // O objeto de detalhes continua sendo o MESMO.
  assert.equal(proximo.detalhes, estado.detalhes);
  // Mas o roteiro da outra pessoa fica guardado no mapa dela.
  assert.equal(
    proximo.feedbacks.C0032.dados.feedback_id,
    'de-outra-pessoa',
  );
});

test('geração sem histórico carregado não quebra e guarda o feedback', () => {
  // Cenário: os detalhes ainda não chegaram. Não há lista para atualizar,
  // mas o roteiro precisa ficar guardado para a tela mostrar.
  const estado = criarEstadoInicial();

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: respostaGerada(),
  });

  assert.equal(proximo.detalhes, estado.detalhes);
  assert.equal(proximo.feedbacks.C0031.status, STATUS.SUCESSO);
});

test('resposta sem roteiro válido não mexe nos detalhes', () => {
  // Se a API devolver algo incompleto, a lista fica como estava; o roteiro
  // ainda é guardado (a tela de destaque mostra o que veio).
  const estado = estadoComPreparados([{ feedback_id: 'antigo-1' }]);

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: respostaGerada({ roteiro: { pontos_positivos: [] } }),
  });

  assert.equal(proximo.detalhes, estado.detalhes);
  assert.equal(proximo.feedbacks.C0031.status, STATUS.SUCESSO);
});

test('o estado anterior não é alterado ao incluir o roteiro novo', () => {
  // Estado imutável: quem guarda a referência antiga continua com ela.
  const estado = estadoComPreparados([{ feedback_id: 'antigo-1' }]);
  const antes = structuredClone(estado);

  const proximo = appReducer(estado, {
    tipo: TIPOS.FEEDBACK_SUCESSO,
    vendedorId: 'C0031',
    dados: respostaGerada(),
  });

  assert.deepEqual(estado, antes);
  assert.notEqual(proximo, estado);
  assert.notEqual(proximo.detalhes, estado.detalhes);
  assert.notEqual(
    proximo.detalhes.dados.feedbacks_preparados,
    estado.detalhes.dados.feedbacks_preparados,
  );
});
