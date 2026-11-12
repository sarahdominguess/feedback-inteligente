/**
 * Abas de navegação: Feedback, Anotações e Dados.
 *
 * Aparecem empilhadas (uma embaixo da outra) nas DUAS visões. A aba ativa vem
 * do contexto (fonte única de verdade) e pode ser trocada por clique ou pelas
 * setas do teclado.
 */

import { ChartColumn, NotebookPen, Sparkles } from 'lucide-react';
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
 * Ordem visual das abas, de cima para baixo. É esta lista que as setas do
 * teclado percorrem.
 *
 * Feedback vem primeiro porque é o fluxo principal do gerente (preparar o
 * roteiro da conversa); as outras duas abas dão apoio a ele.
 */
const ORDEM_ABAS = [ABAS.FEEDBACK, ABAS.ANOTACOES, ABAS.DADOS];

/**
 * Ícone de cada aba, ligado pelo valor técnico de ABAS.
 *
 * Os componentes vêm do pacote lucide-react (biblioteca de ícones em SVG).
 * São decorativos: quem diz o nome da aba é o texto ao lado, por isso eles
 * entram na tela com aria-hidden (explicado no JSX, mais abaixo).
 */
const ICONES_ABAS = {
  [ABAS.FEEDBACK]: Sparkles,
  [ABAS.ANOTACOES]: NotebookPen,
  [ABAS.DADOS]: ChartColumn,
};

/**
 * Componente NavegacaoAbas.
 *
 * Recebe uma prop opcional:
 *   recolhida: quando true, cada aba mostra SÓ o ícone (a barra lateral está
 *     recolhida). O nome continua no DOM, escondido da tela pela classe
 *     ui-visualmente-oculto, e também vira "title" (a dica que aparece ao
 *     passar o mouse). Assim leitores de tela e mouse continuam sabendo o
 *     nome de cada aba.
 *
 * Também lê do contexto a aba atual e a ação mudarAba. O rótulo do conjunto
 * muda conforme a visão (colaborador ou loja), mas a aba escolhida é a MESMA
 * do estado global.
 *
 * Devolve a lista vertical com três botões no papel de abas (role="tab"),
 * cada um com ícone e texto.
 *
 * "role" é um atributo que diz ao navegador e ao leitor de tela qual é o
 * papel de um elemento (aqui: lista de abas e cada aba). aria-selected diz
 * qual aba está aberta agora e aria-orientation avisa que a fila é vertical.
 *
 * Exemplo de uso: <NavegacaoAbas recolhida={false} />
 */
export function NavegacaoAbas({ recolhida = false }) {
  const { estado, mudarAba } = useApp();

  // useRef guarda a referência dos três botões para conseguir mover o foco
  // do teclado de um para outro.
  const botoesRef = useRef([]);

  // O rótulo do conjunto fala de colaborador ou de loja, conforme a visão.
  const ehRegional = estado.visao === VISOES.REGIONAL;

  /**
   * Trata as setas do teclado dentro da lista de abas.
   *
   * Recebe o evento do teclado e a posição da aba que estava com foco.
   * Devolve nada: troca a aba no contexto e move o foco para o novo botão.
   *
   * Como as abas ficam empilhadas, o movimento natural é ↑ e ↓. As setas
   * ← e → continuam funcionando porque parte das pessoas (e dos leitores de
   * tela) está acostumada com o padrão de abas lado a lado; aceitar as duas
   * duplas não atrapalha ninguém.
   *
   * A conta com "%" (resto da divisão) faz a navegação dar a volta: da
   * última aba, a seta para baixo leva para a primeira, e vice-versa.
   */
  function aoTeclar(evento, indice) {
    const total = ORDEM_ABAS.length;
    let proximoIndice = null;

    if (evento.key === 'ArrowDown' || evento.key === 'ArrowRight') {
      proximoIndice = (indice + 1) % total;
    } else if (evento.key === 'ArrowUp' || evento.key === 'ArrowLeft') {
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
      className={
        recolhida
          ? 'navegacao-abas navegacao-abas--recolhida'
          : 'navegacao-abas'
      }
      role="tablist"
      // Avisa ao leitor de tela que a fila é vertical (↑/↓), e não lado a lado.
      aria-orientation="vertical"
      aria-label={ehRegional ? 'Seções da loja' : 'Seções do colaborador'}
    >
      {ORDEM_ABAS.map((valor, indice) => {
        const ativa = valor === estado.aba;

        // Cada aba usa o seu próprio ícone. A variável começa com maiúscula
        // porque, em JSX, componente sempre começa com letra maiúscula.
        const Icone = ICONES_ABAS[valor];

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
             * title: dica que aparece ao passar o mouse. Só faz sentido com a
             * barra recolhida, quando o nome não está escrito na tela.
             */
            title={recolhida ? ROTULOS_ABAS[valor] : undefined}
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
            {/*
             * Ícone decorativo: aria-hidden impede que o leitor de tela
             * anuncie um "desenho" antes do nome que o texto já informa.
             */}
            <span className="navegacao-abas__icone" aria-hidden="true">
              <Icone />
            </span>

            {/*
             * Nome da aba.
             *
             * Com a barra recolhida, o texto continua no DOM (escondido pela
             * classe ui-visualmente-oculto): leitores de tela ainda o
             * anunciam, e nada se perde de acessibilidade.
             */}
            <span
              className={
                recolhida
                  ? 'ui-visualmente-oculto'
                  : 'navegacao-abas__texto'
              }
            >
              {ROTULOS_ABAS[valor]}
            </span>
          </button>
        );
      })}
    </div>
  );
}
