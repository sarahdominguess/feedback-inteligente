/**
 * Barra lateral (menu do colaborador).
 *
 * Em coluna: botão que expande/recolhe, as abas da pessoa escolhida e o card
 * que mostra quem está selecionado. Expandida mostra ícone + texto; recolhida
 * mostra só os ícones, para sobrar espaço ao conteúdo. Só existe na visão do
 * gerente.
 *
 * A preferência NÃO é guardada entre visitas: cada abertura do app começa
 * expandida em telas largas e recolhida no celular.
 */

import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { useState } from 'react';

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
 */
const ID_TITULO_LATERAL = 'titulo-menu-colaborador';

/**
 * Identificador do bloco que o botão de alternar mostra/esconde.
 *
 * Usado no aria-controls do botão: ele avisa ao leitor de tela qual bloco
 * muda quando o botão é acionado.
 */
const ID_CONTEUDO_LATERAL = 'conteudo-menu-colaborador';

/**
 * Diz se a tela é larga o bastante para a barra começar expandida.
 *
 * matchMedia ("media query" no JavaScript) pergunta ao navegador se a tela
 * atende a uma condição — aqui, "768px ou mais". No celular a resposta é
 * false, e a barra começa RECOLHIDA: o conteúdo precisa do espaço.
 * A verificação de existência protege ambientes onde matchMedia não existe
 * (testes no Node, por exemplo): nesse caso, começamos expandidos.
 */
function telaLarga() {
  if (
    typeof window === 'undefined' ||
    typeof window.matchMedia !== 'function'
  ) {
    return true;
  }

  return window.matchMedia('(min-width: 768px)').matches;
}

/**
 * Componente BarraLateral.
 *
 * Não recebe props: lê do contexto a visão atual e o colaborador escolhido.
 * Guarda no estado local se está expandida ou recolhida.
 *
 * Devolve:
 *   - o botão de alternar (sempre visível, no topo);
 *   - as abas, apenas quando há um colaborador selecionado;
 *   - o SeletorColaborador, SEMPRE montado — é ele que carrega a lista de
 *     vendedores e escolhe a Bianca automaticamente na demo, mesmo recolhido.
 *
 * Exemplo de uso: <BarraLateral />
 */
export function BarraLateral() {
  const { estado } = useApp();

  /*
   * Estado local: a barra está expandida?
   *
   * O valor inicial vem de uma FUNÇÃO, para ser calculado uma única vez, na
   * primeira renderização. Ela não é recalculada quando a janela muda de
   * tamanho depois — a pessoa é quem decide, clicando no botão.
   */
  const [expandida, setExpandida] = useState(telaLarga);

  // Na visão regional não existe escolha de colaborador: nada é desenhado.
  if (estado.visao !== VISOES.GERENTE) {
    return null;
  }

  // As abas fazem sentido depois que existe uma pessoa escolhida.
  const temSelecionado = Boolean(estado.vendedorSelecionadoId);

  /**
   * Alterna entre expandida e recolhida.
   *
   * Usa a forma de atualização por função (valor anterior => novo valor):
   * é a maneira segura de trocar um estado booleano sem depender do valor
   * que estava na tela no momento do clique.
   */
  function alternarBarra() {
    setExpandida((estavaExpandida) => !estavaExpandida);
  }

  return (
    // aria-labelledby liga o bloco ao título (invisível) do menu.
    <aside
      className={
        expandida
          ? 'barra-lateral'
          : 'barra-lateral barra-lateral--recolhida'
      }
      aria-labelledby={ID_TITULO_LATERAL}
    >
      {/*
       * Título acessível: não ocupa espaço na tela, mas leitores de tela
       * anunciam "Menu do colaborador" ao entrar na região.
       */}
      <h2 id={ID_TITULO_LATERAL} className="ui-visualmente-oculto">
        Menu do colaborador
      </h2>

      {/*
       * Botão de alternar. aria-label dá o nome falado (só há ícone);
       * aria-expanded avisa se o bloco está aberto (padrão "disclosure");
       * aria-controls aponta para o id do conteúdo que ele mostra/esconde.
       */}
      <button
        type="button"
        className="barra-lateral__alternar"
        aria-label={expandida ? 'Recolher menu' : 'Expandir menu'}
        aria-expanded={expandida}
        aria-controls={ID_CONTEUDO_LATERAL}
        onClick={alternarBarra}
      >
        {/* Ícone decorativo: o nome vem do aria-label do botão. */}
        {expandida ? (
          <PanelLeftClose aria-hidden="true" />
        ) : (
          <PanelLeftOpen aria-hidden="true" />
        )}
      </button>

      {/*
       * Conteúdo visível do menu, num bloco próprio para poder ficar
       * "sticky" (grudado no topo) enquanto a página rola — ver o CSS.
       * A prop "recolhida" avisa os filhos para mostrarem só os ícones.
       */}
      <div id={ID_CONTEUDO_LATERAL} className="barra-lateral__conteudo">
        {temSelecionado && <NavegacaoAbas recolhida={!expandida} />}

        <SeletorColaborador
          recolhida={!expandida}
          // Clicar no círculo do colaborador com a barra recolhida expande a
          // barra (é o único controle que faz sentido nesse estado).
          aoExpandir={() => setExpandida(true)}
        />
      </div>
    </aside>
  );
}
