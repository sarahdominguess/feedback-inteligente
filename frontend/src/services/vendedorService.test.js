/**
 * Testes do serviço de vendedores.
 *
 * O cliente HTTP é real, mas o "adapter" é falso: ele registra a requisição
 * que seria enviada e devolve uma resposta pronta. Nenhum teste usa rede.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { AxiosError } from 'axios';

import { criarClienteApi } from './api.js';
import { ErroApi } from './erroApi.js';
import { criarVendedorService } from './vendedorService.js';

const BASE = 'http://localhost:8000';

/**
 * Cria um adapter falso que guarda cada requisição e responde 200.
 *
 * Recebe uma lista (registro) onde as configurações serão acumuladas.
 * Devolve a função adapter no formato que o Axios espera.
 */
function adaptadorQueRegistra(registro, dados = { ok: true }) {
  return (config) => {
    registro.push(config);
    return Promise.resolve({
      status: 200,
      data: dados,
      headers: {},
      config,
    });
  };
}

/**
 * Cria um adapter falso que responde 404 com o corpo de erro da API.
 */
function adaptadorComErro404() {
  return (config) =>
    Promise.reject(
      new AxiosError(
        'Request failed with status code 404',
        'ERR_BAD_REQUEST',
        config,
        null,
        {
          status: 404,
          data: { erro: "Vendedor com ID 'C9999' não encontrado." },
          headers: {},
          config,
        },
      ),
    );
}

test('lista da loja usa GET no caminho certo e sem params por padrão', async () => {
  // Sem mês informado, a URL não deve levar "?mes=".
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);

  await servico.obterVendedoresPorLoja('L004');

  assert.equal(registro.length, 1);
  assert.equal(registro[0].method, 'get');
  assert.equal(registro[0].url, '/api/vendedores/L004');
  assert.equal(registro[0].params, undefined);
});

test('mês informado vira o param mes, sem espaços', async () => {
  // " 2026-10 " é limpo antes de virar parâmetro de consulta.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);

  await servico.obterVendedoresPorLoja('L004', { mes: ' 2026-10 ' });

  assert.deepEqual(registro[0].params, { mes: '2026-10' });
});

test('identificador com espaço nas pontas é aparado no caminho', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);

  await servico.obterVendedoresPorLoja('  L004  ');

  assert.equal(registro[0].url, '/api/vendedores/L004');
});

test('detalhes do vendedor usa o caminho do histórico', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);

  await servico.obterDetalhesVendedor('C0031');

  assert.equal(registro[0].method, 'get');
  assert.equal(registro[0].url, '/api/vendedores/C0031/historico');
});

test('signal é repassado para a chamada (cancelamento funciona)', async () => {
  // AbortController: objeto com um "sinal" usado para cancelar a chamada.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);
  const controlador = new AbortController();

  await servico.obterVendedoresPorLoja('L004', {
    signal: controlador.signal,
  });

  assert.equal(registro[0].signal, controlador.signal);
});

test('identificador vazio, só espaços ou não texto é recusado sem chamar a API', async () => {
  // A validação acontece antes do Axios: o adapter nunca é executado.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);

  const invalidos = ['', '   ', null, undefined, 31];

  for (const valor of invalidos) {
    await assert.rejects(
      servico.obterVendedoresPorLoja(valor),
      (erro) => {
        assert.ok(erro instanceof ErroApi);
        assert.equal(erro.tipo, 'validacao');
        assert.match(erro.message, /código da loja/);
        return true;
      },
    );
  }

  await assert.rejects(
    servico.obterDetalhesVendedor('   '),
    (erro) => erro.tipo === 'validacao',
  );

  assert.equal(registro.length, 0);
});

test('identificador com barra é codificado no caminho', async () => {
  // "L/004" não pode quebrar a URL em dois segmentos.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarVendedorService(cliente);

  await servico.obterVendedoresPorLoja('L/004');

  assert.equal(registro[0].url, '/api/vendedores/L%2F004');
});

test('404 do servidor chega como ErroApi de tipo cliente', async () => {
  // O interceptor do cliente converte a resposta de erro da API.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorComErro404(),
  });
  const servico = criarVendedorService(cliente);

  await assert.rejects(servico.obterDetalhesVendedor('C9999'), (erro) => {
    assert.ok(erro instanceof ErroApi);
    assert.equal(erro.tipo, 'cliente');
    assert.equal(erro.status, 404);
    assert.equal(erro.message, "Vendedor com ID 'C9999' não encontrado.");
    return true;
  });
});
