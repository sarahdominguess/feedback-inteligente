/**
 * Erros de comunicação com a API, num formato único para a interface.
 *
 * Este arquivo transforma qualquer falha do Axios (biblioteca que faz as
 * chamadas HTTP) num objeto ErroApi, com uma mensagem em português pronta
 * para aparecer na tela. Assim as telas não precisam conhecer detalhes
 * técnicos do Axios.
 */

// Axios: biblioteca que conversa com a API. Usamos axios.isCancel para
// reconhecer um cancelamento feito de propósito (por exemplo, quando a pessoa
// troca de tela antes da resposta chegar).
import axios from 'axios';

/**
 * Lista fechada dos tipos de erro que o frontend entende.
 *
 * - rede: servidor inacessível (backend desligado, cabo, Wi-Fi);
 * - tempo_esgotado: a resposta demorou mais que o limite;
 * - cliente: a API respondeu 4xx (pedido inválido, não encontrado);
 * - servidor: a API respondeu 5xx (erro interno ou IA fora do ar);
 * - cancelada: a chamada foi cancelada de propósito;
 * - validacao: um argumento inválido foi detectado antes de chamar a API;
 * - desconhecido: qualquer outra falha que não sabemos classificar.
 */
export const TIPOS_ERRO = [
  'rede',
  'tempo_esgotado',
  'cliente',
  'servidor',
  'cancelada',
  'validacao',
  'desconhecido',
];

/**
 * Erro padronizado da API, pronto para a interface mostrar.
 *
 * Recebe:
 *   mensagem: texto em português para o usuário.
 *   tipo: um dos valores de TIPOS_ERRO.
 *   status: número HTTP (ex.: 404) ou null quando não houve resposta.
 *   detalhes: espaço reservado para dados extras; hoje sempre null.
 *
 * Exemplo: new ErroApi("Loja não encontrada.", { tipo: "cliente", status: 404 })
 */
export class ErroApi extends Error {
  constructor(
    mensagem,
    { tipo = 'desconhecido', status = null, detalhes = null } = {},
  ) {
    // super() chama o construtor da classe Error do JavaScript, que guarda a
    // mensagem e a pilha de chamadas (stack) para depuração.
    super(mensagem);

    // name é o nome do erro que aparece em ferramentas de depuração.
    this.name = 'ErroApi';
    this.tipo = tipo;
    this.status = status;
    this.detalhes = detalhes;
  }
}

/**
 * Converte qualquer erro em ErroApi, sem vazar dados sensíveis.
 *
 * Recebe: o erro que o Axios (ou outro código) lançou.
 * Devolve: um ErroApi com mensagem em português, tipo e status.
 *
 * Regra de segurança: NUNCA copiamos URL, cabeçalhos, config ou o corpo
 * bruto da resposta para o erro. Lemos apenas o status e o campo "erro"
 * (texto) que a API devolve.
 */
export function normalizarErro(erro) {
  // 1) Se já é nosso erro, não há nada a converter.
  if (erro instanceof ErroApi) {
    return erro;
  }

  // 2) Cancelamento de propósito: axios.isCancel reconhece o erro do
  // CancelToken antigo; o código ERR_CANCELED cobre o AbortController.
  if (axios.isCancel(erro) || erro?.code === 'ERR_CANCELED') {
    return new ErroApi('A consulta foi cancelada.', {
      tipo: 'cancelada',
    });
  }

  // 3) O servidor respondeu (mesmo que com erro): existe erro.response.
  const resposta = erro?.response;
  if (resposta) {
    const status =
      typeof resposta.status === 'number' ? resposta.status : null;

    // 4xx é "culpa do pedido"; 5xx é "problema no servidor".
    const tipo = status !== null && status >= 500 ? 'servidor' : 'cliente';

    // A API sempre devolve {"erro": "mensagem em português"} nos erros.
    const mensagemDaApi = resposta.data?.erro;

    if (typeof mensagemDaApi === 'string' && mensagemDaApi.trim() !== '') {
      return new ErroApi(mensagemDaApi, { tipo, status });
    }

    // Resposta sem o campo "erro": usamos uma mensagem genérica da faixa.
    const mensagemGenerica =
      tipo === 'servidor'
        ? 'O servidor encontrou um erro. Tente novamente em instantes.'
        : 'Não foi possível concluir o pedido.';

    return new ErroApi(mensagemGenerica, { tipo, status });
  }

  // 4) Nenhuma resposta, mas o código indica que o tempo estourou.
  if (erro?.code === 'ECONNABORTED' || erro?.code === 'ETIMEDOUT') {
    return new ErroApi(
      'A resposta demorou mais do que o esperado. Tente novamente.',
      { tipo: 'tempo_esgotado' },
    );
  }

  // 5) Erro do Axios sem resposta: o servidor não foi alcançado.
  if (erro?.isAxiosError) {
    return new ErroApi(
      'Não foi possível conectar ao servidor. Verifique se o backend está rodando.',
      { tipo: 'rede' },
    );
  }

  // 6) Qualquer outra coisa (erro de programação, valor estranho etc.).
  return new ErroApi('Não foi possível concluir a operação.', {
    tipo: 'desconhecido',
  });
}

/**
 * Diz se o erro representa um cancelamento de propósito.
 *
 * Recebe qualquer erro e devolve true apenas quando ele já é um ErroApi de
 * tipo "cancelada". Útil para a tela ignorar cancelamentos em vez de mostrar
 * uma mensagem de falha.
 */
export function erroFoiCancelamento(erro) {
  return erro instanceof ErroApi && erro.tipo === 'cancelada';
}
