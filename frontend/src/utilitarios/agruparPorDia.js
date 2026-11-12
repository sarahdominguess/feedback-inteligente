/**
 * Agrupamento das anotações por dia, para o chat da aba Anotações.
 *
 * Função pura: não usa React, não chama a API e não altera a lista recebida.
 * Ela só reorganiza o que já veio pronto do backend.
 */

/**
 * Agrupa anotações por dia, mantendo a ordem recebida.
 *
 * Recebe uma lista de anotações JÁ em ordem cronológica (use
 * ordenarDaMaisAntigaParaMaisRecente antes) e devolve uma lista de grupos:
 *
 *   [{ data: '2026-08-06', itens: [...] },
 *    { data: '2026-09-15', itens: [...] }]
 *
 * - um grupo por dia, na ordem em que os dias aparecem na lista;
 * - dentro do grupo, os itens ficam na ordem recebida;
 * - lista vazia → lista vazia; entrada que não é lista → lista vazia.
 *
 * Por que o agrupamento depende da ordem: dois dias iguais separados por
 * outro dia viram DOIS grupos (o dia "volta" na conversa). Ordenar é
 * responsabilidade da outra função, não desta.
 *
 * Anotação sem data válida entra num grupo com data "" — quem exibe mostra
 * "—" no lugar do dia, em vez de esconder o texto que a pessoa escreveu.
 *
 * Exemplo: agruparPorDia([
 *            { data: '2026-08-06', texto: 'a' },
 *            { data: '2026-08-06', texto: 'b' },
 *            { data: '2026-09-15', texto: 'c' },
 *          ])
 *          → [{ data: '2026-08-06', itens: [a, b] },
 *             { data: '2026-09-15', itens: [c] }]
 */
export function agruparPorDia(anotacoes) {
  // Entrada inesperada não pode quebrar a tela.
  if (!Array.isArray(anotacoes)) {
    return [];
  }

  /*
   * Os grupos são montados aqui dentro, do zero: nem o array recebido nem os
   * objetos de anotação são alterados. (Criar estruturas novas localmente não
   * fere a "pureza": o que importa é não mexer no que veio de fora.)
   */
  const grupos = [];

  for (const anotacao of anotacoes) {
    // A data é o critério do agrupamento; sem texto válido, vale "".
    const data =
      typeof anotacao?.data === 'string' ? anotacao.data.trim() : '';

    // O último grupo é sempre o "dia atual" da conversa sendo percorrida.
    const ultimo = grupos[grupos.length - 1];

    if (ultimo !== undefined && ultimo.data === data) {
      // Mesmo dia: só acrescenta mais uma mensagem no grupo.
      ultimo.itens.push(anotacao);
    } else {
      // Dia diferente (ou o primeiro item): começa um grupo novo.
      grupos.push({ data, itens: [anotacao] });
    }
  }

  return grupos;
}
