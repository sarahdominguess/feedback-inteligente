/**
 * Cabeçalho fixo do app.
 *
 * Mostra o nome do produto, o subtítulo e o alternador entre as visões do
 * gerente e da regional. A visão ativa vem do estado do contexto.
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
 * Observação sobre o nome da loja: a API devolve "loja_nome", mas o reducer
 * guarda apenas a lista de vendedores. Como o nome não está no estado, ele
 * NÃO é exibido aqui (não inventamos texto). Se um dia o estado passar a
 * guardar a loja, basta acrescentar a linha correspondente no JSX.
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
      {/* Bloco de identidade do produto: título e subtítulo. */}
      <div className="cabecalho__identidade">
        <h1 className="cabecalho__titulo">Feedback Inteligente</h1>
        <p className="cabecalho__subtitulo">
          Co-piloto de feedback para a liderança da Rede Aurora
        </p>
      </div>

      {/*
       * Alternador de visão. role="group" avisa ao leitor de tela que os dois
       * botões formam um grupo; aria-label dá um nome a esse grupo.
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
    </header>
  );
}
