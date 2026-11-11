/**
 * Abas do gerente: Anotações, Dados e Feedback.
 *
 * Só aparecem na visão do gerente. A aba ativa vem do contexto (fonte única
 * de verdade) e pode ser trocada por clique ou pelas setas do teclado.
 */

import { useRef } from 'react';

import {
  ABAS,
  ID_PAINEL_ABAS,
  ROTULOS_ABAS,
  VISOES,
} from '../constantes.js';
import { useApp } from '../context/useApp.js';

// Importa o CSS deste componente.
import './NavegacaoAbas.css';

/**
 * Ordem visual das abas. É esta lista que as setas do teclado percorrem.
 */
const ORDEM_ABAS = [ABAS.ANOTACOES, ABAS.DADOS, ABAS.FEEDBACK];

/**
 * Componente NavegacaoAbas.
 *
 * Não recebe props: lê do contexto a aba atual e a ação mudarAba. Também
 * confere a visão, porque as abas são exclusivas do gerente.
 *
 * Devolve uma barra com três botões no papel de abas (role="tab").
 *
 * "role" é um atributo que diz ao navegador e ao leitor de tela qual é o
 * papel de um elemento (aqui: lista de abas e cada aba). aria-selected diz
 * qual aba está aberta agora.
 *
 * Exemplo de uso: <NavegacaoAbas />
 */
export function NavegacaoAbas() {
  const { estado, mudarAba } = useApp();

  // useRef guarda a referência dos três botões para conseguir mover o foco
  // do teclado de um para outro.
  const botoesRef = useRef([]);

  // Na visão regional não existem abas: o componente não desenha nada.
  if (estado.visao !== VISOES.GERENTE) {
    return null;
  }

  /**
   * Trata as setas esquerda/direita dentro da lista de abas.
   *
   * Recebe o evento do teclado e a posição da aba que estava com foco.
   * Devolve nada: troca a aba no contexto e move o foco para o novo botão.
   *
   * A conta com "%" (resto da divisão) faz a navegação dar a volta: da
   * última aba, a seta direita leva para a primeira, e vice-versa.
   */
  function aoTeclar(evento, indice) {
    const total = ORDEM_ABAS.length;
    let proximoIndice = null;

    if (evento.key === 'ArrowRight') {
      proximoIndice = (indice + 1) % total;
    } else if (evento.key === 'ArrowLeft') {
      proximoIndice = (indice - 1 + total) % total;
    } else {
      // Outra tecla: o comportamento normal do botão continua valendo.
      return;
    }

    // Evita que a seta também role a página.
    evento.preventDefault();

    // Atualiza o estado (uma única fonte de verdade) e leva o foco junto.
    mudarAba(ORDEM_ABAS[proximoIndice]);
    botoesRef.current[proximoIndice]?.focus();
  }

  return (
    // role="tablist" marca o conjunto de abas.
    <div
      className="navegacao-abas"
      role="tablist"
      aria-label="Seções do colaborador"
    >
      {ORDEM_ABAS.map((valor, indice) => {
        const ativa = valor === estado.aba;

        return (
          <button
            key={valor}
            /*
             * O ref guarda o botão na posição dele para o foco por seta.
             * A função não devolve nada de propósito (um retorno seria
             * tratado pelo React como função de limpeza).
             */
            ref={(elemento) => {
              botoesRef.current[indice] = elemento;
            }}
            type="button"
            role="tab"
            // id liga a aba ao painel; aria-controls aponta para o painel.
            id={`aba-${valor}`}
            aria-selected={ativa}
            aria-controls={ID_PAINEL_ABAS}
            /*
             * Roving tabindex: só a aba ativa entra na ordem do Tab (0); as
             * outras valem -1 e são alcançadas pelas setas. Isso evita que
             * o Tab pare em cada aba antes de chegar ao conteúdo.
             */
            tabIndex={ativa ? 0 : -1}
            className={
              ativa
                ? 'navegacao-abas__aba navegacao-abas__aba--ativa'
                : 'navegacao-abas__aba'
            }
            onClick={() => mudarAba(valor)}
            onKeyDown={(evento) => aoTeclar(evento, indice)}
          >
            {ROTULOS_ABAS[valor]}
          </button>
        );
      })}
    </div>
  );
}
