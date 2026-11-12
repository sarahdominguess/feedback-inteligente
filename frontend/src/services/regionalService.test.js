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
import { TIMEOUT_GERACAO_MS } from './feedbackService.js';
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

// ---------------------------------------------------------------------------
// Rotas por loja (Etapa 8)
// ---------------------------------------------------------------------------

test('listar lojas usa GET no caminho novo e repassa o signal', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro, { lojas: [] }),
  });
  const servico = criarRegionalService(cliente);
  const controlador = new AbortController();

  const dados = await servico.listarLojas({ signal: controlador.signal });

  assert.deepEqual(dados, { lojas: [] });
  assert.equal(registro[0].method, 'get');
  assert.equal(registro[0].url, '/api/regional/lojas');
  assert.equal(registro[0].signal, controlador.signal);
});

test('histórico da loja usa GET, protege o id e repassa o signal', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro, { loja_id: 'L004' }),
  });
  const servico = criarRegionalService(cliente);
  const controlador = new AbortController();

  const dados = await servico.obterHistoricoLoja(' L/004 ', {
    signal: controlador.signal,
  });

  assert.deepEqual(dados, { loja_id: 'L004' });
  assert.equal(registro[0].method, 'get');
  // O espaço das pontas saiu e a barra virou %2F (não quebra a URL).
  assert.equal(
    registro[0].url,
    '/api/regional/lojas/L%2F004/historico',
  );
  assert.equal(registro[0].signal, controlador.signal);
});

test('histórico sem loja falha na validação e não chama a rede', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarRegionalService(cliente);

  for (const lojaId of ['', '   ', 123]) {
    await assert.rejects(
      servico.obterHistoricoLoja(lojaId),
      (erro) => {
        assert.ok(erro instanceof ErroApi);
        assert.equal(erro.tipo, 'validacao');
        return true;
      },
    );
  }

  assert.deepEqual(registro, []);
});

test('anotação da regional usa POST com o texto aparado', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro, {
      data: '2026-11-12',
      autora: 'Patrícia Lemos',
      texto: 'visitar a loja',
    }),
  });
  const servico = criarRegionalService(cliente);
  const controlador = new AbortController();

  const dados = await servico.registrarAnotacaoRegional(
    ' L004 ',
    '  visitar a loja  ',
    { signal: controlador.signal },
  );

  assert.equal(dados.autora, 'Patrícia Lemos');
  assert.equal(registro[0].method, 'post');
  assert.equal(registro[0].url, '/api/regional/lojas/L004/anotacoes');
  assert.deepEqual(registro[0].data, JSON.stringify({ texto: 'visitar a loja' }));
  assert.equal(registro[0].signal, controlador.signal);
});

test('anotação da regional recusa texto inválido antes da rede', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarRegionalService(cliente);

  const casos = [
    ['', 'Escreva alguma coisa antes de salvar a anotação.'],
    ['   ', 'Escreva alguma coisa antes de salvar a anotação.'],
    [123, 'Escreva a anotação como texto.'],
  ];

  for (const [texto, mensagem] of casos) {
    await assert.rejects(
      servico.registrarAnotacaoRegional('L004', texto),
      (erro) => {
        assert.ok(erro instanceof ErroApi);
        assert.equal(erro.tipo, 'validacao');
        assert.equal(erro.message, mensagem);
        return true;
      },
    );
  }

  assert.deepEqual(registro, []);
});

test('geração para o gerente usa o caminho novo e o timeout longo', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro, { feedback_id: 'abc' }),
  });
  const servico = criarRegionalService(cliente);
  const controlador = new AbortController();

  const dados = await servico.gerarFeedbackRegional('L004', {
    signal: controlador.signal,
  });

  assert.deepEqual(dados, { feedback_id: 'abc' });
  assert.equal(registro[0].method, 'post');
  assert.equal(registro[0].url, '/api/regional/feedback/gerar');
  // Sem mês, o corpo leva SÓ a loja.
  assert.deepEqual(registro[0].data, JSON.stringify({ loja_id: 'L004' }));
  assert.equal(registro[0].signal, controlador.signal);
  assert.equal(registro[0].timeout, TIMEOUT_GERACAO_MS);
});

test('geração para o gerente inclui o mês só quando informado', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarRegionalService(cliente);

  await servico.gerarFeedbackRegional('L004', {
    mesReferencia: ' 2026-10 ',
  });
  await servico.gerarFeedbackRegional('L004', { mesReferencia: '   ' });

  assert.deepEqual(registro[0].data, JSON.stringify({
    loja_id: 'L004',
    mes_referencia: '2026-10',
  }));
  // Mês vazio é o mesmo que não informado.
  assert.deepEqual(registro[1].data, JSON.stringify({ loja_id: 'L004' }));
});

test('geração para o gerente sem loja falha na validação', async () => {
  const registro = [];
  const cliente = criarClienteApi({
    baseURL: BASE,
    adapter: adaptadorQueRegistra(registro),
  });
  const servico = criarRegionalService(cliente);

  await assert.rejects(
    servico.gerarFeedbackRegional('   '),
    (erro) => {
      assert.ok(erro instanceof ErroApi);
      assert.equal(erro.tipo, 'validacao');
      return true;
    },
  );

  assert.deepEqual(registro, []);
});
