/**
 * Menu de usuário do cabeçalho (Diego / Patrícia).
 *
 * Mostra quem está usando o sistema: círculo com as iniciais, o nome e, logo
 * abaixo, o cargo. A seta ao lado abre um painel com a OUTRA pessoa; escolher
 * troca a visão do app (gerente ↔ regional).
 *
 * O sistema não tem login: são os dois perfis da demonstração. A visão em uso
 * fica no contexto (estado.visao) e é trocada pela ação mudarVisao.
 */

import { ChevronDown, ChevronUp } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { useApp } from '../context/useApp.js';
import { iniciaisDoNome } from '../utilitarios/seletorColaborador.js';
import { outrosUsuarios, usuarioDaVisao } from '../utilitarios/usuarios.js';

// Importa o CSS deste componente.
import './MenuUsuario.css';

/**
 * Componente MenuUsuario.
 *
 * Não recebe props: lê a visão atual do contexto e chama mudarVisao.
 *
 * Devolve a identificação do usuário ativo e a seta que abre/fecha o painel
 * com as outras opções.
 *
 * Exemplo de uso: <MenuUsuario />
 */
export function MenuUsuario() {
  const { estado, mudarVisao } = useApp();

  /*
   * Estado local: o painel está aberto?
   *
   * "Estado local" é a informação que só este componente usa e que, quando
   * muda, faz ele se desenhar de novo.
   */
  const [aberto, setAberto] = useState(false);

  /*
   * useRef: uma "caixinha" que guarda um elemento da tela entre renderizações
   * sem provocar nova renderização. Guardamos:
   * - o container inteiro, para saber se um clique foi DENTRO ou FORA;
   * - o botão da seta, para devolver o foco quando o menu fecha.
   */
  const containerRef = useRef(null);
  const botaoSetaRef = useRef(null);

  // Usuário da visão atual e a lista com as outras opções (só uma).
  const atual = usuarioDaVisao(estado.visao);
  const outros = outrosUsuarios(estado.visao);

  /*
   * useEffect: roda um código depois que a tela aparece.
   *
   * Aqui ele liga o "clique fora": quando o painel está aberto, clicar em
   * qualquer lugar da página fecha o menu — comportamento esperado de
   * qualquer menu suspenso.
   *
   * O listener fica no documento (document) porque o clique pode acontecer em
   * qualquer lugar. Ele é REMOVIDO na função de limpeza (o return), que roda
   * quando o menu fecha ou o componente sai da tela; sem isso, ficaria um
   * espião acumulado a cada abertura.
   *
   * O clique na própria seta também chega no documento, mas o container
   * contém a seta, então o menu NÃO fecha — quem alterna é o onClick dela.
   */
  useEffect(() => {
    if (!aberto) {
      return undefined;
    }

    function aoClicarFora(evento) {
      // contains devolve true quando o alvo do clique está dentro do menu.
      if (containerRef.current?.contains(evento.target)) {
        return;
      }

      setAberto(false);
    }

    document.addEventListener('click', aoClicarFora);

    return () => {
      document.removeEventListener('click', aoClicarFora);
    };
  }, [aberto]);

  /**
   * Fecha o painel e devolve o foco para a seta.
   *
   * "Foco" é o lugar onde o teclado está agindo. Quando o painel some, o
   * elemento focado pode deixar de existir; devolver o foco mantém a pessoa
   * que usa teclado no mesmo lugar.
   */
  function fecharPainel() {
    setAberto(false);
    botaoSetaRef.current?.focus();
  }

  /**
   * Escolhe a outra pessoa: troca a visão, fecha o painel e devolve o foco.
   *
   * Recebe a visão do usuário escolhido. Quem guarda a visão é o contexto, e
   * o resto da tela (barra lateral, páginas) reage sozinho à mudança.
   */
  function escolherUsuario(visao) {
    mudarVisao(visao);
    setAberto(false);
    botaoSetaRef.current?.focus();
  }

  /**
   * Trata o teclado no menu.
   *
   * Esc fecha o painel e devolve o foco à seta. Outras teclas seguem o
   * comportamento normal (Tab anda pelos botões, Enter/Espaço acionam).
   */
  function aoTeclar(evento) {
    if (evento.key !== 'Escape' || !aberto) {
      return;
    }

    evento.preventDefault();
    fecharPainel();
  }

  return (
    /*
     * position: relative (no CSS) faz deste container a "âncora" do painel:
     * o painel absoluto é posicionado em relação a ele, e não à página.
     * O onKeyDown fica aqui porque os eventos do teclado sobem dos filhos
     * (botão da seta e opções) até este elemento.
     */
    <div
      ref={containerRef}
      className="menu-usuario"
      onKeyDown={aoTeclar}
    >
      {/* Identificação do usuário ativo: círculo, nome e cargo embaixo. */}
      <span className="menu-usuario__identificacao">
        <span className="menu-usuario__avatar" aria-hidden="true">
          {iniciaisDoNome(atual.nome)}
        </span>

        <span className="menu-usuario__texto">
          <span className="menu-usuario__nome">{atual.nome}</span>
          <span className="menu-usuario__cargo">{atual.cargo}</span>
        </span>
      </span>

      {/*
       * Botão só com a seta. aria-label dá o nome falado; aria-expanded avisa
       * se o painel está aberto (padrão "disclosure"); aria-controls aponta
       * para o id do painel.
       */}
      <button
        ref={botaoSetaRef}
        type="button"
        className="menu-usuario__seta"
        aria-label="Trocar de usuário"
        aria-expanded={aberto}
        aria-controls="painel-menu-usuario"
        onClick={() => setAberto((estavaAberto) => !estavaAberto)}
      >
        {aberto ? (
          <ChevronUp aria-hidden="true" />
        ) : (
          <ChevronDown aria-hidden="true" />
        )}
      </button>

      {/*
       * Painel com as outras opções. position: absolute no CSS o coloca logo
       * abaixo do menu, alinhado à direita, sem empurrar o conteúdo da página.
       */}
      {aberto && (
        <ul
          id="painel-menu-usuario"
          className="menu-usuario__painel"
          aria-label="Outros usuários"
        >
          {outros.map((usuario) => (
            <li key={usuario.visao}>
              <button
                type="button"
                className="menu-usuario__opcao"
                onClick={() => escolherUsuario(usuario.visao)}
              >
                <span
                  className="menu-usuario__avatar menu-usuario__avatar--opcao"
                  aria-hidden="true"
                >
                  {iniciaisDoNome(usuario.nome)}
                </span>

                <span className="menu-usuario__texto">
                  <span className="menu-usuario__nome">
                    {usuario.nome}
                  </span>
                  <span className="menu-usuario__cargo">
                    {usuario.cargo}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
