/**
 * Testes do cliente HTTP central e da normalização de erros.
 *
 * Usam o executor de testes que já vem no Node (node:test), sem biblioteca
 * extra. As chamadas NÃO vão para a internet: cada teste passa um "adapter"
 * falso, que é a peça do Axios que faria a requisição de verdade.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { AxiosError } from 'axios';

import { criarClienteApi } from './api.js';
import {
  ErroApi,
  erroFoiCancelamento,
  normalizarErro,
  TIPOS_ERRO,
} from './erroApi.js';

const BASE = 'http://localhost:8000';

/**
 * Monta o objeto de resposta que o Axios espera receber do adapter.
 *
 * Recebe o config da chamada, o status HTTP e os dados (já em objeto).
 */
function respostaFalsa(config, status, data) {
  return { status, data, headers: {}, config };
}

/**
 * Adapter falso que sempre responde com sucesso (status 2xx).
 */
function adaptadorQueResponde(data, status = 200) {
  return (config) => Promise.resolve(respostaFalsa(config, status, data));
}

/**
 * Adapter falso que sempre falha com uma resposta HTTP de erro.
 *
 * O Axios de verdade rejeita a promessa quando o status não é 2xx; por isso
 * aqui também rejeitamos com um AxiosError contendo a resposta.
 */
function adaptadorQueFalha(status, data) {
  return (config) =>
    Promise.reject(
      new AxiosError(
        `Request failed with status code ${status}`,
        status >= 500 ? 'ERR_BAD_RESPONSE' : 'ERR_BAD_REQUEST',
        config,
        null,
        respostaFalsa(config, status, data),
      ),
    );
}

/**
 * Adapter falso que falha sem resposta, como quando o servidor está desligado
 * (ERR_NETWORK) ou o tempo estourou (ECONNABORTED).
 */
function adaptadorSemResposta(codigo) {
  return (config) =>
    Promise.reject(new AxiosError('Falha simulada', codigo, config, null));
}

test('sucesso entrega somente os dados da resposta', async () => {
  // O interceptor deve "abrir" o envelope do Axios e devolver resposta.data.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueResponde({ status: 'ok' }),
  });

  const dados = await cliente.get('/health');

  assert.deepEqual(dados, { status: 'ok' });
});

test('404 com campo erro vira ErroApi de tipo cliente', async () => {
  // A API devolve {"erro": "..."} quando a loja não existe; a mensagem
  // precisa chegar igual para a tela mostrar.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueFalha(404, {
      erro: "Loja 'L999' não encontrada.",
    }),
  });

  await assert.rejects(cliente.get('/api/vendedores/L999'), (erro) => {
    assert.ok(erro instanceof ErroApi);
    assert.equal(erro.tipo, 'cliente');
    assert.equal(erro.status, 404);
    assert.equal(erro.message, "Loja 'L999' não encontrada.");
    return true;
  });
});

test('400 com campo erro também vira tipo cliente', async () => {
  // Entrada inválida (ex.: mês fora de AAAA-MM) chega como 400.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueFalha(400, { erro: 'mes: formato inválido' }),
  });

  await assert.rejects(cliente.get('/api/vendedores/L004'), (erro) => {
    assert.equal(erro.tipo, 'cliente');
    assert.equal(erro.status, 400);
    assert.equal(erro.message, 'mes: formato inválido');
    return true;
  });
});

test('500 sem campo erro usa mensagem genérica de servidor', async () => {
  // Se a resposta não tem {"erro": ...}, não inventamos detalhes: usamos
  // uma mensagem genérica, mas mantemos o tipo e o status.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueFalha(500, { detalhe: 'stack interno' }),
  });

  await assert.rejects(cliente.get('/api/regional/desempenho-gerente'), (erro) => {
    assert.equal(erro.tipo, 'servidor');
    assert.equal(erro.status, 500);
    assert.equal(
      erro.message,
      'O servidor encontrou um erro. Tente novamente em instantes.',
    );
    return true;
  });
});

test('503 com campo erro vira tipo servidor com a mensagem da API', async () => {
  // IA indisponível: a API responde 503 com texto pronto.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueFalha(503, {
      erro: 'Serviço de IA indisponível.',
    }),
  });

  await assert.rejects(cliente.post('/api/feedback/gerar'), (erro) => {
    assert.equal(erro.tipo, 'servidor');
    assert.equal(erro.status, 503);
    assert.equal(erro.message, 'Serviço de IA indisponível.');
    return true;
  });
});

test('servidor inacessível vira tipo rede', async () => {
  // Sem resposta e com cara de erro do Axios: backend desligado.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorSemResposta('ERR_NETWORK'),
  });

  await assert.rejects(cliente.get('/health'), (erro) => {
    assert.equal(erro.tipo, 'rede');
    assert.equal(erro.status, null);
    assert.equal(
      erro.message,
      'Não foi possível conectar ao servidor. Verifique se o backend está rodando.',
    );
    return true;
  });
});

test('código ECONNABORTED vira tipo tempo_esgotado', async () => {
  // O Axios usa esse código quando o timeout configurado estoura.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorSemResposta('ECONNABORTED'),
  });

  await assert.rejects(cliente.get('/api/vendedores/L004'), (erro) => {
    assert.equal(erro.tipo, 'tempo_esgotado');
    assert.equal(
      erro.message,
      'A resposta demorou mais do que o esperado. Tente novamente.',
    );
    return true;
  });
});

test('cancelamento com AbortController vira tipo cancelada', async () => {
  // AbortController: um "botão de cancelar" ligado a um sinal. Abortamos
  // antes da chamada para o Axios nem executar o adapter.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueResponde({ nunca: 'chega' }),
  });

  const controlador = new AbortController();
  controlador.abort();

  await assert.rejects(
    cliente.get('/api/vendedores/L004', {
      signal: controlador.signal,
    }),
    (erro) => {
      assert.equal(erro.tipo, 'cancelada');
      assert.equal(erroFoiCancelamento(erro), true);
      return true;
    },
  );
});

test('baseURL perde barras sobrando no final', async () => {
  // Sem isso, a URL final teria "//" entre a base e o caminho.
  const cliente = criarClienteApi({ baseURL: 'http://localhost:8000///' });

  assert.equal(cliente.defaults.baseURL, BASE);
});

test('ErroApi não carrega URL, cabeçalhos, config nem resposta bruta', async () => {
  // Regra de segurança: o erro exposto para a interface não pode vazar
  // detalhes internos da requisição ou da resposta.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueFalha(404, {
      erro: 'Não encontrado.',
      segredo: 'não deve aparecer',
    }),
  });

  await assert.rejects(cliente.get('/qualquer'), (erro) => {
    const proibidas = ['url', 'headers', 'config', 'request', 'response'];
    for (const chave of proibidas) {
      assert.equal(chave in erro, false, `não deveria ter "${chave}"`);
    }
    assert.equal(JSON.stringify(erro).includes('segredo'), false);
    return true;
  });
});

test('normalizarErro devolve o mesmo objeto quando já é ErroApi', () => {
  // Converter duas vezes não deve criar um erro novo.
  const original = new ErroApi('Falha conhecida.', { tipo: 'cliente' });

  assert.equal(normalizarErro(original), original);
});

test('a lista de tipos de erro tem exatamente os sete previstos', () => {
  // Mudar essa lista sem atualizar as telas quebraria o tratamento.
  assert.deepEqual(TIPOS_ERRO, [
    'rede',
    'tempo_esgotado',
    'cliente',
    'servidor',
    'cancelada',
    'validacao',
    'desconhecido',
  ]);
});
