#!/usr/bin/env node
/**
 * Verificação rápida de que a API responde no formato esperado.
 *
 * Usa o MESMO cliente HTTP e as MESMAS fábricas de serviço do frontend, mas
 * aponta para a URL informada (padrão http://localhost:8000). É útil para
 * saber, sem abrir o navegador, se o backend está no ar e devolvendo os
 * contratos combinados.
 *
 * Uso:
 *   npm run verificar:api
 *   npm run verificar:api -- --url http://localhost:8000
 *   npm run verificar:api -- --gerar
 *
 * ATENÇÃO: a opção --gerar chama a DeepSeek de VERDADE e CONSOME CRÉDITOS.
 * Sem ela, nenhuma chamada à IA é feita.
 *
 * O script nunca imprime cabeçalhos HTTP nem dados sensíveis: só um resumo
 * curto de cada passo e, em caso de falha, a mensagem do backend.
 */

import { criarClienteApi } from '../src/services/api.js';
import { ErroApi } from '../src/services/erroApi.js';
import { criarVendedorService } from '../src/services/vendedorService.js';
import { criarRegionalService } from '../src/services/regionalService.js';
import { criarFeedbackService } from '../src/services/feedbackService.js';

/**
 * Lê os argumentos da linha de comando.
 *
 * --url troca o endereço; --gerar liga a chamada real à IA (gasta créditos).
 */
function lerArgumentos(argumentos) {
  const opcoes = { url: 'http://localhost:8000', gerar: false };

  for (let indice = 0; indice < argumentos.length; indice += 1) {
    const atual = argumentos[indice];

    if (atual === '--url' && argumentos[indice + 1]) {
      opcoes.url = argumentos[indice + 1];
      indice += 1;
    } else if (atual === '--gerar') {
      opcoes.gerar = true;
    }
  }

  return opcoes;
}

// Contador de falhas: no final, o código de saída será 1 se algo falhou.
let falhas = 0;

/**
 * Executa um passo e imprime OK ou FALHOU numa linha.
 *
 * Recebe o título do passo e uma função assíncrona que devolve um detalhe
 * curto (ou lança erro quando a verificação não passa).
 */
async function executar(titulo, passo) {
  try {
    const detalhe = await passo();
    console.log(`OK      ${titulo}${detalhe ? ` — ${detalhe}` : ''}`);
  } catch (erro) {
    falhas += 1;

    const mensagem =
      erro instanceof ErroApi
        ? `${erro.tipo}: ${erro.message}`
        : String(erro?.message ?? erro);

    console.log(`FALHOU  ${titulo} — ${mensagem}`);
  }
}

const opcoes = lerArgumentos(process.argv.slice(2));

// Cliente apontando para a URL pedida. As fábricas recebem esse cliente em
// vez do cliente padrão, o que permite verificar qualquer endereço.
const cliente = criarClienteApi({ baseURL: opcoes.url });
const vendedores = criarVendedorService(cliente);
const regional = criarRegionalService(cliente);
const feedback = criarFeedbackService(cliente);

console.log(`Verificando a API em ${opcoes.url}`);
if (opcoes.gerar) {
  console.log('ATENÇÃO: --gerar fará uma chamada real à IA e consumirá créditos.');
}

// (a) Lista da loja precisa trazer os 8 vendedores.
await executar('(a) lista da loja L004 tem 8 vendedores', async () => {
  const dados = await vendedores.obterVendedoresPorLoja('L004');
  const quantidade = dados?.vendedores?.length;

  if (quantidade !== 8) {
    throw new Error(`esperava 8 vendedores, recebi ${quantidade}`);
  }
  return `${quantidade} vendedores`;
});

// (b) Histórico da Bianca precisa ter 4 meses no resumo.
await executar('(b) histórico da Bianca tem 4 meses de resumo', async () => {
  const dados = await vendedores.obterDetalhesVendedor('C0031');
  const meses = dados?.resumo_mensal?.length;

  if (meses !== 4) {
    throw new Error(`esperava 4 meses, recebi ${meses}`);
  }
  return `${meses} meses`;
});

// (c) A visão regional precisa trazer 4 meses de resultado.
await executar('(c) visão regional tem 4 meses de resultado', async () => {
  const dados = await regional.obterDesempenhoGerente();
  const meses = dados?.resultado_loja?.length;

  if (meses !== 4) {
    throw new Error(`esperava 4 meses, recebi ${meses}`);
  }
  return `${meses} meses`;
});

// (d) Loja inexistente precisa virar ErroApi de cliente com 404 e a
// mensagem em português do backend.
await executar('(d) loja L999 responde 404 com mensagem do backend', async () => {
  try {
    await vendedores.obterVendedoresPorLoja('L999');
  } catch (erro) {
    if (!(erro instanceof ErroApi)) {
      throw erro;
    }
    if (erro.tipo !== 'cliente' || erro.status !== 404) {
      throw new Error(`esperava cliente/404, recebi ${erro.tipo}/${erro.status}`);
    }
    if (!erro.message.includes('L999')) {
      throw new Error('a mensagem do backend não veio como esperado');
    }
    return erro.message;
  }

  throw new Error('a chamada deveria ter falhado com 404');
});

// (e) Servidor fora do ar: usamos uma porta fechada de propósito.
await executar('(e) servidor fora do ar vira erro de rede', async () => {
  const semServidor = criarClienteApi({
    baseURL: 'http://localhost:9',
    timeout: 3000,
  });
  const vendedoresSemServidor = criarVendedorService(semServidor);

  try {
    await vendedoresSemServidor.obterVendedoresPorLoja('L004');
  } catch (erro) {
    if (!(erro instanceof ErroApi)) {
      throw erro;
    }
    if (erro.tipo !== 'rede') {
      throw new Error(`esperava rede, recebi ${erro.tipo}`);
    }
    return 'sem conexão, como esperado';
  }

  throw new Error('a chamada deveria falhar sem servidor');
});

// (f) Opcional: geração real. Só roda com --gerar.
if (opcoes.gerar) {
  await executar('(f) geração de feedback (consome créditos da IA)', async () => {
    const dados = await feedback.gerarFeedback('C0031');
    const secoes = dados?.roteiro?.roteiro_conversa?.length ?? 0;

    if (secoes === 0) {
      throw new Error('roteiro veio sem itens de conversa');
    }
    return `feedback_id ${dados.feedback_id}`;
  });
} else {
  console.log(
    'PULADO  (f) geração de feedback — use --gerar para chamar a IA e consumir créditos.',
  );
}

console.log(
  falhas === 0
    ? 'Todos os passos passaram.'
    : `${falhas} passo(s) falharam.`,
);

// Código 1 quando algo falhou (útil em scripts e CI).
process.exitCode = falhas === 0 ? 0 : 1;
