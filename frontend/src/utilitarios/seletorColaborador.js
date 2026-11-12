/**
 * Funções de apoio do seletor de colaborador.
 *
 * Aqui ficam apenas contas e filtros em cima da lista de vendedores que vem
 * da API: as iniciais para o avatar, achar uma pessoa pelo código e listar as
 * outras (para trocar). Função pura: recebe dados e devolve resultado, sem
 * React, sem rede e sem alterar o que recebeu.
 */

/**
 * Verifica se um código de colaborador serve para busca.
 *
 * Recebe o valor recebido e devolve true só quando é texto com algo além de
 * espaços. Serve para as duas funções abaixo recusarem id vazio, null ou
 * número sem repetir a mesma checagem.
 *
 * Exemplo: idValido('C0031') devolve true; idValido('   ') devolve false.
 */
function idValido(id) {
  return typeof id === 'string' && id.trim() !== '';
}

/**
 * Monta as iniciais de um nome, para o avatar redondo do card.
 *
 * Recebe o nome completo (texto). Devolve até DUAS letras maiúsculas: a
 * primeira letra do primeiro nome e a primeira do último nome. Nomes de uma
 * palavra só devolvem uma letra. Texto vazio, só com espaços ou que não é
 * texto devolve "?" (assim a tela nunca fica com um círculo em branco).
 *
 * Espaços extras e repetidos no meio do nome são ignorados.
 *
 * Exemplos:
 *   iniciaisDoNome('Bianca Rocha')   → 'BR'
 *   iniciaisDoNome('  cher  ')       → 'C'
 *   iniciaisDoNome('Ana Maria Lima') → 'AL' (primeiro e ÚLTIMO nome)
 *   iniciaisDoNome('')               → '?'
 */
export function iniciaisDoNome(nome) {
  // Entrada que não é texto não pode quebrar a tela.
  if (typeof nome !== 'string') {
    return '?';
  }

  /*
   * trim() remove os espaços das pontas; split(/\s+/) corta o nome em partes
   * separando por um ou mais espaços; filter(Boolean) joga fora pedaços
   * vazios. Resultado: só os nomes de verdade, sem sujeira.
   */
  const partes = nome.trim().split(/\s+/).filter(Boolean);

  // Nome vazio (ou só espaços): não há letra para mostrar.
  if (partes.length === 0) {
    return '?';
  }

  // Primeira letra do primeiro nome.
  const primeira = partes[0].charAt(0);

  // Nome de uma palavra só (ex.: "Cher"): devolve apenas essa letra.
  // Sem esta saída, a letra seria somada duas vezes e viraria "CC".
  if (partes.length === 1) {
    return primeira.toUpperCase();
  }

  // A última parte é o sobrenome (o que fica entre o primeiro e o último
  // nome não entra nas iniciais).
  const ultima = partes[partes.length - 1].charAt(0);

  // toUpperCase garante maiúsculas mesmo se o nome vier em minúsculas.
  return (primeira + ultima).toUpperCase();
}

/**
 * Procura um colaborador na lista pelo código.
 *
 * Recebe a lista de vendedores (no formato da API, com vendedor_id e nome) e
 * o código procurado. Devolve o item encontrado ou null quando não existe,
 * quando o código é vazio e quando a lista não é uma lista.
 *
 * A comparação é EXATA: "C0031" não encontra "c0031".
 *
 * Exemplo: encontrarColaborador(lista, 'C0031') → { vendedor_id: 'C0031',
 * nome: 'Bianca Rocha', ... }
 */
export function encontrarColaborador(lista, id) {
  // Lista inválida ou código vazio: não há o que procurar.
  if (!Array.isArray(lista) || !idValido(id)) {
    return null;
  }

  /*
   * find percorre a lista e devolve o primeiro item que satisfaz a condição.
   * Quando nada casa, ele devolve undefined; o ?? null transforma isso em
   * null, que é o combinado da função.
   */
  const encontrado = lista.find(
    (colaborador) => colaborador?.vendedor_id === id,
  );

  return encontrado ?? null;
}

/**
 * Lista os colaboradores MENOS o que está selecionado.
 *
 * Recebe a lista de vendedores e o código do selecionado. Devolve uma lista
 * NOVA, na mesma ordem recebida da API (a função não ordena por conta
 * própria, porque a ordem é decisão do backend).
 *
 * Quando o código é vazio/null ou não existe na lista, devolve todos os
 * colaboradores — é o caso de "ainda não escolhi ninguém". Lista inválida
 * devolve lista vazia.
 *
 * A lista original nunca é alterada: filter cria outra lista.
 *
 * Exemplo: outrosColaboradores(lista, 'C0031') devolve a lista sem a Bianca,
 * mantendo os demais na mesma ordem.
 */
export function outrosColaboradores(lista, idSelecionado) {
  // Proteção simples: se a API mudar o formato, a tela mostra o vazio.
  if (!Array.isArray(lista)) {
    return [];
  }

  /*
   * Sem seleção válida, não há ninguém para tirar. O espalhamento ([...lista])
   * devolve uma cópia, para quem chamar não receber o mesmo array da API e
   * acabar alterando o estado sem querer.
   */
  if (!idValido(idSelecionado)) {
    return [...lista];
  }

  // filter mantém tudo o que NÃO é o selecionado (e já devolve lista nova).
  return lista.filter(
    (colaborador) => colaborador?.vendedor_id !== idSelecionado,
  );
}
