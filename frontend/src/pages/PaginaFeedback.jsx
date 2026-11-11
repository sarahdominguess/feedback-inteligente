/**
 * Página da aba Feedback do colaborador selecionado.
 *
 * Tem o seletor de período, o botão que gera o roteiro com IA, os estados da
 * geração, o visualizador do roteiro e a lista de roteiros já preparados.
 */

import { useState } from 'react';

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { VisualizadorRoteiro } from '../components/VisualizadorRoteiro.jsx';
import { formatarDataHora } from '../utilitarios/formatadores.js';
import { montarOpcoesDePeriodo } from '../utilitarios/opcoesDePeriodo.js';
import { rotuloPeriodo } from '../utilitarios/periodoDoRoteiro.js';

// Importa o CSS desta página.
import './PaginaFeedback.css';

/**
 * Componente PaginaFeedback.
 *
 * Não recebe props: lê do contexto o vendedor selecionado, o histórico
 * (estado.detalhes) e o roteiro daquele vendedor (estado.feedbacks[id]).
 *
 * Devolve dois blocos: "Gerar roteiro de feedback" (seletor, botão, aviso e
 * resultado) e "Roteiros já preparados".
 *
 * Exemplo de uso: <PaginaFeedback key={vendedorId} />
 */
export function PaginaFeedback() {
  const { estado, gerarFeedback, selecionarVendedor } = useApp();

  const vendedorId = estado.vendedorSelecionadoId;
  const { status: statusDetalhes, dados: detalhes, erro: erroDetalhes } =
    estado.detalhes;

  // Pode ser undefined: a pessoa ainda não gerou nenhum roteiro.
  const feedback = vendedorId ? estado.feedbacks[vendedorId] : undefined;

  /*
   * Estado local do seletor. periodoEscolhido começa null para usarmos o
   * padrão calculado; depois guarda o que a pessoa escolheu.
   * periodoSolicitado lembra o período do último pedido, para o botão
   * "Tentar de novo" repetir exatamente a mesma geração.
   *
   * O componente é montado com key={vendedorId} em AreaCentral, então trocar
   * de colaborador reinicia estes valores automaticamente.
   */
  const [periodoEscolhido, setPeriodoEscolhido] = useState(null);
  const [periodoSolicitado, setPeriodoSolicitado] = useState(undefined);

  // Enquanto o histórico do colaborador não chega, não há como montar o
  // seletor de meses nem a lista de roteiros preparados.
  if (statusDetalhes === STATUS.OCIOSO || statusDetalhes === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando os dados do colaborador…"
        linhas={4}
        variante="cartao"
      />
    );
  }

  if (statusDetalhes === STATUS.ERRO) {
    return (
      <EstadoErro
        mensagem={erroDetalhes}
        aoTentarDeNovo={
          vendedorId ? () => selecionarVendedor(vendedorId) : undefined
        }
      />
    );
  }

  if (!detalhes) {
    return (
      <EstadoVazio
        titulo="Sem dados do colaborador"
        descricao="Escolha um colaborador na lista para preparar o feedback."
      />
    );
  }

  const resumoMensal = detalhes.resumo_mensal ?? [];
  const preparados = detalhes.feedbacks_preparados ?? [];

  /*
   * Estado derivado: as opções e o padrão são calculados a partir do
   * histórico a cada renderização. Não guardamos uma cópia no estado, para
   * não existir uma segunda fonte de verdade.
   */
  const { opcoes, valorPadrao } = montarOpcoesDePeriodo(resumoMensal);

  /*
   * Usar ?? (e não ||) é importante: "Todo o histórico" vale "", que é
   * falsy. Com ||, a escolha de "Todo o histórico" voltaria ao padrão.
   */
  const periodo = periodoEscolhido ?? valorPadrao;

  const statusFeedback = feedback?.status ?? STATUS.OCIOSO;
  const gerando = statusFeedback === STATUS.CARREGANDO;

  /**
   * Pede a geração do roteiro com o período que está no seletor.
   *
   * Sem mês, envia undefined: o serviço omite o campo e o backend usa todo o
   * histórico. O contexto já ignora cliques repetidos; a trava aqui evita
   * pedidos duplicados enquanto a tela está carregando.
   */
  function aoGerar() {
    if (!vendedorId || gerando) {
      return;
    }

    const mesReferencia = periodo === '' ? undefined : periodo;

    // Guarda o período do pedido para o "Tentar de novo" repetir igual.
    setPeriodoSolicitado(mesReferencia);
    gerarFeedback(vendedorId, { mesReferencia });
  }

  /**
   * Repete a geração com o MESMO período do pedido que falhou.
   * Não há nova tentativa automática: cada geração consome créditos.
   */
  function aoTentarDeNovo() {
    if (!vendedorId) {
      return;
    }

    gerarFeedback(vendedorId, { mesReferencia: periodoSolicitado });
  }

  return (
    <div className="pagina-feedback pagina-feedback--expandida">
      {/* ---------- Gerar roteiro ---------- */}
      <section
        className="pagina-feedback__secao"
        aria-labelledby="titulo-gerar"
      >
        <h2 id="titulo-gerar" className="pagina-feedback__titulo">
          Gerar roteiro de feedback
        </h2>

        <div className="pagina-feedback__controles">
          <div className="pagina-feedback__campo">
            {/* O label fica ligado ao select pelo htmlFor/id. */}
            <label
              htmlFor="periodo-feedback"
              className="pagina-feedback__rotulo"
            >
              Período
            </label>

            {/*
             * select é a lista suspensa nativa do navegador. O valor "" é a
             * opção "Todo o histórico"; os demais são os meses do resumo.
             * Fica desabilitado durante a geração para ninguém pensar que
             * mudar o período altera um pedido já em andamento.
             */}
            <select
              id="periodo-feedback"
              className="pagina-feedback__select"
              value={periodo}
              onChange={(evento) => setPeriodoEscolhido(evento.target.value)}
              disabled={gerando}
            >
              {opcoes.map((opcao) => (
                <option
                  key={opcao.valor || 'todo-o-historico'}
                  value={opcao.valor}
                >
                  {opcao.rotulo}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            className="ui-botao-primario"
            onClick={aoGerar}
            disabled={gerando}
          >
            Gerar roteiro
          </button>
        </div>

        {/* Aviso fixo: custo, tempo e responsabilidade de quem revisa. */}
        <p className="pagina-feedback__aviso">
          A geração usa IA, consome créditos e pode levar até alguns minutos.
          Revise tudo antes de usar: você continua sendo o dono da conversa.
        </p>

        {/*
         * Área de resultado com aria-live="polite": o leitor de tela avisa
         * quando o conteúdo muda (carregando, erro ou roteiro pronto) sem
         * interromper a leitura em andamento.
         */}
        <div className="pagina-feedback__resultado" aria-live="polite">
          {statusFeedback === STATUS.OCIOSO && (
            <EstadoVazio
              titulo="Nenhum roteiro gerado ainda"
              descricao="Escolha o período e clique em Gerar roteiro. O rascunho trará pontos positivos, pontos de melhoria, possíveis motivos e um roteiro de conversa, para você revisar."
            />
          )}

          {statusFeedback === STATUS.CARREGANDO && (
            <EstadoCarregando
              titulo="Preparando o roteiro…"
              descricao="Isso pode levar de 10 segundos a alguns minutos. Não precisa clicar de novo."
              linhas={4}
              variante="cartao"
            />
          )}

          {statusFeedback === STATUS.ERRO && (
            <EstadoErro
              mensagem={feedback?.erro}
              aoTentarDeNovo={aoTentarDeNovo}
            />
          )}

          {statusFeedback === STATUS.SUCESSO && feedback?.dados && (
            /*
             * O visualizador recebe o roteiro por props: não usa o contexto,
             * não corrige o texto e não valida o conteúdo.
             */
            <VisualizadorRoteiro
              roteiro={feedback.dados.roteiro}
              vendedorNome={feedback.dados.vendedor_nome}
              mesReferencia={feedback.dados.mes_referencia}
              geradoEm={feedback.dados.gerado_em}
            />
          )}
        </div>
      </section>

      {/* ---------- Roteiros já preparados ---------- */}
      <section
        className="pagina-feedback__secao"
        aria-labelledby="titulo-preparados"
      >
        <h2 id="titulo-preparados" className="pagina-feedback__titulo">
          Roteiros já preparados
        </h2>

        <p className="pagina-feedback__explicacao">
          "Roteiro preparado" não significa "feedback realizado": é só o
          rascunho gerado pela IA.
        </p>

        {preparados.length === 0 ? (
          <EstadoVazio
            titulo="Nenhum roteiro preparado"
            descricao="Ainda não há rascunhos gerados para esta pessoa."
          />
        ) : (
          <ul className="pagina-feedback__preparados">
            {preparados.map((item) => (
              <li key={item.feedback_id} className="pagina-feedback__preparado">
                <span className="pagina-feedback__preparado-periodo">
                  {rotuloPeriodo(item.mes_referencia)}
                </span>
                <span className="pagina-feedback__preparado-data">
                  {formatarDataHora(item.gerado_em)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
