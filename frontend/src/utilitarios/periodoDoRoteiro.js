/**
 * Rótulo do período de um roteiro de feedback.
 *
 * Função pura: transforma o mês "AAAA-MM" em texto para a tela, sem rede e
 * sem depender do React. É usada pela página e pelo visualizador do roteiro.
 */

import { formatarMes } from './formatadores.js';

/**
 * Devolve o período em texto: "outubro de 2026" ou "Todo o histórico".
 *
 * Recebe mes_referencia como a API manda: "AAAA-MM" ou null quando a geração
 * considerou todo o histórico. Texto vazio também conta como "todo".
 *
 * Se o texto não for um mês válido, formatarMes devolve "—". É melhor mostrar
 * que o dado veio errado do que fingir que era o histórico inteiro.
 *
 * Exemplo: rotuloPeriodo('2026-10') → "outubro de 2026"
 *          rotuloPeriodo(null) → "Todo o histórico"
 */
export function rotuloPeriodo(mesReferencia) {
  if (typeof mesReferencia === 'string' && mesReferencia.trim() !== '') {
    return formatarMes(mesReferencia);
  }

  return 'Todo o histórico';
}
