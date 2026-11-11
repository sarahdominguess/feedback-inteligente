/**
 * Barra lateral do gerente.
 *
 * Junta o título "Equipe", a lista de colaboradores e as abas da pessoa
 * escolhida. É aqui que o gerente escolhe quem ver e o que ver. Só existe na
 * visão do gerente.
 */

import { VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { ListaColaboradores } from './ListaColaboradores.jsx';
import { NavegacaoAbas } from './NavegacaoAbas.jsx';

// Importa o CSS deste componente.
import './BarraLateral.css';

/**
 * Componente BarraLateral.
 *
 * Não recebe props: lê do contexto a visão atual e o colaborador escolhido.
 *
 * Devolve um bloco lateral com:
 *   - o título "Equipe";
 *   - a ListaColaboradores (que cuida dos estados de carregando/erro/vazio);
 *   - as abas, apenas quando há um colaborador selecionado.
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
    // aria-labelledby liga o bloco ao título "Equipe" para o leitor de tela.
    <aside className="barra-lateral" aria-labelledby="titulo-equipe">
      <h2 id="titulo-equipe" className="barra-lateral__titulo">
        Equipe
      </h2>

      {/* Lista com os colaboradores da loja e seus estados. */}
      <ListaColaboradores />

      {/*
       * Abas logo abaixo da lista: aparecem só quando há alguém selecionado,
       * porque são as seções daquela pessoa (anotações, dados, feedback).
       */}
      {temSelecionado && <NavegacaoAbas />}
    </aside>
  );
}
