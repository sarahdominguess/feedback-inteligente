/**
 * Serviço de geração de feedback.
 *
 * É a chamada mais lenta do sistema: o backend conversa com a IA (DeepSeek),
 * valida a resposta e só então devolve o roteiro. Por isso este serviço tem um
 * tempo de espera próprio, maior que o padrão.
 *
 * O frontend não monta prompt, não valida a qualidade do roteiro e não tenta
 * de novo sozinho: cada geração consome créditos de IA.
 */

import { api } from './api.js';
import { ErroApi } from './erroApi.js';

/**
 * Tempo máximo de espera desta chamada: 150 segundos (150.000 ms).
 *
 * Por que tão alto: o backend pode chamar a IA até DUAS vezes (a segunda é
 * uma correção quando a primeira resposta é reprovada), e cada chamada pode
 * levar até 60 s. Com o timeout padrão do cliente (20 s) a tela desistiria
 * antes de o servidor terminar. O valor é passado só nesta requisição, sem
 * mudar o padrão das demais.
 */
export const TIMEOUT_GERACAO_MS = 150000;

/**
 * Cria o serviço de geração de feedback usando um cliente HTTP.
 *
 * A fábrica permite os testes passarem um cliente falso (com adapter
 * simulado), sem rede e sem gastar créditos de IA.
 *
 * Recebe: cliente (instância do Axios; padrão = cliente real).
 * Devolve: { gerarFeedback }.
 */
export function criarFeedbackService(cliente = api) {
  /**
   * Pede ao backend um roteiro de feedback para um vendedor.
   *
   * Recebe:
   *   vendedorId: código da pessoa (ex.: "C0031"), obrigatório.
   *   mesReferencia: opcional, "AAAA-MM". O nome é camelCase no JavaScript,
   *     mas no corpo JSON vira "mes_referencia" (snake_case), que é o formato
   *     que o backend espera.
   *   signal: opcional, para cancelar a chamada.
   *
   * Devolve os dados da API sem transformar: feedback_id, vendedor_id,
   * vendedor_nome, mes_referencia, gerado_em e roteiro com as 4 listas.
   *
   * Exemplo: gerarFeedback("C0031", { mesReferencia: "2026-10" })
   */
  async function gerarFeedback(vendedorId, { mesReferencia, signal } = {}) {
    // 1) Validação local: identificador precisa ser texto não vazio. Assim
    // nem chegamos a gastar uma chamada de IA com um pedido sem sentido.
    if (typeof vendedorId !== 'string' || vendedorId.trim() === '') {
      throw new ErroApi('Informe o código do vendedor para continuar.', {
        tipo: 'validacao',
      });
    }

    // 2) Corpo no formato do backend (snake_case). O mês só entra quando foi
    // informado; não validamos o formato AAAA-MM aqui porque o backend é a
    // autoridade: ele responde 400 com uma mensagem clara se o texto estiver
    // errado. Duplicar a regra no frontend só criaria divergência.
    const corpo = { vendedor_id: vendedorId.trim() };
    if (typeof mesReferencia === 'string' && mesReferencia.trim() !== '') {
      corpo.mes_referencia = mesReferencia.trim();
    }

    // 3) Uma única chamada, com o timeout maior desta operação. Sem retry:
    // repetir automaticamente gastaria créditos de IA sem a pessoa pedir.
    return cliente.post('/api/feedback/gerar', corpo, {
      signal,
      timeout: TIMEOUT_GERACAO_MS,
    });
  }

  return { gerarFeedback };
}

// Função já ligada ao cliente HTTP real, pronta para a tela usar.
export const { gerarFeedback } = criarFeedbackService();
