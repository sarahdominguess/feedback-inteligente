/**
 * Funções de apoio do seletor de LOJA (visão da regional).
 *
 * Aqui ficam apenas contas e filtros em cima da lista de lojas que vem da API:
 * achar uma loja pelo código, listar as outras (para trocar) e montar a letra
 * do círculo do card. Função pura: recebe dados e devolve resultado, sem
 * React, sem rede e sem alterar o que recebeu.
 */

/**
 * Verifica se um código de loja serve para busca.
 *
 * Recebe o valor recebido e devolve true só quando é texto com algo além de
 * espaços. Serve para as funções abaixo recusarem id vazio, null ou número
 * sem repetir a mesma checagem.
 *
 * Exemplo: idValido('L004') devolve true; idValido('   ') devolve false.
 */
function idValido(id) {
  return typeof id === 'string' && id.trim() !== '';
}

/**
 * Remove acentos e deixa tudo em minúsculas, só para COMPARAR palavras.
 *
 * Recebe um texto e devolve a versão normalizada. Usada para reconhecer
 * "Aurora", "aurora" e "Áurora" como a mesma palavra genérica.
 *
 * Exemplo: normalizar('Áurora') devolve 'aurora'.
 */
function normalizar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
}

/**
 * Procura uma loja na lista pelo código.
 *
 * Recebe a lista de lojas (no formato da API, com loja_id e loja_nome) e o
 * código procurado. Devolve o item encontrado ou null quando não existe,
 * quando o código é vazio e quando a lista não é uma lista.
 *
 * A comparação é EXATA: "L004" não encontra "l004".
 *
 * Exemplo: encontrarLoja(lista, 'L004') → { loja_id: 'L004', ... }
 */
export function encontrarLoja(lista, id) {
  if (!Array.isArray(lista) || !idValido(id)) {
    return null;
  }

  /*
   * find percorre a lista e devolve o primeiro item que satisfaz a condição.
   * Quando nada casa, ele devolve undefined; o ?? null transforma isso em
   * null, que é o combinado da função.
   */
  const encontrada = lista.find((loja) => loja?.loja_id === id);

  return encontrada ?? null;
}

/**
 * Lista as lojas MENOS a que está selecionada.
 *
 * Recebe a lista de lojas e o código da selecionada. Devolve uma lista NOVA,
 * na mesma ordem recebida da API (a função não ordena por conta própria,
 * porque a ordem é decisão do backend).
 *
 * Quando o código é vazio/null ou não existe na lista, devolve todas as
 * lojas — é o caso de "ainda não escolhi nenhuma". Lista inválida devolve
 * lista vazia. A lista original nunca é alterada.
 *
 * Exemplo: outrasLojas(lista, 'L004') devolve a lista sem a L004.
 */
export function outrasLojas(lista, idSelecionado) {
  // Proteção simples: se a API mudar o formato, a tela mostra o vazio.
  if (!Array.isArray(lista)) {
    return [];
  }

  /*
   * Sem seleção válida, não há loja para tirar. O espalhamento ([...lista])
   * devolve uma cópia, para quem chamar não receber o mesmo array da API e
   * acabar alterando o estado sem querer.
   */
  if (!idValido(idSelecionado)) {
    return [...lista];
  }

  // filter mantém tudo o que NÃO é a loja selecionada (e já devolve lista nova).
  return lista.filter((loja) => loja?.loja_id !== idSelecionado);
}

/**
 * Monta a letra do círculo do card para uma loja.
 *
 * Recebe o nome da loja. Devolve UMA letra maiúscula: a inicial da primeira
 * palavra que NÃO seja genérica ("Aurora" e "Shopping" aparecem em todas as
 * lojas da rede e não distinguem nenhuma). Assim "Aurora Shopping Centro"
 * vira "C". A letra mantém o acento quando existe ("Íris" → "Í").
 *
 * Texto vazio, só com espaços, sem nenhuma palavra útil ou que não é texto
 * devolve "?" (a tela nunca fica com um círculo em branco).
 *
 * Exemplos:
 *   iniciaisDaLoja('Aurora Shopping Centro') → 'C'
 *   iniciaisDaLoja('Aurora Shopping Évora')  → 'É'
 *   iniciaisDaLoja('')                       → '?'
 */
export function iniciaisDaLoja(nome) {
  // Entrada que não é texto não pode quebrar a tela.
  if (typeof nome !== 'string') {
    return '?';
  }

  /*
   * trim() remove os espaços das pontas; split(/\s+/) corta por um ou mais
   * espaços; filter(Boolean) joga fora pedaços vazios.
   */
  const partes = nome.trim().split(/\s+/).filter(Boolean);

  // Palavras que não identificam a loja dentro da rede.
  const palavrasGenericas = new Set(['aurora', 'shopping']);

  const uteis = partes.filter(
    (parte) => !palavrasGenericas.has(normalizar(parte)),
  );

  // Nome vazio ou só com palavras genéricas: não há letra para mostrar.
  if (uteis.length === 0) {
    return '?';
  }

  // charAt(0) pega a primeira letra (inclusive acentuada) e toUpperCase sobe
  // a caixa sem perder o acento.
  return uteis[0].charAt(0).toUpperCase();
}
