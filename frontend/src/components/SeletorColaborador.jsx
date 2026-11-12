/**
 * Seletor de colaborador: card com a pessoa escolhida e uma seta para trocar.
 *
 * Lê do contexto (useApp) a lista de vendedores da loja, quem está selecionado
 * e as ações carregarVendedores/selecionarVendedor. Ao clicar na seta, abre
 * logo abaixo do card a lista dos OUTROS colaboradores; escolher um troca a
 * pessoa e fecha a lista. Não faz chamadas HTTP diretas nem cálculos de venda.
 */

// ChevronDown/Up: as setinhas da biblioteca lucide-react. "Down" aponta para
// baixo (lista fechada, clique para abrir) e "Up" para cima (lista aberta).
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useEffect, useId, useMemo, useRef, useState } from 'react';

// STATUS: situação da lista; VENDEDOR_FOCO_ID: quem já vem selecionado na demo.
import { STATUS, VENDEDOR_FOCO_ID } from '../constantes.js';
// Hook que entrega o estado global e as ações do AppProvider.
import { useApp } from '../context/useApp.js';
// Funções puras testadas em seletorColaborador.test.js.
import {
  encontrarColaborador,
  iniciaisDoNome,
  outrosColaboradores,
} from '../utilitarios/seletorColaborador.js';
import { EstadoCarregando } from './EstadoCarregando.jsx';
import { EstadoErro } from './EstadoErro.jsx';
import { EstadoVazio } from './EstadoVazio.jsx';

// Importa o CSS deste componente.
import './SeletorColaborador.css';

/**
 * Componente SeletorColaborador.
 *
 * Do contexto (useApp) lê:
 *   estado.vendedores: { status, dados, erro } da lista da loja;
 *   estado.vendedorSelecionadoId: quem está escolhido agora;
 *   carregarVendedores(): busca a lista na API;
 *   selecionarVendedor(id): escolhe uma pessoa e busca o histórico dela.
 *
 * Props (dados que o componente recebe de quem o usa):
 *   recolhida: opcional (padrão false). Com true, mostra só o círculo com as
 *     iniciais do colaborador — a barra lateral está recolhida e não há
 *     espaço para nome, seta nem lista.
 *   aoExpandir: opcional. Função chamada quando a pessoa clica no círculo com
 *     a barra recolhida: em vez de abrir a lista, ela PEDE para a barra
 *     expandir (quem manda na largura é a BarraLateral).
 *
 * Devolve o card da pessoa escolhida (ou o aviso de carregando/erro/vazio) e,
 * quando a seta é acionada, a lista dos outros colaboradores logo abaixo.
 * Recolhido, devolve só o círculo — mas continua montado, então o
 * carregamento da lista e a seleção automática da Bianca seguem funcionando.
 *
 * Exemplo de uso: <SeletorColaborador recolhida aoExpandir={abrir} />
 */
export function SeletorColaborador({ recolhida = false, aoExpandir }) {
  const { estado, carregarVendedores, selecionarVendedor } = useApp();

  // Atalho para os três pedaços da lista que interessam aqui.
  const { status, dados, erro } = estado.vendedores;

  /*
   * Garante que o trabalho abaixo sempre receba uma lista de verdade.
   *
   * useMemo guarda o resultado entre renderizações: se "dados" já é uma lista
   * (o caso normal), devolve a própria; se não for, devolve sempre a MESMA
   * lista vazia em vez de criar uma nova a cada renderização. Isso importa
   * porque o useEffect abaixo depende dela: uma lista nova a cada render faria
   * o efeito rodar sem necessidade.
   */
  const lista = useMemo(() => (Array.isArray(dados) ? dados : []), [dados]);

  /*
   * Estado local: a lista de outros colaboradores está aberta?
   *
   * "Estado" é a informação que muda e faz a tela se atualizar. Este valor é
   * local (só deste componente) porque não interessa ao resto do app.
   */
  const [aberto, setAberto] = useState(false);

  // useRef: uma "caixa" que guarda um valor entre renderizações sem fazer a
  // tela se atualizar. Usamos para lembrar se o pedido da lista já saiu, para
  // guardar o botão da seta e para alcançar os itens da lista.
  const jaPediuLista = useRef(false);
  const botaoSetaRef = useRef(null);
  const itensRef = useRef([]);

  /*
   * useId gera um identificador único para ligar o botão da seta à lista que
   * ele abre (usado no aria-controls). Dois seletores na mesma tela nunca
   * colidem, porque cada um recebe um id diferente.
   */
  const idLista = useId();

  // useEffect: roda um código depois que a tela aparece.
  //
  // A condição de status evita pedir de novo a cada renderização: assim que o
  // pedido começa, o status deixa de ser "ocioso" e o efeito não repete.
  //
  // Só isso, porém, não segura o StrictMode (modo de desenvolvimento que
  // monta o componente duas vezes de propósito, para revelar efeitos mal
  // feitos): as duas execuções acontecem antes de o novo status chegar à
  // tela. Por isso a caixa jaPediuLista impede a segunda chamada. Resultado:
  // a lista é pedida uma única vez.
  useEffect(() => {
    if (jaPediuLista.current) {
      return;
    }

    // Se outra parte do app já carregou a lista, não pedimos de novo: o
    // estado é compartilhado por toda a aplicação.
    if (status !== STATUS.OCIOSO) {
      return;
    }

    jaPediuLista.current = true;
    carregarVendedores();
  }, [status, carregarVendedores]);

  // Segundo efeito: quando a lista chega e ninguém está selecionado, escolhe
  // a Bianca (VENDEDOR_FOCO_ID) se ela estiver na lista. É uma conveniência
  // do cenário da demo; se ela não estiver lá, ninguém é selecionado.
  useEffect(() => {
    if (status !== STATUS.SUCESSO) {
      return;
    }

    if (estado.vendedorSelecionadoId) {
      return;
    }

    const temFoco = lista.some(
      (vendedor) => vendedor.vendedor_id === VENDEDOR_FOCO_ID,
    );

    if (!temFoco) {
      return;
    }

    selecionarVendedor(VENDEDOR_FOCO_ID);
  }, [status, lista, estado.vendedorSelecionadoId, selecionarVendedor]);

  /*
   * Pessoas para mostrar:
   * - selecionado: o item da lista que combina com o id escolhido (ou null);
   * - outros: TODOS menos o selecionado, na ordem da API. Quando não há
   *   ninguém escolhido, a função devolve a lista inteira.
   */
  const selecionado = encontrarColaborador(
    lista,
    estado.vendedorSelecionadoId,
  );
  const outros = outrosColaboradores(lista, estado.vendedorSelecionadoId);

  /*
   * Se a barra for recolhida com a lista aberta, a lista fecha.
   *
   * O ajuste é feito DURANTE a renderização — é o padrão que o próprio React
   * recomenda para "corrigir um estado quando uma prop muda". Fazer isso num
   * useEffect mostraria um desenho intermediário com a lista aberta num
   * espaço de 64px.
   *
   * Como funciona: guardamos o valor anterior da prop. Quando ele muda,
   * atualizamos o registro e, se a barra recolheu, fechamos a lista. O React
   * refaz a renderização na hora, já com o estado certo.
   */
  const [recolhidaAnterior, setRecolhidaAnterior] = useState(recolhida);

  if (recolhida !== recolhidaAnterior) {
    setRecolhidaAnterior(recolhida);

    if (recolhida) {
      setAberto(false);
    }
  }

  /**
   * Abre ou fecha a lista de outros colaboradores.
   *
   * Recebe: nada (usa o estado atual). Devolve: nada.
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
   * "Foco" é o lugar onde o teclado está agindo. Quando a lista some do DOM,
   * o elemento focado deixa de existir; sem devolver o foco, a pessoa que usa
   * teclado ficaria "perdida" no começo da página.
   */
  function fecharLista() {
    setAberto(false);
    botaoSetaRef.current?.focus();
  }

  /**
   * Escolhe um colaborador e fecha a lista.
   *
   * Recebe o código da pessoa. A ação do contexto já cuida de buscar o
   * histórico dela; aqui só fechamos a lista e devolvemos o foco à seta.
   */
  function escolherColaborador(vendedorId) {
    selecionarVendedor(vendedorId);
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
   * Recebe o evento e a posição do item que estava com foco.
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

    const total = outros.length;

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

  // Nome e cargo exibidos. Sem ninguém escolhido, o card convida a escolher.
  const nomeExibido = selecionado ? selecionado.nome : 'Escolher colaborador';
  const cargoExibido = selecionado ? selecionado.cargo : null;

  /*
   * Barra recolhida: só o círculo com as iniciais.
   *
   * Esta saída fica ANTES dos avisos de carregando/erro/vazio de propósito:
   * recolhida, a barra tem 64px e qualquer texto quebraria o layout. Os
   * avisos aparecem assim que a pessoa expande a barra.
   *
   * O componente continua montado, então os efeitos acima seguem carregando a
   * lista e escolhendo a Bianca automaticamente.
   */
  if (recolhida) {
    // Nome e cargo num rótulo só: é o que o leitor de tela fala no círculo.
    const rotuloAcessivel = selecionado
      ? `${selecionado.nome}, ${selecionado.cargo}`
      : 'Escolher colaborador';

    return (
      <div className="seletor-colaborador seletor-colaborador--recolhido">
        {/*
         * O círculo é um botão: clicar nele NÃO abre a lista (não há espaço),
         * e sim pede para a barra expandir, pela função recebida em
         * aoExpandir. title repete o nome como dica ao passar o mouse.
         */}
        <button
          type="button"
          className="seletor-colaborador__avatar-botao"
          aria-label={rotuloAcessivel}
          title={nomeExibido}
          onClick={() => aoExpandir?.()}
        >
          <span className="seletor-colaborador__avatar" aria-hidden="true">
            {iniciaisDoNome(selecionado?.nome)}
          </span>
        </button>
      </div>
    );
  }

  return (
    <div className="seletor-colaborador">
      {/* Erro: mostra o texto vindo do estado e permite tentar de novo. */}
      {status === STATUS.ERRO && (
        <EstadoErro
          mensagem={erro}
          aoTentarDeNovo={() => carregarVendedores()}
        />
      )}

      {/* Ainda não pedimos (ocioso) ou o pedido está em andamento. */}
      {(status === STATUS.OCIOSO || status === STATUS.CARREGANDO) && (
        <EstadoCarregando
          titulo="Carregando colaboradores…"
          linhas={2}
          variante="texto"
        />
      )}

      {/* Deu certo, mas a loja não devolveu ninguém. */}
      {status === STATUS.SUCESSO && lista.length === 0 && (
        <EstadoVazio
          titulo="Nenhum colaborador encontrado"
          descricao="Não há colaboradores para mostrar nesta loja agora."
        />
      )}

      {/* Deu certo: o card e, se aberta, a lista dos outros. */}
      {status === STATUS.SUCESSO && lista.length > 0 && (
        <>
          {/*
           * O card em si NÃO é clicável: quem controla a lista é o botão da
           * seta. Assim fica claro para todo mundo (mouse, teclado e leitor
           * de tela) qual elemento faz o quê.
           */}
          <div className="seletor-colaborador__card">
            {/*
             * Círculo com as iniciais. aria-hidden porque é decorativo: o
             * nome completo aparece escrito ao lado.
             */}
            {selecionado && (
              <span
                className="seletor-colaborador__avatar"
                aria-hidden="true"
              >
                {iniciaisDoNome(selecionado.nome)}
              </span>
            )}

            <span className="seletor-colaborador__texto">
              <span
                className={
                  selecionado
                    ? 'seletor-colaborador__nome'
                    : 'seletor-colaborador__nome seletor-colaborador__nome--vazio'
                }
              >
                {nomeExibido}
              </span>

              {/* Cargo só existe quando há alguém escolhido. */}
              {cargoExibido && (
                <span className="seletor-colaborador__cargo">
                  {cargoExibido}
                </span>
              )}
            </span>

            {/*
             * Botão só com ícone. aria-label dá o nome que o leitor de tela
             * fala; aria-expanded avisa se o bloco está aberto ou fechado
             * (é o padrão "disclosure": botão + bloco que aparece/some);
             * aria-controls aponta para o id da lista.
             */}
            <button
              ref={botaoSetaRef}
              type="button"
              className="seletor-colaborador__seta"
              aria-label="Trocar de colaborador"
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
          {aberto && outros.length > 0 && (
            <ul
              id={idLista}
              className="seletor-colaborador__lista"
              aria-label="Outros colaboradores"
            >
              {outros.map((vendedor, indice) => (
                <li key={vendedor.vendedor_id}>
                  <button
                    type="button"
                    className="seletor-colaborador__item"
                    /*
                     * A ref guarda este botão na posição dele, para as setas
                     * ↑/↓ conseguirem mover o foco até ele. A função não
                     * devolve nada (um retorno seria tratado pelo React como
                     * função de limpeza).
                     */
                    ref={(elemento) => {
                      itensRef.current[indice] = elemento;
                    }}
                    onClick={() =>
                      escolherColaborador(vendedor.vendedor_id)
                    }
                    onKeyDown={(evento) => aoTeclarItem(evento, indice)}
                  >
                    <span
                      className="seletor-colaborador__avatar seletor-colaborador__avatar--lista"
                      aria-hidden="true"
                    >
                      {iniciaisDoNome(vendedor.nome)}
                    </span>

                    <span className="seletor-colaborador__texto">
                      <span className="seletor-colaborador__nome">
                        {vendedor.nome}
                      </span>
                      <span className="seletor-colaborador__cargo">
                        {vendedor.cargo}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {/*
           * Caso raro: a loja só tem a pessoa já escolhida. Sem esta frase, a
           * seta abriria um espaço vazio sem explicação.
           */}
          {aberto && outros.length === 0 && (
            <p className="seletor-colaborador__sem-outros">
              Não há outros colaboradores nesta loja.
            </p>
          )}
        </>
      )}
    </div>
  );
}
