/**
 * Cabeçalho fixo do app.
 *
 * Em toda a largura: à esquerda a identidade do produto (título e subtítulo)
 * e, à direita, a área do usuário — por enquanto com os botões que alternam
 * entre as visões do gerente e da regional (o menu de usuário entra na
 * próxima fatia). Em telas estreitas o conteúdo quebra em duas linhas.
 */

import { VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';

// Importa o CSS deste componente.
import './Cabecalho.css';

/**
 * Componente Cabecalho.
 *
 * Não recebe props: lê do contexto com o useApp() a visão atual e a ação que
 * troca de visão. O estado é a única fonte de verdade — não há estado local.
 *
 * O título é o único h1 da página e o subtítulo é fixo (não muda com a
 * visão). A área do usuário fica à direita, num bloco próprio, para receber
 * o menu de usuário sem mexer no resto do cabeçalho.
 *
 * Exemplo de uso: <Cabecalho />
 */
export function Cabecalho() {
  const { estado, mudarVisao } = useApp();

  // Duas variáveis curtas deixam o JSX mais legível e evitam repetir a
  // comparação em cada botão.
  const gerenteAtivo = estado.visao === VISOES.GERENTE;
  const regionalAtivo = estado.visao === VISOES.REGIONAL;

  return (
    <header className="cabecalho">
      {/* Identidade do produto: título e subtítulo, à esquerda. */}
      <div className="cabecalho__identidade">
        <h1 className="cabecalho__titulo">Feedback Inteligente</h1>
        <p className="cabecalho__subtitulo">
          Assistente de IA para feedback
        </p>
      </div>

      {/*
       * Área do usuário, à direita. Por enquanto guarda o alternador de
       * visão; na próxima fatia ela passa a mostrar quem está usando o
       * sistema (Diego ou Patrícia).
       */}
      <div className="cabecalho__area-usuario">
        {/*
         * Alternador de visão. role="group" avisa ao leitor de tela que os
         * dois botões formam um grupo; aria-label dá um nome a esse grupo.
         */}
        <div
          className="cabecalho__visoes"
          role="group"
          aria-label="Escolher visão"
        >
          {/*
           * aria-pressed="true" informa que a visão está ativa. O valor é
           * booleano, então o React escreve "true"/"false" sozinho.
           */}
          <button
            type="button"
            className={
              gerenteAtivo
                ? 'cabecalho__botao cabecalho__botao--ativo'
                : 'cabecalho__botao'
            }
            aria-pressed={gerenteAtivo}
            onClick={() => mudarVisao(VISOES.GERENTE)}
          >
            Gerente
          </button>

          <button
            type="button"
            className={
              regionalAtivo
                ? 'cabecalho__botao cabecalho__botao--ativo'
                : 'cabecalho__botao'
            }
            aria-pressed={regionalAtivo}
            onClick={() => mudarVisao(VISOES.REGIONAL)}
          >
            Regional
          </button>
        </div>
      </div>
    </header>
  );
}
