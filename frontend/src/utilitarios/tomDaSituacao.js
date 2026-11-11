/**
 * Traduz a situação de uma métrica no "tom" visual do selo.
 *
 * Função pura: para a mesma entrada devolve sempre a mesma saída, sem rede,
 * sem estado e sem calcular métrica. "Tom" é a ideia visual (neutro,
 * positivo, atenção ou negativo); quem escolhe as cores é o CSS do Selo.
 */

/**
 * Devolve o tom correspondente à situação vinda da API.
 *
 * Recebe a situação ("acima", "abaixo", "na_media" ou "indisponivel") e
 * devolve "positivo", "atencao", "neutro" ou "negativo".
 *
 * Por que "abaixo" vira "atencao" e não "negativo": estar abaixo da média do
 * time é um ponto de desenvolvimento para conversar, não uma falha. O tom de
 * erro (negativo) fica reservado para problemas de verdade.
 *
 * Situação desconhecida, null ou qualquer outro tipo vira "neutro", o tom
 * mais discreto, para a tela nunca inventar um alerta.
 *
 * Exemplo: tomDaSituacao('acima') → "positivo"
 *          tomDaSituacao('abaixo') → "atencao"
 *          tomDaSituacao('outra_coisa') → "neutro"
 */
export function tomDaSituacao(situacao) {
  switch (situacao) {
    case 'acima':
      return 'positivo';

    case 'abaixo':
      return 'atencao';

    case 'na_media':
      return 'neutro';

    case 'indisponivel':
      return 'neutro';

    default:
      // Qualquer valor fora do contrato cai no tom discreto.
      return 'neutro';
  }
}
