/**
 * Hook de acesso ao contexto da aplicação.
 *
 * Hook: função especial do React cujo nome começa com "use". Só pode ser
 * chamada dentro de componentes ou de outros hooks.
 */

import { useContext } from 'react';

import { AppContext } from './appContext.js';

/**
 * Devolve o estado e as ações compartilhadas.
 *
 * Precisa ser usado dentro de <AppProvider>. Fora dele, o contexto vale null
 * e lançamos um erro em português para o problema aparecer claro em vez de
 * virar um "cannot read property of null" no meio da tela.
 */
export function useApp() {
  const valor = useContext(AppContext);

  if (valor === null) {
    throw new Error(
      'useApp precisa ser usado dentro de <AppProvider>. Verifique se o componente está envolvido pelo provider em main.jsx.',
    );
  }

  return valor;
}
