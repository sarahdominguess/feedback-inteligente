/**
 * Testes do serviço da visão regional.
 *
 * Usa um adapter falso para conferir o caminho, o método e o repasse do
 * signal, sem nenhuma chamada de rede.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { AxiosError } from 'axios';

import { criarClienteApi } from './api.js';
import { ErroApi } from './erroApi.js';
import { criarRegionalService } from './regionalService.js';

const BASE = 'http://localhost:8000';

/**
 * Adapter falso que guarda a requisição e responde 200 com os dados dados.
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

test('desempenho usa GET no caminho da regional', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarRegionalService(cliente);

  const dados = await servico.obterDesempenhoGerente();

  assert.deepEqual(dados, { ok: true });
  assert.equal(registro.length, 1);
  assert.equal(registro[0].method, 'get');
  assert.equal(registro[0].url, '/api/regional/desempenho-gerente');
  assert.equal(registro[0].params, undefined);
});

test('signal é repassado para a chamada', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarRegionalService(cliente);
  const controlador = new AbortController();

  await servico.obterDesempenhoGerente({ signal: controlador.signal });

  assert.equal(registro[0].signal, controlador.signal);
});

test('erro 500 do servidor chega como ErroApi de tipo servidor', async () => {
  // A mensagem vinda da API precisa ser preservada.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: (config) =>
      Promise.reject(
        new AxiosError(
          'Request failed with status code 500',
          'ERR_BAD_RESPONSE',
          config,
          null,
          {
            status: 500,
            data: {
              erro: 'Não foi possível carregar os dados necessários.',
            },
            headers: {},
            config,
          },
        ),
      ),
  });
  const servico = criarRegionalService(cliente);

  await assert.rejects(servico.obterDesempenhoGerente(), (erro) => {
    assert.ok(erro instanceof ErroApi);
    assert.equal(erro.tipo, 'servidor');
    assert.equal(erro.status, 500);
    assert.equal(
      erro.message,
      'Não foi possível carregar os dados necessários.',
    );
    return true;
  });
});
