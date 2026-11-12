/**
 * Testes do serviço de anotações.
 *
 * O cliente HTTP é o real, mas o "adapter" (a peça que conversa com a rede) é
 * falso: ele registra a requisição que seria enviada e devolve uma resposta
 * pronta. Nenhum teste usa rede de verdade.
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { AxiosError } from 'axios';

import { criarClienteApi } from './api.js';
import { criarAnotacaoService } from './anotacaoService.js';
import { ErroApi } from './erroApi.js';

const BASE = 'http://localhost:8000';

// Resposta que o backend devolve quando grava uma anotação (AnotacaoDTO).
const ANOTACAO_GRAVADA = {
  data: '2026-11-12',
  sobre: 'Bianca Rocha',
  texto: 'cliente elogiou o caixa',
  e_do_time: false,
};

/**
 * Cria um adapter falso que guarda cada requisição e responde 201.
 *
 * Recebe a lista onde as configurações serão acumuladas e os dados que a
 * resposta deve conter. Devolve a função adapter no formato do Axios.
 */
function adaptadorQueRegistra(registro, dados = ANOTACAO_GRAVADA) {
  return (config) => {
    registro.push(config);
    return Promise.resolve({
      // 201 = "criado", o status que o backend usa nesta rota.
      status: 201,
      data: dados,
      headers: {},
      config,
    });
  };
}

/**
 * Cria um adapter falso que responde com erro da API.
 *
 * Recebe o status (400 ou 404) e a mensagem em português que viria no campo
 * "erro". Devolve a função adapter que rejeita como o Axios faz.
 */
function adaptadorComErro(status, mensagem) {
  return (config) =>
    Promise.reject(
      new AxiosError(
        `Request failed with status code ${status}`,
        'ERR_BAD_REQUEST',
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
 * Lê o corpo enviado na requisição.
 *
 * O Axios transforma o objeto em texto JSON antes de entregar ao adapter;
 * esta função aceita os dois casos para o teste não depender desse detalhe.
 */
function corpoEnviado(config) {
  return typeof config.data === 'string' ? JSON.parse(config.data) : config.data;
}

test('envia POST no caminho do vendedor com o corpo { texto }', async () => {
  // A rota é a do backend: /api/vendedores/{id}/anotacoes, método POST.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  await servico.registrarAnotacao('C0031', 'cliente elogiou o caixa');

  assert.equal(registro.length, 1);
  assert.equal(registro[0].method, 'post');
  assert.equal(registro[0].url, '/api/vendedores/C0031/anotacoes');

  // O corpo leva SÓ o texto: data e "sobre" são decisão do backend.
  assert.deepEqual(corpoEnviado(registro[0]), {
    texto: 'cliente elogiou o caixa',
  });
});

test('tira os espaços das pontas do texto antes de enviar', async () => {
  // O que a pessoa digita pode vir cercado de espaços sem querer.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  await servico.registrarAnotacao('C0031', '   texto com espaços   ');

  assert.equal(corpoEnviado(registro[0]).texto, 'texto com espaços');
});

test('preserva as quebras de linha do meio do texto', async () => {
  // Só as pontas são limpas: o miolo é o que a pessoa escreveu.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  await servico.registrarAnotacao(
    'C0031',
    '\n  primeira linha\nsegunda linha  \n',
  );

  assert.equal(
    corpoEnviado(registro[0]).texto,
    'primeira linha\nsegunda linha',
  );
});

test('identificador com barra é codificado no caminho', async () => {
  // "C/0031" não pode quebrar a URL em dois segmentos.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  await servico.registrarAnotacao('C/0031', 'texto');

  assert.equal(registro[0].url, '/api/vendedores/C%2F0031/anotacoes');
});

test('signal é repassado para a chamada (cancelamento funciona)', async () => {
  // AbortSignal: o "sinal" de um AbortController, usado para cancelar a
  // chamada em andamento (ex.: a pessoa trocou de tela).
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);
  const controlador = new AbortController();

  await servico.registrarAnotacao('C0031', 'texto', {
    signal: controlador.signal,
  });

  assert.equal(registro[0].signal, controlador.signal);
});

test('devolve o corpo da resposta sem transformar', async () => {
  // O serviço entrega direto o AnotacaoDTO que a API devolveu.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  const resultado = await servico.registrarAnotacao('C0031', 'texto');

  assert.deepEqual(resultado, ANOTACAO_GRAVADA);
});

test('vendedor inválido é recusado sem chamar a API', async () => {
  // A validação acontece antes do Axios: o adapter nunca é executado.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  const invalidos = ['', '   ', null, undefined, 31];

  for (const valor of invalidos) {
    await assert.rejects(
      servico.registrarAnotacao(valor, 'texto válido'),
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

test('texto vazio, só espaços ou não texto é recusado sem chamar a API', async () => {
  // O backend validaria de novo, mas não vale a pena gastar uma requisição.
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarAnotacaoService(cliente);

  const invalidos = ['', '   \n\t ', null, undefined, 123];

  for (const valor of invalidos) {
    await assert.rejects(
      servico.registrarAnotacao('C0031', valor),
      (erro) => {
        assert.ok(erro instanceof ErroApi);
        assert.equal(erro.tipo, 'validacao');
        return true;
      },
    );
  }

  assert.equal(registro.length, 0);
});

test('400 do servidor chega como ErroApi com a mensagem do backend', async () => {
  // O interceptor do cliente converte a resposta de erro da API em ErroApi.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorComErro(400, 'texto: texto muito curto'),
  });
  const servico = criarAnotacaoService(cliente);

  await assert.rejects(
    servico.registrarAnotacao('C0031', 'texto'),
    (erro) => {
      assert.ok(erro instanceof ErroApi);
      assert.equal(erro.tipo, 'cliente');
      assert.equal(erro.status, 400);
      assert.equal(erro.message, 'texto: texto muito curto');
      return true;
    },
  );
});

test('404 do servidor chega como ErroApi com a mensagem do backend', async () => {
  // Vendedor inexistente: a mensagem pronta do backend é o que a tela mostra.
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorComErro(
      404,
      "Vendedor com ID 'C9999' não encontrado.",
    ),
  });
  const servico = criarAnotacaoService(cliente);

  await assert.rejects(
    servico.registrarAnotacao('C9999', 'texto'),
    (erro) => {
      assert.ok(erro instanceof ErroApi);
      assert.equal(erro.tipo, 'cliente');
      assert.equal(erro.status, 404);
      assert.equal(
        erro.message,
        "Vendedor com ID 'C9999' não encontrado.",
      );
      return true;
    },
  );
});
