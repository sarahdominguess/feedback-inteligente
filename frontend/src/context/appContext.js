/**
 * Contexto global da aplicação.
 *
 * Context (React): um jeito de compartilhar dados (estado e ações) entre
 * vários componentes sem passá-los de pai para filho, um a um. O valor é
 * criado aqui e preenchido pelo AppProvider.
 */

import { createContext } from 'react';

/**
 * Guarda o valor compartilhado: { estado, carregarVendedores, ... }.
 * O valor inicial null permite ao hook useApp detectar uso fora do Provider.
 */
export const AppContext = createContext(null);
