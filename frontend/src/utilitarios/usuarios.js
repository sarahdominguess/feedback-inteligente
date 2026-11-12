/**
 * Funções de apoio do menu de usuário (Diego/Patrícia).
 *
 * Transformam a constante USUARIOS na informação que o menu precisa: quem
 * está ativo e quem são as outras opções. Função pura: para a mesma entrada
 * devolve sempre a mesma saída, sem React e sem rede.
 */

import { USUARIOS } from '../constantes.js';

/**
 * Devolve o usuário que corresponde a uma visão do app.
 *
 * Recebe a visão atual ("gerente" ou "regional") e devolve o item de USUARIOS
 * com aquela visão. Visão desconhecida (ou vazia) devolve o PRIMEIRO usuário
 * da lista: melhor mostrar Diego do que deixar o canto do cabeçalho vazio.
 *
 * Exemplo: usuarioDaVisao('regional') → { visao: 'regional', nome: 'Patrícia',
 * cargo: 'Regional' }
 */
export function usuarioDaVisao(visao) {
  // find percorre a lista e devolve o primeiro que casa; undefined se nenhum.
  const encontrado = USUARIOS.find((usuario) => usuario.visao === visao);

  // ?? devolve o primeiro usuário quando "encontrado" é null/undefined.
  return encontrado ?? USUARIOS[0];
}

/**
 * Lista os OUTROS usuários (todos menos o da visão atual).
 *
 * Recebe a visão atual e devolve uma lista NOVA, na mesma ordem da constante
 * USUARIOS — a constante original nunca é alterada. Visão desconhecida devolve
 * todos, porque nenhum deles está em uso.
 *
 * Exemplo: outrosUsuarios('gerente') → [{ visao: 'regional', nome: 'Patrícia',
 * cargo: 'Regional' }]
 */
export function outrosUsuarios(visao) {
  // filter já devolve uma lista nova; a constante fica intacta.
  return USUARIOS.filter((usuario) => usuario.visao !== visao);
}
