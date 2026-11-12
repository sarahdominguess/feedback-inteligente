/**
 * Seletor de LOJA da visão regional.
 *
 * Card com a loja escolhida e uma seta para trocar. Ao clicar na seta, abre
 * logo abaixo a lista das OUTRAS lojas; escolher uma troca a loja e fecha a
 * lista. Lê do contexto (useApp) a lista de lojas, a loja selecionada e as
 * ações carregarLojas/selecionarLoja. Não faz chamadas HTTP diretas nem
 * cálculos de venda.
 *
 * Hoje a regional tem UMA loja (L004), então a lista aberta mostra um aviso.
 * O componente já funciona com N lojas para quando existirem outras.
 */

// ChevronDown/Up: as setinhas da biblioteca lucide-react. "Down" aponta para
// baixo (lista fechada, clique para abrir) e "Up" para cima (lista aberta).
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useEffect, useId, useMemo, useRef, useState } from 'react';

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
// Funções puras testadas em seletorLoja.test.js.
import {
  encontrarLoja,
  iniciaisDaLoja,
  outrasLojas,
} from '../utilitarios/seletorLoja.js';
import { EstadoCarregando } from './EstadoCarregando.jsx';
import { EstadoErro } from './EstadoErro.jsx';
import { EstadoVazio } from './EstadoVazio.jsx';

// Importa o CSS deste componente.
import './SeletorLoja.css';

/**
 * Componente SeletorLoja.
 *
 * Do contexto (useApp) lê:
 *   estado.lojas: { status, dados, erro } da lista de lojas;
 *   estado.lojaSelecionadaId: qual loja está escolhida agora;
 *   carregarLojas(): busca a lista na API;
 *   selecionarLoja(id): escolhe uma loja e busca o histórico dela.
 *
 * Props:
 *   recolhida: opcional (padrão false). Com true, mostra só o círculo com a
 *     letra da loja — a barra lateral está recolhida e não há espaço para
 *     nome, seta nem lista.
 *   aoExpandir: opcional. Função chamada quando a pessoa clica no círculo com
 *     a barra recolhida: em vez de abrir a lista, ela PEDE para a barra
 *     expandir (quem manda na largura é a BarraLateral).
 *
 * Devolve o card da loja escolhida (ou o aviso de carregando/erro/vazio) e,
 * quando a seta é acionada, a lista das outras lojas logo abaixo. Recolhido,
 * devolve só o círculo — mas continua montado, então o carregamento da lista
 * e a seleção automática da primeira loja seguem funcionando.
 *
 * Exemplo de uso: <SeletorLoja recolhida aoExpandir={abrir} />
 */
export function SeletorLoja({ recolhida = false, aoExpandir }) {
  const { estado, carregarLojas, selecionarLoja } = useApp();

  // Atalho para os três pedaços da lista que interessam aqui.
  const { status, dados, erro } = estado.lojas;

  /*
   * Garante que o trabalho abaixo sempre receba uma lista de verdade.
   *
   * useMemo guarda o resultado entre renderizações: se "dados" já é uma lista
   * (o caso normal), devolve a própria; se não for, devolve sempre a MESMA
   * lista vazia em vez de criar uma nova a cada renderização. Isso importa
   * porque o useEffect abaixo depende dela.
   */
  const lista = useMemo(() => (Array.isArray(dados) ? dados : []), [dados]);

  /*
   * Estado local: a lista das outras lojas está aberta?
   *
   * "Estado" é a informação que muda e faz a tela se atualizar. Este valor é
   * local (só deste componente) porque não interessa ao resto do app.
   */
  const [aberto, setAberto] = useState(false);

  // useRef: uma "caixa" que guarda um valor entre renderizações sem fazer a
  // tela se atualizar. Usamos para lembrar se o pedido já saiu, para guardar
  // o botão da seta e para alcançar os itens da lista.
  const jaPediuLista = useRef(false);
  const botaoSetaRef = useRef(null);
  const itensRef = useRef([]);

  /*
   * useId gera um identificador único para ligar o botão da seta à lista que
   * ele abre (usado no aria-controls). Dois seletores na mesma tela nunca
   * colidem, porque cada um recebe um id diferente.
   */
  const idLista = useId();

  /*
   * useEffect: roda um código depois que a tela aparece.
   *
   * A condição de status evita pedir de novo a cada renderização: assim que o
   * pedido começa, o status deixa de ser "ocioso" e o efeito não repete.
   * A caixa jaPediuLista segura o StrictMode (que monta o componente duas
   * vezes em desenvolvimento): a lista é pedida uma única vez.
   */
  useEffect(() => {
    if (jaPediuLista.current) {
      return;
    }

    // Se outra parte do app já carregou a lista, não pedimos de novo.
    if (status !== STATUS.OCIOSO) {
      return;
    }

    jaPediuLista.current = true;
    carregarLojas();
  }, [status, carregarLojas]);

  // Segundo efeito: quando a lista chega e ninguém está selecionado, escolhe
  // a PRIMEIRA loja (cenário atual: L004). É conveniência de tela; se a lista
  // vier vazia, ninguém é selecionado.
  useEffect(() => {
    if (status !== STATUS.SUCESSO) {
      return;
    }

    if (estado.lojaSelecionadaId) {
      return;
    }

    if (lista.length === 0) {
      return;
    }

    selecionarLoja(lista[0].loja_id);
  }, [status, lista, estado.lojaSelecionadaId, selecionarLoja]);

  /*
   * Lojas para mostrar:
   * - selecionada: o item da lista que combina com o id escolhido (ou null);
   * - outras: TODAS menos a selecionada, na ordem da API. Sem seleção, a
   *   função devolve a lista inteira.
   */
  const selecionada = encontrarLoja(lista, estado.lojaSelecionadaId);
  const outras = outrasLojas(lista, estado.lojaSelecionadaId);

  /*
   * Se a barra for recolhida com a lista aberta, a lista fecha.
   *
   * O ajuste é feito DURANTE a renderização — padrão recomendado pelo React
   * para "corrigir um estado quando uma prop muda". Num useEffect haveria um
   * desenho intermediário com a lista aberta num espaço de 64px.
   */
  const [recolhidaAnterior, setRecolhidaAnterior] = useState(recolhida);

  if (recolhida !== recolhidaAnterior) {
    setRecolhidaAnterior(recolhida);

    if (recolhida) {
      setAberto(false);
    }
  }

  /**
   * Abre ou fecha a lista das outras lojas.
   *
   * Ao abrir, limpamos a caixa de refs dos itens para não guardar posições de
   * uma abertura anterior (a lista pode ter mudado desde então).
   */
  function alternarLista() {
    setAberto((estavaAberto) => {
      if (!estavaAberto) {
        itensRef.current = [];
      }
      return !estavaAberto;
    });
  }

  /**
   * Fecha a lista e devolve o foco para o botão da seta.
   *
   * Quando a lista some do DOM, o elemento focado deixa de existir; sem
   * devolver o foco, quem usa teclado ficaria "perdido" na página.
   */
  function fecharLista() {
    setAberto(false);
    botaoSetaRef.current?.focus();
  }

  /**
   * Escolhe uma loja e fecha a lista.
   *
   * A ação do contexto já cuida de buscar o histórico da loja; aqui só
   * fechamos a lista e devolvemos o foco à seta.
   */
  function escolherLoja(lojaId) {
    selecionarLoja(lojaId);
    setAberto(false);
    botaoSetaRef.current?.focus();
  }

  /**
   * Trata o teclado no botão da seta.
   *
   * Esc fecha a lista (voltando o foco para a própria seta). Enter e Espaço
   * continuam funcionando sozinhos, porque o elemento é um <button>.
   */
  function aoTeclarSeta(evento) {
    if (evento.key === 'Escape' && aberto) {
      evento.preventDefault();
      fecharLista();
    }
  }

  /**
   * Trata o teclado dentro da lista aberta.
   *
   * Esc fecha a lista; ↑ e ↓ movem o foco entre os itens, dando a volta no
   * começo e no fim (a conta com "%" faz esse retorno).
   */
  function aoTeclarItem(evento, indice) {
    if (evento.key === 'Escape') {
      evento.preventDefault();
      fecharLista();
      return;
    }

    if (evento.key !== 'ArrowDown' && evento.key !== 'ArrowUp') {
      // Tab, Shift+Tab e as demais teclas seguem o comportamento normal.
      return;
    }

    const total = outras.length;

    if (total === 0) {
      return;
    }

    // Evita que a seta também role a página.
    evento.preventDefault();

    const passo = evento.key === 'ArrowDown' ? 1 : -1;
    const proximoIndice = (indice + passo + total) % total;

    // Ref: acesso direto ao botão daquela posição para chamar focus().
    itensRef.current[proximoIndice]?.focus();
  }

  // Nome e gerente exibidos. Sem loja escolhida, o card convida a escolher.
  const nomeExibido = selecionada ? selecionada.loja_nome : 'Escolher loja';
  const gerenteExibido = selecionada
    ? `Gerente: ${selecionada.gerente_nome}`
    : null;

  /*
   * Barra recolhida: só o círculo com a letra da loja.
   *
   * Esta saída fica ANTES dos avisos de carregando/erro/vazio de propósito:
   * recolhida, a barra tem 64px e qualquer texto quebraria o layout. Os
   * avisos aparecem assim que a pessoa expande a barra.
   */
  if (recolhida) {
    // Nome e gerente num rótulo só: é o que o leitor de tela fala no círculo.
    const rotuloAcessivel = selecionada
      ? `${selecionada.loja_nome}, ${gerenteExibido}`
      : 'Escolher loja';

    return (
      <div className="seletor-loja seletor-loja--recolhido">
        {/*
         * O círculo é um botão: clicar nele NÃO abre a lista (não há espaço),
         * e sim pede para a barra expandir, pela função recebida em
         * aoExpandir. title repete o nome como dica ao passar o mouse.
         */}
        <button
          type="button"
          className="seletor-loja__avatar-botao"
          aria-label={rotuloAcessivel}
          title={nomeExibido}
          onClick={() => aoExpandir?.()}
        >
          <span className="seletor-loja__avatar" aria-hidden="true">
            {iniciaisDaLoja(selecionada?.loja_nome)}
          </span>
        </button>
      </div>
    );
  }

  return (
    <div className="seletor-loja">
      {/* Erro: mostra o texto vindo do estado e permite tentar de novo. */}
      {status === STATUS.ERRO && (
        <EstadoErro
          mensagem={erro}
          aoTentarDeNovo={() => carregarLojas()}
        />
      )}

      {/* Ainda não pedimos (ocioso) ou o pedido está em andamento. */}
      {(status === STATUS.OCIOSO || status === STATUS.CARREGANDO) && (
        <EstadoCarregando
          titulo="Carregando lojas…"
          linhas={2}
          variante="texto"
        />
      )}

      {/* Deu certo, mas a regional não devolveu nenhuma loja. */}
      {status === STATUS.SUCESSO && lista.length === 0 && (
        <EstadoVazio
          titulo="Nenhuma loja encontrada"
          descricao="Não há lojas para mostrar nesta regional agora."
        />
      )}

      {/* Deu certo: o card e, se aberta, a lista das outras lojas. */}
      {status === STATUS.SUCESSO && lista.length > 0 && (
        <>
          {/*
           * O card em si NÃO é clicável: quem controla a lista é o botão da
           * seta. Assim fica claro para mouse, teclado e leitor de tela qual
           * elemento faz o quê.
           */}
          <div className="seletor-loja__card">
            {/*
             * Círculo com a letra da loja. aria-hidden porque é decorativo: o
             * nome completo aparece escrito ao lado.
             */}
            {selecionada && (
              <span className="seletor-loja__avatar" aria-hidden="true">
                {iniciaisDaLoja(selecionada.loja_nome)}
              </span>
            )}

            <span className="seletor-loja__texto">
              <span
                className={
                  selecionada
                    ? 'seletor-loja__nome'
                    : 'seletor-loja__nome seletor-loja__nome--vazio'
                }
              >
                {nomeExibido}
              </span>

              {/* Linha do gerente só existe quando há loja escolhida. */}
              {gerenteExibido && (
                <span className="seletor-loja__gerente">
                  {gerenteExibido}
                </span>
              )}
            </span>

            {/*
             * Botão só com ícone. aria-label dá o nome que o leitor de tela
             * fala; aria-expanded avisa se o bloco está aberto ou fechado
             * (padrão "disclosure"); aria-controls aponta para a lista.
             */}
            <button
              ref={botaoSetaRef}
              type="button"
              className="seletor-loja__seta"
              aria-label="Trocar de loja"
              aria-expanded={aberto}
              aria-controls={idLista}
              onClick={alternarLista}
              onKeyDown={aoTeclarSeta}
            >
              {aberto ? <ChevronUp /> : <ChevronDown />}
            </button>
          </div>

          {/*
           * Lista aberta: entra no fluxo normal da página (logo abaixo do
           * card), empurrando o conteúdo. Nada de posicionamento absoluto,
           * que poderia ser cortado pela lateral ou sumir no celular.
           */}
          {aberto && outras.length > 0 && (
            <ul
              id={idLista}
              className="seletor-loja__lista"
              aria-label="Outras lojas"
            >
              {outras.map((loja, indice) => (
                <li key={loja.loja_id}>
                  <button
                    type="button"
                    className="seletor-loja__item"
                    /*
                     * A ref guarda este botão na posição dele, para as setas
                     * ↑/↓ moverem o foco até ele.
                     */
                    ref={(elemento) => {
                      itensRef.current[indice] = elemento;
                    }}
                    onClick={() => escolherLoja(loja.loja_id)}
                    onKeyDown={(evento) => aoTeclarItem(evento, indice)}
                  >
                    <span
                      className="seletor-loja__avatar seletor-loja__avatar--lista"
                      aria-hidden="true"
                    >
                      {iniciaisDaLoja(loja.loja_nome)}
                    </span>

                    <span className="seletor-loja__texto">
                      <span className="seletor-loja__nome">
                        {loja.loja_nome}
                      </span>
                      <span className="seletor-loja__gerente">
                        Gerente: {loja.gerente_nome}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {/*
           * Caso atual da regional: só existe uma loja com dados. Sem esta
           * frase, a seta abriria um espaço vazio sem explicação.
           */}
          {aberto && outras.length === 0 && (
            <p className="seletor-loja__sem-outros">
              Não há outras lojas com dados nesta regional.
            </p>
          )}
        </>
      )}
    </div>
  );
}
