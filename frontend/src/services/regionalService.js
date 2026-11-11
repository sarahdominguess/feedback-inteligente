/**
 * Serviço da visão executiva da regional.
 *
 * Responsável pela chamada que a gerente regional usa para ver o resultado da
 * loja e a cobertura dos roteiros preparados. Só busca e devolve os dados: as
 * contas (atingimentos, cobertura) já vêm prontas do backend.
 */

import { api } from './api.js';

/**
 * Cria o serviço da regional usando um cliente HTTP.
 *
 * A fábrica existe para os testes trocarem o cliente real por um falso com
 * adapter simulado, sem depender de rede.
 *
 * Recebe: cliente (instância do Axios; padrão = cliente real).
 * Devolve: { obterDesempenhoGerente }.
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

  return { obterDesempenhoGerente };
}

// Função já ligada ao cliente HTTP real, pronta para a tela usar.
export const { obterDesempenhoGerente } = criarRegionalService();
