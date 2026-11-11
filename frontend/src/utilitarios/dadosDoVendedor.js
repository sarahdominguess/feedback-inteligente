/**
 * Funções puras de apoio à página da aba Dados.
 *
 * Elas apenas escolhem um item da lista e montam textos de exibição. Não
 * calculam métrica, não chamam a API e não dependem do React.
 */

/**
 * Procura, na lista de comparativos, o item de uma métrica.
 *
 * Recebe a lista vinda da API (ou qualquer valor) e o nome técnico da
 * métrica: "ticket_medio", "pecas_por_atendimento" ou "conversao".
 *
 * Devolve o item encontrado ou null quando não existe. Se o valor recebido
 * não for uma lista, devolve null em vez de quebrar a tela.
 *
 * Exemplo: acharComparativo(lista, 'conversao') → { nome: 'conversao', ... }
 */
export function acharComparativo(comparativo, nome) {
  if (!Array.isArray(comparativo)) {
    return null;
  }

  // item?.nome usa "optional chaining": se item for null, nem tenta ler a
  // propriedade e a comparação simplesmente falha.
  return comparativo.find((item) => item?.nome === nome) ?? null;
}

/**
 * Monta o texto da posição no ranking do time.
 *
 * Recebe um item do comparativo. Devolve "Posição 3 de 8" quando posicao e
 * total_vendedores são inteiros positivos; caso contrário, texto vazio.
 *
 * O contrato diz que posição 1 é a melhor e que null significa "fora do
 * ranking". Por isso 0, texto ou valor ausente não viram posição.
 *
 * Exemplo: textoPosicao({ posicao: 3, total_vendedores: 8 }) → "Posição 3 de 8"
 */
export function textoPosicao(item) {
  if (!item) {
    return '';
  }

  const posicao = item.posicao;
  const total = item.total_vendedores;

  const posicaoValida = Number.isInteger(posicao) && posicao > 0;
  const totalValido = Number.isInteger(total) && total > 0;

  if (!posicaoValida || !totalValido) {
    return '';
  }

  return `Posição ${posicao} de ${total}`;
}

/**
 * Monta a linha de detalhe do cartão de indicador.
 *
 * Recebe o item do comparativo (ou null) e a média do time JÁ formatada por
 * quem chama (ex.: "R$ 210,00"). Devolve "Média do time: X · Posição 3 de 8"
 * ou apenas a parte que existir. Sem item, devolve texto vazio, e o cartão
 * fica sem detalhe.
 *
 * Exemplo: montarDetalheComparativo(item, 'R$ 210,00')
 *          → "Média do time: R$ 210,00 · Posição 3 de 8"
 */
export function montarDetalheComparativo(item, mediaFormatada) {
  if (!item) {
    return '';
  }

  // Se a média não vier como texto útil, usamos o travessão do app.
  const media =
    typeof mediaFormatada === 'string' && mediaFormatada !== ''
      ? mediaFormatada
      : '—';

  const partes = [`Média do time: ${media}`];
  const posicao = textoPosicao(item);

  // O "·" separa as duas informações só quando a posição existe.
  if (posicao !== '') {
    partes.push(posicao);
  }

  return partes.join(' · ');
}
