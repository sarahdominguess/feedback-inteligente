/**
 * Barra lateral do gerente.
 *
 * Em coluna, de cima para baixo: as abas da pessoa escolhida (Feedback,
 * Anotações, Dados) e, por último, o card que mostra quem está selecionado e
 * permite trocar de pessoa. A lista de toda a equipe não existe mais. Só
 * aparece na visão do gerente.
 */

import { VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { NavegacaoAbas } from './NavegacaoAbas.jsx';
import { SeletorColaborador } from './SeletorColaborador.jsx';

// Importa o CSS deste componente.
import './BarraLateral.css';

/**
 * Identificador do título que nomeia a barra lateral.
 *
 * O título é só para leitores de tela (a classe ui-visualmente-oculto o
 * esconde da tela), mas continua ligado ao <aside> por aria-labelledby.
 * Fica numa constante para o id do título e a referência nunca divergirem.
 */
const ID_TITULO_LATERAL = 'titulo-menu-colaborador';

/**
 * Componente BarraLateral.
 *
 * Não recebe props: lê do contexto a visão atual e o colaborador escolhido.
 *
 * Devolve um bloco lateral com:
 *   - as abas, apenas quando há um colaborador selecionado (são as seções
 *     daquela pessoa);
 *   - o SeletorColaborador, SEMPRE montado — é ele que carrega a lista de
 *     vendedores e escolhe a Bianca automaticamente na demo. Se ele só
 *     existisse depois da seleção, ninguém carregaria nada (ovo e galinha).
 *
 * A ordem no DOM é a ordem que aparece na tela: abas primeiro, card depois.
 *
 * Exemplo de uso: <BarraLateral />
 */
export function BarraLateral() {
  const { estado } = useApp();

  // Na visão regional não existe escolha de colaborador: nada é desenhado.
  if (estado.visao !== VISOES.GERENTE) {
    return null;
  }

  // As abas fazem sentido depois que existe uma pessoa escolhida.
  const temSelecionado = Boolean(estado.vendedorSelecionadoId);

  return (
    // aria-labelledby liga o bloco ao título (invisível) do menu.
    <aside className="barra-lateral" aria-labelledby={ID_TITULO_LATERAL}>
      {/*
       * Título acessível: não ocupa espaço na tela, mas leitores de tela
       * anunciam "Menu do colaborador" ao entrar na região.
       */}
      <h2 id={ID_TITULO_LATERAL} className="ui-visualmente-oculto">
        Menu do colaborador
      </h2>

      {/*
       * Conteúdo visível do menu, num bloco próprio para poder ficar
       * "sticky" (grudado no topo) enquanto a página rola — explicado no CSS.
       */}
      <div className="barra-lateral__conteudo">
        {/* Abas da pessoa escolhida (Feedback, Anotações, Dados). */}
        {temSelecionado && <NavegacaoAbas />}

        {/* Card da pessoa escolhida, com a seta para trocar. */}
        <SeletorColaborador />
      </div>
    </aside>
  );
}
