/**
 * Ordenação das anotações do gerente.
 *
 * Função pura: não altera a lista recebida, não chama a API e não depende do
 * React. Só devolve uma NOVA lista com a anotação mais recente primeiro.
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
