/**
 * Lista dos roteiros já preparados para um colaborador, com seta para abrir.
 *
 * Cada item mostra o período e a data/hora da geração e, ao abrir, o roteiro
 * completo (os quatro cards). Funciona como um "acordeão": só um item fica
 * aberto por vez e clicar no que já está aberto fecha.
 *
 * Recebe por props (os dados que o componente recebe de quem o usa):
 *   roteiros: a lista feedbacks_preparados, já do mais novo para o mais
 *     antigo. A ordem é mantida como veio.
 *   vendedorNome: nome usado dentro do visualizador do roteiro.
 */

import { ChevronDown, ChevronUp } from 'lucide-react';
import { useRef, useState } from 'react';

import {
  descricaoDoRoteiroPreparado,
  roteiroTemConteudo,
  tituloDoRoteiroPreparado,
} from '../utilitarios/roteirosPreparados.js';
import { VisualizadorRoteiro } from './VisualizadorRoteiro.jsx';

// Importa o CSS deste componente.
import './ListaRoteirosPreparados.css';

/**
 * Componente ListaRoteirosPreparados.
 *
 * Devolve uma lista (ul) com um item por roteiro. O controle de abrir/fechar
 * é o botão da seta; o item aberto fica destacado e mostra o roteiro dentro
 * dele mesmo.
 *
 * Exemplo de uso:
 *   <ListaRoteirosPreparados roteiros={preparados} vendedorNome="Bianca" />
 */
export function ListaRoteirosPreparados({ roteiros, vendedorNome }) {
  /*
   * "Estado local" é a informação que só este componente usa e que, quando
   * muda, faz ele se desenhar de novo. Aqui guardamos QUAL item está aberto
   * (null = todos fechados). Como é um valor só, abrir outro fecha o
   * anterior automaticamente — o comportamento de acordeão.
   */
  const [abertoId, setAbertoId] = useState(null);

  /*
   * useRef: uma "caixinha" que guarda elementos da tela entre renderizações
   * sem provocar nova renderização. Guardamos o botão da seta de cada item
   * para conseguir devolver o foco a ele quando o Esc fecha o roteiro.
   */
  const botoesRef = useRef({});

  // Proteção simples: se a lista vier estranha, mostramos uma lista vazia.
  const lista = Array.isArray(roteiros) ? roteiros : [];

  /**
   * Abre o item pedido ou fecha o que já está aberto.
   *
   * Recebe a chave do item (o feedback_id). Devolve nada: só atualiza o
   * estado local usando o valor ANTERIOR (forma segura de atualizar estado
   * que depende do valor antigo).
   */
  function alternar(chave) {
    setAbertoId((atual) => (atual === chave ? null : chave));
  }

  /**
   * Fecha o item e devolve o foco ao botão da seta.
   *
   * Por que devolver o foco: quem navega por teclado precisa continuar no
   * mesmo lugar depois que o bloco desaparece; sem isso o foco "cai" no
   * começo da página.
   */
  function fecharEAbrirFoco(chave) {
    setAbertoId(null);
    botoesRef.current[chave]?.focus();
  }

  /**
   * Trata o teclado dentro de um item.
   *
   * Esc fecha o item aberto e devolve o foco à seta. Outras teclas seguem o
   * comportamento normal (Tab anda entre os controles, Enter aciona botões).
   */
  function aoTeclarNoItem(evento, chave, aberto) {
    if (evento.key !== 'Escape' || !aberto) {
      return;
    }

    evento.preventDefault();
    fecharEAbrirFoco(chave);
  }

  return (
    <ul className="lista-roteiros-preparados">
      {lista.map((item, indice) => {
        /*
         * A chave identifica o item para o React e para o estado de aberto.
         * feedback_id é único na API; o índice é só uma rede de segurança
         * para um registro antigo sem id.
         */
        const chave = item?.feedback_id ?? `preparado-${indice}`;
        const temConteudo = roteiroTemConteudo(item);
        // Só consideramos "aberto" se houver conteúdo para mostrar.
        const aberto = temConteudo && abertoId === chave;

        const titulo = tituloDoRoteiroPreparado(item);
        const idPainel = `roteiro-preparado-${chave}`;

        return (
          <li
            key={chave}
            className={
              aberto
                ? 'lista-roteiros-preparados__item lista-roteiros-preparados__item--aberto'
                : 'lista-roteiros-preparados__item'
            }
            // O Esc é tratado no item inteiro porque o evento do botão sobe
            // até aqui (eventos do React "borbulham" para os pais).
            onKeyDown={(evento) => aoTeclarNoItem(evento, chave, aberto)}
          >
            <div className="lista-roteiros-preparados__cabecalho">
              {/* Identificação do roteiro: período em destaque, data abaixo. */}
              <div className="lista-roteiros-preparados__texto">
                <span className="lista-roteiros-preparados__titulo">
                  {titulo}
                </span>
                <span className="lista-roteiros-preparados__descricao">
                  {descricaoDoRoteiroPreparado(item)}
                </span>
              </div>

              {/*
               * Botão só com ícone: aria-label dá o nome que o leitor de tela
               * fala; aria-expanded avisa se o bloco está aberto (padrão
               * "disclosure"); aria-controls aponta para o id do conteúdo.
               * Sem conteúdo, o botão fica desabilitado e não anuncia um
               * painel que não existe.
               */}
              <button
                ref={(elemento) => {
                  botoesRef.current[chave] = elemento;
                }}
                type="button"
                className="lista-roteiros-preparados__seta"
                aria-label={
                  aberto
                    ? `Esconder roteiro de ${titulo}`
                    : `Mostrar roteiro de ${titulo}`
                }
                aria-expanded={temConteudo ? aberto : undefined}
                aria-controls={temConteudo ? idPainel : undefined}
                disabled={!temConteudo}
                onClick={() => alternar(chave)}
              >
                {aberto ? <ChevronUp /> : <ChevronDown />}
              </button>
            </div>

            {/*
             * Registro antigo sem as quatro listas: explicamos por que não dá
             * para abrir, em vez de mostrar um botão que não faz nada.
             */}
            {!temConteudo && (
              <p className="lista-roteiros-preparados__sem-conteudo">
                Conteúdo indisponível para este roteiro.
              </p>
            )}

            {/*
             * Conteúdo do item aberto: o mesmo visualizador usado no
             * resultado da geração, escondendo o cabeçalho (o item já mostra
             * período e data).
             */}
            {aberto && (
              <div
                id={idPainel}
                className="lista-roteiros-preparados__conteudo"
              >
                <VisualizadorRoteiro
                  roteiro={item.roteiro}
                  vendedorNome={vendedorNome}
                  mesReferencia={item.mes_referencia}
                  geradoEm={item.gerado_em}
                  ocultarCabecalho
                />
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
