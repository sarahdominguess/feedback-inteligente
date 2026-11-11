/**
 * Funções puras da visão regional.
 *
 * Só escolhem textos e tons de exibição a partir dos dados da API. Não
 * calculam métrica: atingimento, cobertura e participação já vêm prontos do
 * backend.
 */

import { formatarData } from './formatadores.js';

/**
 * Escolhe o selo do atingimento da loja.
 *
 * Recebe a fração que o backend já calculou: vendas da loja divididas pela
 * meta. Devolve um objeto { texto, tom } quando é um número válido:
 * - maior ou igual a 1 (100% da meta) → "Meta batida" / positivo;
 * - menor que 1 → "Abaixo da meta" / atenção.
 * Sem número válido (null, undefined ou NaN), devolve null e a tabela não
 * mostra selo nenhum.
 *
 * A comparação com 1 NÃO cria métrica nova: só escolhe qual texto aparece.
 * O cálculo do atingimento é do backend.
 *
 * Exemplo: seloDoAtingimento(1.12)
 *          → { texto: 'Meta batida', tom: 'positivo' }
 */
export function seloDoAtingimento(atingimento) {
  if (typeof atingimento !== 'number' || !Number.isFinite(atingimento)) {
    return null;
  }

  if (atingimento >= 1) {
    return { texto: 'Meta batida', tom: 'positivo' };
  }

  return { texto: 'Abaixo da meta', tom: 'atencao' };
}

/**
 * Escolhe o tom do selo de acompanhamento de feedback.
 *
 * Recebe a situação vinda do backend: "com_roteiro" ou "sem_roteiro".
 * Devolve "positivo" para quem já tem roteiro preparado e "atencao" para
 * quem ainda não tem. Situação desconhecida vira "neutro", para a tela não
 * inventar um alerta.
 *
 * Exemplo: tomDoAcompanhamento('com_roteiro') → 'positivo'
 */
export function tomDoAcompanhamento(situacao) {
  if (situacao === 'com_roteiro') {
    return 'positivo';
  }

  if (situacao === 'sem_roteiro') {
    return 'atencao';
  }

  return 'neutro';
}

/**
 * Monta o texto do período analisado.
 *
 * Recebe as datas de início e fim como a API manda ("AAAA-MM-DD" ou null).
 * Devolve:
 * - as duas datas: "01/08/2026 a 01/11/2026";
 * - só o início: "A partir de 01/08/2026";
 * - só o fim: "Até 01/11/2026";
 * - nenhuma: "Período não informado".
 *
 * O formatador devolve "—" quando a data não existe; por isso comparamos o
 * resultado com esse texto para saber se a data existe de verdade.
 *
 * Exemplo: textoPeriodo('2026-08-01', '2026-11-01')
 *          → "01/08/2026 a 01/11/2026"
 */
export function textoPeriodo(inicio, fim) {
  const inicioFormatado = formatarData(inicio);
  const fimFormatado = formatarData(fim);

  const temInicio = inicioFormatado !== '—';
  const temFim = fimFormatado !== '—';

  if (temInicio && temFim) {
    return `${inicioFormatado} a ${fimFormatado}`;
  }

  if (temInicio) {
    return `A partir de ${inicioFormatado}`;
  }

  if (temFim) {
    return `Até ${fimFormatado}`;
  }

  return 'Período não informado';
}
