/**
 * Serviço de vendedores.
 *
 * Aqui ficam as chamadas HTTP das telas que mostram a lista da loja e o
 * histórico de um vendedor. Nenhuma regra de negócio mora aqui: os números
 * (ticket médio, P.A., conversão) já chegam prontos da API, e o serviço só
 * pede e devolve os dados.
 */

import { api } from './api.js';
import { ErroApi } from './erroApi.js';

/**
 * Confere se um identificador é texto e não está vazio.
 *
 * Recebe o valor recebido e o nome do campo (para a mensagem ficar clara).
 * Devolve o texto já sem espaços nas pontas. Se for inválido, lança um
 * ErroApi de tipo "validacao" — e a API nem chega a ser chamada.
 */
function validarIdentificador(valor, nomeDoCampo) {
  if (typeof valor !== 'string' || valor.trim() === '') {
    throw new ErroApi(`Informe ${nomeDoCampo} para continuar.`, {
      tipo: 'validacao',
    });
  }
  return valor.trim();
}

/**
 * Cria o serviço de vendedores usando um cliente HTTP.
 *
 * Por que existe uma "fábrica" (função que devolve funções): nos testes
 * passamos um cliente falso, com um adapter que simula a API. Em produção a
 * fábrica é chamada sem argumento e usa o cliente real exportado por api.js.
 *
 * Recebe: cliente (instância do Axios; padrão = cliente real).
 * Devolve: { obterVendedoresPorLoja, obterDetalhesVendedor }.
 */
export function criarVendedorService(cliente = api) {
  /**
   * Busca os vendedores de uma loja.
   *
   * Recebe:
   *   lojaId: código da loja (ex.: "L004").
   *   mes: opcional, "AAAA-MM"; sem ele, a API usa todo o histórico.
   *   signal: opcional, permite cancelar a chamada (AbortController).
   *
   * Devolve os dados da API sem transformar (ListaVendedoresResposta).
   *
   * Exemplo: obterVendedoresPorLoja("L004", { mes: "2026-10" })
   */
  async function obterVendedoresPorLoja(lojaId, { mes, signal } = {}) {
    const id = validarIdentificador(lojaId, 'o código da loja');

    // A query "mes" só entra quando foi realmente informada (texto não vazio).
    // Assim a URL fica limpa e a API não recebe um mês inválido por acidente.
    const configuracao = { signal };
    if (typeof mes === 'string' && mes.trim() !== '') {
      configuracao.params = { mes: mes.trim() };
    }

    // encodeURIComponent protege o caminho: "L/004" vira "L%2F004" e não
    // quebra a URL em dois pedaços.
    return cliente.get(`/api/vendedores/${encodeURIComponent(id)}`, configuracao);
  }

  /**
   * Busca o histórico completo de um vendedor.
   *
   * Recebe:
   *   vendedorId: código da pessoa (ex.: "C0031").
   *   signal: opcional, para cancelar a chamada.
   *
   * Devolve os dados da API sem transformar (HistoricoVendedorResposta).
   *
   * Exemplo: obterDetalhesVendedor("C0031")
   */
  async function obterDetalhesVendedor(vendedorId, { signal } = {}) {
    const id = validarIdentificador(vendedorId, 'o código do vendedor');

    return cliente.get(
      `/api/vendedores/${encodeURIComponent(id)}/historico`,
      { signal },
    );
  }

  return { obterVendedoresPorLoja, obterDetalhesVendedor };
}

// Funções já ligadas ao cliente HTTP real, prontas para as telas usarem.
export const { obterVendedoresPorLoja, obterDetalhesVendedor } =
  criarVendedorService();
