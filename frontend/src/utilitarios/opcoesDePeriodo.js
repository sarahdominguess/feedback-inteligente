/**
 * Opções do seletor de período do roteiro de feedback.
 *
 * Função pura: monta a lista de opções e escolhe o período pré-selecionado
 * sem alterar o histórico, sem chamar a API e sem depender do React.
 */

import { formatarMes } from './formatadores.js';

/**
 * Monta a opção "Todo o histórico" e uma opção por mês do resumo.
 *
 * Recebe a lista resumo_mensal vinda da API.
 *
 * Devolve:
 *   { opcoes: [{ valor, rotulo }], valorPadrao }
 *
 * - valor "" representa "Todo o histórico" (nenhum mês escolhido);
 * - valorPadrao é o último mês NÃO parcial ou "" se não houver nenhum.
 *
 * "Último" respeita a ordem recebida (a API entrega em ordem cronológica);
 * não reordenamos nada aqui.
 *
 * Exemplo: montarOpcoesDePeriodo([{ mes: '2026-10', mes_parcial: false }])
 *   → {
 *       opcoes: [
 *         { valor: '', rotulo: 'Todo o histórico' },
 *         { valor: '2026-10', rotulo: 'outubro de 2026' },
 *       ],
 *       valorPadrao: '2026-10',
 *     }
 */
export function montarOpcoesDePeriodo(resumoMensal) {
  // Entrada inesperada vira lista vazia em vez de quebrar a tela.
  const meses = Array.isArray(resumoMensal)
    ? resumoMensal.filter(
        (item) => typeof item?.mes === 'string' && item.mes !== '',
      )
    : [];

  const opcoes = [
    { valor: '', rotulo: 'Todo o histórico' },
    ...meses.map((item) => ({
      valor: item.mes,
      rotulo: item.mes_parcial
        ? `${formatarMes(item.mes)} (parcial)`
        : formatarMes(item.mes),
    })),
  ];

  return { opcoes, valorPadrao: escolherUltimoMesCompleto(meses) };
}

/**
 * Escolhe o último mês com mes_parcial exatamente igual a false.
 *
 * Percorre a lista de trás para frente. Devolve "" quando nenhum mês está
 * completo (por exemplo, quando só existe um mês em andamento), o que faz o
 * seletor abrir em "Todo o histórico".
 */
function escolherUltimoMesCompleto(meses) {
  for (let indice = meses.length - 1; indice >= 0; indice -= 1) {
    if (meses[indice].mes_parcial === false) {
      return meses[indice].mes;
    }
  }

  return '';
}
