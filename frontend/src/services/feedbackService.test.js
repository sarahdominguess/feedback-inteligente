/**
 * Testes do serviço de geração de feedback.
 *
 * Todo teste usa um adapter falso: nenhuma chamada de rede e nenhum crédito
 * de IA são gastos. O adapter registra a configuração da requisição para
 * conferirmos corpo, caminho, timeout e signal.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { AxiosError } from 'axios';

import { criarClienteApi } from './api.js';
import { ErroApi } from './erroApi.js';
import {
  criarFeedbackService,
  TIMEOUT_GERACAO_MS,
} from './feedbackService.js';

const BASE = 'http://localhost:8000';

/**
 * Adapter falso que guarda a requisição e responde 200 com dados prontos.
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
 * Adapter falso que responde com um erro HTTP da API.
 *
 * Recebe o status e a mensagem que o backend devolveria em {"erro": ...}.
 */
function adaptadorComErro(status, mensagem) {
  return (config) =>
    Promise.reject(
      new AxiosError(
        `Request failed with status code ${status}`,
        status >= 500 ? 'ERR_BAD_RESPONSE' : 'ERR_BAD_REQUEST',
        config,
        null,
        {
          status,
          data: { erro: mensagem },
          headers: {},
          config,
        },
      ),
    );
}

/**
 * Cria cliente e serviço com o adapter informado.
 */
function criarServico(adapter) {
  const cliente = criarClienteApi({ baseURL: BASE, adapter });
  return { cliente, servico: criarFeedbackService(cliente) };
}

test('corpo sem mês tem apenas vendedor_id (snake_case)', async () => {
  // O nome no JavaScript é camelCase (mesReferencia), mas o JSON enviado
  // precisa usar o nome do backend (mes_referencia). Sem mês, a chave nem
  // aparece no corpo.
  const registro = [];
  const { servico } = criarServico(adaptadorQueRegistra(registro));

  await servico.gerarFeedback('C0031');

  const corpo = JSON.parse(registro[0].data);
  assert.deepEqual(corpo, { vendedor_id: 'C0031' });
  assert.equal('mes_referencia' in corpo, false);
});

test('mês informado entra como mes_referencia, sem espaços', async () => {
  const registro = [];
  const { servico } = criarServico(adaptadorQueRegistra(registro));

  await servico.gerarFeedback('C0031', { mesReferencia: ' 2026-10 ' });

  const corpo = JSON.parse(registro[0].data);
  assert.deepEqual(corpo, {
    vendedor_id: 'C0031',
    mes_referencia: '2026-10',
  });
});

test('usa POST no caminho da geração', async () => {
  const registro = [];
  const { servico } = criarServico(adaptadorQueRegistra(registro));

  await servico.gerarFeedback('C0031');

  assert.equal(registro[0].method, 'post');
  assert.equal(registro[0].url, '/api/feedback/gerar');
});

test('timeout da geração é 150000 e não muda o padrão do cliente', async () => {
  // A geração espera até 150 s (duas chamadas de IA + validação). As demais
  // chamadas continuam com o padrão de 20 s.
  const registro = [];
  const { cliente, servico } = criarServico(adaptadorQueRegistra(registro));

  await servico.gerarFeedback('C0031');
  await cliente.get('/health');

  assert.equal(TIMEOUT_GERACAO_MS, 150000);
  assert.equal(registro[0].timeout, 150000);
  assert.equal(registro[1].timeout, 20000);
  assert.equal(cliente.defaults.timeout, 20000);
});

test('signal é repassado para a chamada', async () => {
  const registro = [];
  const { servico } = criarServico(adaptadorQueRegistra(registro));
  const controlador = new AbortController();

  await servico.gerarFeedback('C0031', {
    signal: controlador.signal,
  });

  assert.equal(registro[0].signal, controlador.signal);
});

test('vendedorId inválido é recusado sem chamar a API', async () => {
  // A validação local evita gastar uma chamada de IA com pedido inválido.
  const registro = [];
  const { servico } = criarServico(adaptadorQueRegistra(registro));

  for (const valor of ['', '   ', null, undefined, 31]) {
    await assert.rejects(
      servico.gerarFeedback(valor),
      (erro) => {
        assert.ok(erro instanceof ErroApi);
        assert.equal(erro.tipo, 'validacao');
        assert.match(erro.message, /código do vendedor/);
        return true;
      },
    );
  }

  assert.equal(registro.length, 0);
});

test('erros do backend chegam como ErroApi com tipo e mensagem certos', async () => {
  // 400/404 são "cliente"; 500/502/503 são "servidor". A mensagem é sempre a
  // que o backend devolveu em {"erro": ...}.
  const casos = [
    [400, 'cliente', 'mes_referencia: formato inválido'],
    [404, 'cliente', "Vendedor com ID 'C9999' não encontrado."],
    [500, 'servidor', 'O serviço de IA não está configurado no servidor.'],
    [502, 'servidor', 'A IA devolveu uma resposta inválida.'],
    [503, 'servidor', 'Serviço de IA indisponível.'],
  ];

  for (const [status, tipo, mensagem] of casos) {
    const { servico } = criarServico(adaptadorComErro(status, mensagem));

    await assert.rejects(
      servico.gerarFeedback('C0031'),
      (erro) => {
        assert.ok(erro instanceof ErroApi, `status ${status}`);
        assert.equal(erro.tipo, tipo, `status ${status}`);
        assert.equal(erro.status, status);
        assert.equal(erro.message, mensagem);
        return true;
      },
    );
  }
});

test('falha faz uma única chamada, sem retry automático', async () => {
  // Sem retry: repetir sozinho gastaria créditos de IA sem a pessoa pedir.
  let chamadas = 0;
  const adapter = (config) => {
    chamadas += 1;
    return adaptadorComErro(503, 'Serviço de IA indisponível.')(config);
  };
  const { servico } = criarServico(adapter);

  await assert.rejects(servico.gerarFeedback('C0031'));

  assert.equal(chamadas, 1);
});
