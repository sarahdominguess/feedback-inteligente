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
 * A ordem dos itens aqui é a MESMA ordem usada na tela (documentação viva):
 * Feedback primeiro, porque é o fluxo principal do gerente; depois Anotações,
 * que alimentam o roteiro; por último Dados, os indicadores.
 *
 * - feedback: geração e leitura do roteiro de feedback;
 * - anotacoes: o que o gerente escreveu sobre a pessoa;
 * - dados: indicadores e comparativo com o time.
 */
export const ABAS = {
  FEEDBACK: 'feedback',
  ANOTACOES: 'anotacoes',
  DADOS: 'dados',
};

/**
 * Rótulos em português das abas, indexados pelo valor técnico de ABAS.
 *
 * Ficam aqui porque a navegação (botões) e a área central (título do painel)
 * usam o mesmo texto. Assim os dois nunca divergem.
 */
export const ROTULOS_ABAS = {
  // Mesma ordem das abas: Feedback, Anotações, Dados.
  [ABAS.FEEDBACK]: 'Feedback',
  [ABAS.ANOTACOES]: 'Anotações',
  [ABAS.DADOS]: 'Dados',
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
 * Perfis de usuário da demonstração (menu do canto superior direito).
 *
 * O sistema NÃO tem login: estes são os dois perfis do cenário do desafio.
 * Escolher um deles no menu troca a VISÃO do app (gerente ou regional) — e a
 * visão já é guardada pelo contexto, então nada é salvo aqui.
 *
 * Aqui vai só o PRIMEIRO NOME, que é o que aparece no menu. Em outros pontos
 * da tela (ex.: anotações da regional) o nome completo continua vindo da API
 * ("Diego Furtado", "Patrícia Lemos").
 */
export const USUARIOS = [
  { visao: VISOES.GERENTE, nome: 'Diego', cargo: 'Gerente' },
  { visao: VISOES.REGIONAL, nome: 'Patrícia', cargo: 'Regional' },
];

/**
 * Limite de caracteres de uma anotação nova — só para ORIENTAR na tela.
 *
 * Serve para o contador e para o maxLength do campo de escrita. O limite de
 * verdade é validado pelo BACKEND (backend/config.py, ANOTACAO_TEXTO_MAXIMO):
 * se os dois números divergirem, quem manda é o backend, que responde 400 com
 * uma mensagem clara. Este valor existe para a pessoa ver quando está
 * chegando no fim antes de tentar enviar.
 */
export const ANOTACAO_TEXTO_MAXIMO = 1000;

/**
 * Vendedora usada como foco do cenário da demo: Bianca Rocha (C0031).
 *
 * Serve apenas para a lateral já abrir com ela selecionada quando a lista
 * carregar. É uma conveniência de tela, não uma regra de negócio: se esse ID
 * não estiver na lista devolvida pela API, ninguém é selecionado.
 */
export const VENDEDOR_FOCO_ID = 'C0031';

/**
 * Créditos do projeto, mostrados no rodapé.
 *
 * AUTORA_NOME é o nome que aparece no texto "Desenvolvido por ...".
 * AUTORA_INSTAGRAM é só o nome de usuário, SEM o "@": o componente do rodapé
 * monta o "@" da tela e a URL completa do Instagram a partir daqui. Assim o
 * endereço fica num lugar só e não é digitado à mão em outro arquivo.
 */
export const AUTORA_NOME = 'Sarah Domingues';
export const AUTORA_INSTAGRAM = 'sarahdev.css';
