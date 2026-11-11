/**
 * Constantes compartilhadas do frontend.
 *
 * Aqui ficam os valores fixos usados por várias partes do app (reducer,
 * contexto e telas), num lugar só, para não haver texto "solto" repetido e
 * divergente pelo código.
 */

/**
 * Loja usada quando nada foi escolhido: L004, a loja do Diego.
 * O backend só atende essa loja hoje; mudar aqui é o ponto único de troca.
 */
export const LOJA_PADRAO_ID = 'L004';

/**
 * Situação de um pedaço de dados que vem da API.
 *
 * - ocioso: ainda não pedimos nada;
 * - carregando: pedido em andamento;
 * - sucesso: chegou tudo certo;
 * - erro: o pedido falhou (a mensagem fica em estado.erro).
 */
export const STATUS = {
  OCIOSO: 'ocioso',
  CARREGANDO: 'carregando',
  SUCESSO: 'sucesso',
  ERRO: 'erro',
};

/**
 * Abas da tela do gerente (o que aparece no centro da página).
 *
 * - anotacoes: o que o gerente escreveu sobre a pessoa;
 * - dados: indicadores e comparativo com o time;
 * - feedback: geração e leitura do roteiro.
 */
export const ABAS = {
  ANOTACOES: 'anotacoes',
  DADOS: 'dados',
  FEEDBACK: 'feedback',
};

/**
 * Rótulos em português das abas, indexados pelo valor técnico de ABAS.
 *
 * Ficam aqui porque duas partes usam o mesmo texto: a navegação (botões) e a
 * área central (aviso "Aba ... em construção"). Assim os dois nunca divergem.
 */
export const ROTULOS_ABAS = {
  [ABAS.ANOTACOES]: 'Anotações',
  [ABAS.DADOS]: 'Dados',
  [ABAS.FEEDBACK]: 'Feedback',
};

/**
 * Identificador do painel de conteúdo das abas (usado pelo ARIA).
 *
 * A aba aponta para este id com aria-controls e o painel aponta de volta para
 * a aba com aria-labelledby. Fica num lugar só para os dois combinarem.
 */
export const ID_PAINEL_ABAS = 'painel-aba';

/**
 * Visões do sistema (quem está olhando a tela).
 *
 * - gerente: Diego prepara o feedback de um vendedor;
 * - regional: Patrícia acompanha a loja como um todo.
 */
export const VISOES = {
  GERENTE: 'gerente',
  REGIONAL: 'regional',
};

/**
 * Vendedora usada como foco do cenário da demo: Bianca Rocha (C0031).
 *
 * Serve apenas para a lateral já abrir com ela selecionada quando a lista
 * carregar. É uma conveniência de tela, não uma regra de negócio: se esse ID
 * não estiver na lista devolvida pela API, ninguém é selecionado.
 */
export const VENDEDOR_FOCO_ID = 'C0031';
