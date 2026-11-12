/**
 * Serviço da visão executiva da regional.
 *
 * Responsável pelas chamadas que a gerente regional usa para ver o resultado da
 * loja, a cobertura dos roteiros preparados, as lojas disponíveis e o histórico
 * de cada loja. Só busca e devolve os dados: as contas (atingimentos,
 * cobertura) já vêm prontas do backend.
 */

import { api } from './api.js';
import { ErroApi } from './erroApi.js';
import { TIMEOUT_GERACAO_MS } from './feedbackService.js';

/**
 * Confere se o código da loja é texto e não está vazio.
 *
 * Recebe o valor recebido. Devolve o texto sem espaços nas pontas; se for
 * inválido, lança um ErroApi de tipo "validacao" e a API nem chega a ser
 * chamada.
 *
 * Exemplo: validarLojaId('  L004  ') devolve 'L004'.
 */
function validarLojaId(valor) {
  if (typeof valor !== 'string' || valor.trim() === '') {
    throw new ErroApi('Informe o código da loja para continuar.', {
      tipo: 'validacao',
    });
  }

  return valor.trim();
}

/**
 * Confere e limpa o texto da anotação da regional.
 *
 * Recebe o que a pessoa digitou. Devolve o texto sem espaços, tabulações e
 * quebras de linha das PONTAS — as do MEIO continuam, porque fazem parte do
 * que foi escrito.
 *
 * Lança ErroApi de tipo "validacao" quando não é texto ou fica vazio depois da
 * limpeza. As mensagens são as MESMAS do serviço de anotações do gerente, para
 * a pessoa ver o mesmo texto nos dois lugares.
 *
 * O limite de caracteres NÃO é conferido aqui: o backend é a autoridade e
 * responde 400 com mensagem clara.
 *
 * Exemplo: validarTexto('  visitar a loja  ') devolve 'visitar a loja'.
 */
function validarTexto(valor) {
  if (typeof valor !== 'string') {
    throw new ErroApi('Escreva a anotação como texto.', {
      tipo: 'validacao',
    });
  }

  const textoLimpo = valor.trim();

  if (textoLimpo === '') {
    throw new ErroApi('Escreva alguma coisa antes de salvar a anotação.', {
      tipo: 'validacao',
    });
  }

  return textoLimpo;
}

/**
 * Cria o serviço da regional usando um cliente HTTP.
 *
 * A fábrica existe para os testes trocarem o cliente real por um falso com
 * adapter simulado, sem depender de rede.
 *
 * Recebe: cliente (instância do Axios; padrão = cliente real).
 * Devolve: { obterDesempenhoGerente, listarLojas, obterHistoricoLoja,
 *   registrarAnotacaoRegional, gerarFeedbackRegional }.
 */
export function criarRegionalService(cliente = api) {
  /**
   * Busca o consolidado da loja para a regional.
   *
   * Recebe: signal (opcional), para cancelar a chamada em andamento.
   * Devolve os dados da API sem transformar (DesempenhoGerenteResposta).
   *
   * Exemplo: obterDesempenhoGerente()
   */
  async function obterDesempenhoGerente({ signal } = {}) {
    return cliente.get('/api/regional/desempenho-gerente', { signal });
  }

  /**
   * Lista as lojas que a regional pode acompanhar.
   *
   * Recebe: signal (opcional), para cancelar a chamada.
   * Devolve os dados da API sem transformar (ListaLojasResposta).
   *
   * Hoje o backend devolve só a L004, mas o formato já é uma lista.
   *
   * Exemplo: listarLojas()
   */
  async function listarLojas({ signal } = {}) {
    return cliente.get('/api/regional/lojas', { signal });
  }

  /**
   * Busca o histórico de uma loja (consolidado + roteiros do gerente).
   *
   * Recebe:
   *   lojaId: código da loja (ex.: "L004"), obrigatório.
   *   signal: opcional, para cancelar a chamada.
   *
   * Devolve os dados da API sem transformar (HistoricoLojaResposta).
   *
   * Exemplo: obterHistoricoLoja("L004")
   */
  async function obterHistoricoLoja(lojaId, { signal } = {}) {
    const id = validarLojaId(lojaId);

    // encodeURIComponent protege o caminho: "L/004" vira "L%2F004" e não
    // quebra a URL em dois pedaços.
    return cliente.get(
      `/api/regional/lojas/${encodeURIComponent(id)}/historico`,
      { signal },
    );
  }

  /**
   * Grava uma anotação nova da regional sobre a loja.
   *
   * Recebe:
   *   lojaId: código da loja, obrigatório.
   *   texto: o que a regional escreveu, obrigatório e não vazio.
   *   signal: opcional, para cancelar a chamada.
   *
   * Devolve o corpo da resposta SEM transformar (AnotacaoRegionalDTO):
   * { data, autora, texto }. A autora e a data são decisão do backend — o
   * cliente envia só o texto.
   *
   * Exemplo: registrarAnotacaoRegional("L004", "visitar a loja na sexta")
   */
  async function registrarAnotacaoRegional(lojaId, texto, { signal } = {}) {
    // 1) Validação local: recusa id/texto inválidos antes de tocar na rede.
    const id = validarLojaId(lojaId);
    const textoLimpo = validarTexto(texto);

    // 2) POST no caminho da loja. O corpo leva SÓ o texto: a autora
    // ("Patrícia Lemos") e a data de hoje são gravadas pelo servidor.
    return cliente.post(
      `/api/regional/lojas/${encodeURIComponent(id)}/anotacoes`,
      { texto: textoLimpo },
      { signal },
    );
  }

  /**
   * Pede ao backend o roteiro de feedback da regional para o gerente da loja.
   *
   * Recebe:
   *   lojaId: código da loja, obrigatório.
   *   mesReferencia: opcional, "AAAA-MM". Em camelCase no JavaScript e
   *     snake_case no corpo JSON, que é o formato do backend.
   *   signal: opcional, para cancelar a chamada.
   *
   * Devolve os dados da API sem transformar (FeedbackRegionalGerarResposta).
   * Usa o MESMO timeout longo da geração do vendedor, porque a IA pode ser
   * chamada duas vezes no backend.
   *
   * Exemplo: gerarFeedbackRegional("L004", { mesReferencia: "2026-10" })
   */
  async function gerarFeedbackRegional(lojaId, { mesReferencia, signal } = {}) {
    // 1) Validação local: não gastamos uma chamada de IA com pedido vazio.
    const id = validarLojaId(lojaId);

    // 2) Corpo no formato do backend (snake_case). O mês só entra quando foi
    // informado; o formato AAAA-MM é validado pelo backend (autoridade).
    const corpo = { loja_id: id };
    if (typeof mesReferencia === 'string' && mesReferencia.trim() !== '') {
      corpo.mes_referencia = mesReferencia.trim();
    }

    // 3) Uma única chamada, com o timeout maior desta operação. Sem retry:
    // repetir sozinho gastaria créditos de IA sem a pessoa pedir.
    return cliente.post('/api/regional/feedback/gerar', corpo, {
      signal,
      timeout: TIMEOUT_GERACAO_MS,
    });
  }

  return {
    obterDesempenhoGerente,
    listarLojas,
    obterHistoricoLoja,
    registrarAnotacaoRegional,
    gerarFeedbackRegional,
  };
}

// Funções já ligadas ao cliente HTTP real, prontas para as telas usarem.
export const {
  obterDesempenhoGerente,
  listarLojas,
  obterHistoricoLoja,
  registrarAnotacaoRegional,
  gerarFeedbackRegional,
} = criarRegionalService();
