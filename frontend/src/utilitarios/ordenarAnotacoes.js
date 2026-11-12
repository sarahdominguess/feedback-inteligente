/**
 * Ordenação das anotações do gerente.
 *
 * Função pura: não altera a lista recebida, não chama a API e não depende do
 * React. Devolve sempre uma NOVA lista: uma função para ver a mais recente
 * primeiro e outra para ver a mais antiga primeiro (ordem de chat).
 */

/**
 * Ordena anotações da mais recente para a mais antiga.
 *
 * Recebe uma lista de anotações no formato da API ({ data, texto, ... }).
 * Devolve uma lista nova; a original fica intacta. Quando duas anotações têm
 * a mesma data, mantém a ordem em que vieram (ordem estável).
 *
 * Por que não usamos new Date: a data chega como texto "AAAA-MM-DD". Nesse
 * formato, comparar os textos em ordem alfabética já dá a ordem cronológica,
 * sem risco de o fuso horário mudar o dia.
 *
 * Exemplo: ordenarAnotacoes([{ data: '2026-08-06' }, { data: '2026-10-08' }])
 *          → [{ data: '2026-10-08' }, { data: '2026-08-06' }]
 */
export function ordenarAnotacoes(anotacoes) {
  // Entrada inesperada não pode quebrar a tela.
  if (!Array.isArray(anotacoes)) {
    return [];
  }

  /*
   * O map com o índice guarda a posição original de cada item. No empate de
   * datas, comparamos os índices para garantir a ordem recebida, mesmo que o
   * motor do JavaScript mude a estabilidade do sort no futuro.
   */
  return anotacoes
    .map((anotacao, indice) => ({ anotacao, indice }))
    .sort((a, b) => {
      const dataA =
        typeof a.anotacao?.data === 'string' ? a.anotacao.data : '';
      const dataB =
        typeof b.anotacao?.data === 'string' ? b.anotacao.data : '';

      // Datas iguais (ou sem data): quem chegou primeiro continua primeiro.
      if (dataA === dataB) {
        return a.indice - b.indice;
      }

      // Ordem decrescente: a data maior (mais recente) vem antes.
      return dataA > dataB ? -1 : 1;
    })
    // Devolve só as anotações, sem o índice auxiliar.
    .map(({ anotacao }) => anotacao);
}

/**
 * Ordena anotações da mais antiga para a mais recente (ordem de chat).
 *
 * Recebe uma lista de anotações no formato da API ({ data, texto, ... }).
 * Devolve uma lista NOVA, com a data menor primeiro — num chat, a conversa
 * mais antiga fica em cima e a nova aparece embaixo. A lista original fica
 * intacta.
 *
 * "Ordenação estável" quer dizer que, quando duas anotações têm a MESMA data,
 * elas mantêm a ordem em que chegaram na lista (a ordem em que foram
 * escritas). Nada é embaralhado de forma imprevisível.
 *
 * Por que comparamos textos e não usamos new Date: a data chega como texto
 * "AAAA-MM-DD", e nesse formato a ordem alfabética já é a ordem cronológica.
 * new Date("2026-10-10") seria lido como meia-noite no fuso universal e, no
 * Brasil, poderia cair no dia anterior (problema de fuso horário).
 *
 * Exemplo: ordenarDaMaisAntigaParaMaisRecente([
 *            { data: '2026-10-08' }, { data: '2026-08-06' },
 *          ]) → [{ data: '2026-08-06' }, { data: '2026-10-08' }]
 */
export function ordenarDaMaisAntigaParaMaisRecente(anotacoes) {
  // Entrada inesperada não pode quebrar a tela.
  if (!Array.isArray(anotacoes)) {
    return [];
  }

  /*
   * O map com o índice guarda a posição original de cada item. No empate de
   * datas, comparamos os índices para garantir a ordem recebida.
   */
  return anotacoes
    .map((anotacao, indice) => ({ anotacao, indice }))
    .sort((a, b) => {
      const dataA =
        typeof a.anotacao?.data === 'string' ? a.anotacao.data : '';
      const dataB =
        typeof b.anotacao?.data === 'string' ? b.anotacao.data : '';

      // Datas iguais (ou sem data): quem chegou primeiro continua primeiro.
      if (dataA === dataB) {
        return a.indice - b.indice;
      }

      // Ordem crescente: a data menor (mais antiga) vem antes.
      return dataA < dataB ? -1 : 1;
    })
    // Devolve só as anotações, sem o índice auxiliar.
    .map(({ anotacao }) => anotacao);
}
