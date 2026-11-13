/**
 * Aba Feedback da visão regional (Etapa 8).
 *
 * Espelha a aba do gerente, mas o roteiro é preparado PARA O GERENTE da loja
 * escolhida: a regional escolhe o período, gera com a IA e lê o resultado.
 * Lê estado.detalhesLoja (consolidado + roteiros anteriores) e
 * estado.feedbacksRegional[lojaSelecionadaId] (a geração em andamento/última).
 *
 * Nada é calculado aqui: os números e o roteiro vêm prontos da API.
 */

import { useState } from 'react';

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { ListaRoteirosPreparados } from '../components/ListaRoteirosPreparados.jsx';
import { VisualizadorRoteiro } from '../components/VisualizadorRoteiro.jsx';
import { montarOpcoesDePeriodo } from '../utilitarios/opcoesDePeriodo.js';

// Importa o CSS desta página (cópia própria do CSS da aba do gerente).
import './PaginaFeedbackRegional.css';

/**
 * Componente PaginaFeedbackRegional.
 *
 * Não recebe props: lê do contexto a loja selecionada, o histórico dela
 * (estado.detalhesLoja) e o roteiro do gerente (feedbacksRegional[lojaId]).
 *
 * Devolve dois blocos: "Gerar feedback para o gerente" (seletor, botão e
 * resultado) e "Roteiros já preparados para o gerente".
 *
 * Exemplo de uso: <PaginaFeedbackRegional key={lojaSelecionadaId} />
 */
export function PaginaFeedbackRegional() {
  const { estado, gerarFeedbackRegional, selecionarLoja } = useApp();

  const lojaId = estado.lojaSelecionadaId;
  const { status: statusDetalhes, dados, erro: erroDetalhes } =
    estado.detalhesLoja;

  // Pode ser undefined: a regional ainda não gerou nenhum roteiro nesta loja.
  const feedback = lojaId ? estado.feedbacksRegional[lojaId] : undefined;

  /*
   * Estado local do seletor. periodoEscolhido começa null para usarmos o
   * padrão calculado; periodoSolicitado lembra o período do último pedido,
   * para "Tentar de novo" repetir exatamente a mesma geração.
   */
  const [periodoEscolhido, setPeriodoEscolhido] = useState(null);
  const [periodoSolicitado, setPeriodoSolicitado] = useState(undefined);

  // Enquanto o histórico da loja não chega, não há como montar o seletor de
  // meses nem a lista de roteiros preparados.
  if (statusDetalhes === STATUS.OCIOSO || statusDetalhes === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando os dados da loja…"
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
          lojaId ? () => selecionarLoja(lojaId) : undefined
        }
      />
    );
  }

  if (!dados) {
    return (
      <EstadoVazio
        titulo="Sem dados da loja"
        descricao="Escolha uma loja no card da barra lateral para preparar o feedback do gerente."
      />
    );
  }

  // Nome do gerente para os textos; fallback genérico se faltar.
  const gerenteNome =
    typeof dados.gerente_nome === 'string' &&
    dados.gerente_nome.trim() !== ''
      ? dados.gerente_nome
      : 'o gerente da loja';

  const resultadoLoja = dados.resultado_loja ?? [];
  const preparados = dados.feedbacks_preparados ?? [];

  /*
   * Estado derivado: as opções e o padrão saem dos MESMOS meses do resultado
   * da loja (cada item tem "mes" e "mes_parcial"), então o seletor oferece
   * exatamente os períodos que existem nos dados.
   */
  const { opcoes, valorPadrao } = montarOpcoesDePeriodo(resultadoLoja);

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
    if (!lojaId || gerando) {
      return;
    }

    const mesReferencia = periodo === '' ? undefined : periodo;

    // Guarda o período do pedido para o "Tentar de novo" repetir igual.
    setPeriodoSolicitado(mesReferencia);
    gerarFeedbackRegional(lojaId, { mesReferencia });
  }

  /**
   * Repete a geração com o MESMO período do pedido que falhou.
   * Não há nova tentativa automática: cada geração consome créditos.
   */
  function aoTentarDeNovo() {
    if (!lojaId) {
      return;
    }

    gerarFeedbackRegional(lojaId, { mesReferencia: periodoSolicitado });
  }

  return (
    <div className="pagina-feedback-regional">
      {/* ---------- Gerar feedback para o gerente ---------- */}
      <section
        className="pagina-feedback-regional__secao"
        aria-labelledby="titulo-gerar-regional"
      >
        <h2
          id="titulo-gerar-regional"
          className="pagina-feedback-regional__titulo pagina-feedback-regional__titulo--principal"
        >
          Gerar feedback para o gerente
        </h2>

        <div className="pagina-feedback-regional__controles">
          <div className="pagina-feedback-regional__campo">
            {/* O label fica ligado ao select pelo htmlFor/id. */}
            <label
              htmlFor="periodo-feedback-regional"
              className="pagina-feedback-regional__rotulo"
            >
              Período
            </label>

            {/*
             * select é a lista suspensa nativa. O valor "" é "Todo o
             * histórico"; os demais são os meses do resultado da loja.
             * Fica desabilitado durante a geração para ninguém pensar que
             * mudar o período altera um pedido já em andamento.
             */}
            <select
              id="periodo-feedback-regional"
              className="pagina-feedback-regional__select"
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
            Gerar feedback
          </button>
        </div>

        {/*
         * Área de resultado com aria-live="polite": o leitor de tela avisa
         * quando o conteúdo muda (carregando, erro ou roteiro pronto) sem
         * interromper a leitura em andamento.
         */}
        <div
          className="pagina-feedback-regional__resultado"
          aria-live="polite"
        >
          {statusFeedback === STATUS.OCIOSO && (
            <EstadoVazio
              titulo="Nenhum roteiro gerado ainda"
              descricao={`Escolha o período e clique em Gerar feedback. O rascunho trará pontos positivos, pontos de melhoria, possíveis motivos e um roteiro de conversa para a sua conversa com ${gerenteNome}.`}
            />
          )}

          {statusFeedback === STATUS.CARREGANDO && (
            <EstadoCarregando
              titulo="Preparando o feedback do gerente…"
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
             * não corrige o texto e não valida o conteúdo. O nome exibido é o
             * do GERENTE avaliado.
             */
            <VisualizadorRoteiro
              roteiro={feedback.dados.roteiro}
              vendedorNome={feedback.dados.gerente_nome}
              mesReferencia={feedback.dados.mes_referencia}
              geradoEm={feedback.dados.gerado_em}
            />
          )}
        </div>
      </section>

      {/* ---------- Roteiros já preparados para o gerente ---------- */}
      <section
        className="pagina-feedback-regional__secao"
        aria-labelledby="titulo-preparados-regional"
      >
        <h2
          id="titulo-preparados-regional"
          className="pagina-feedback-regional__titulo"
        >
          Roteiros já preparados para o gerente
        </h2>

        <p className="pagina-feedback-regional__explicacao">
          Roteiro preparado não significa feedback realizado: é só o rascunho
          gerado pela IA.
        </p>

        {preparados.length === 0 ? (
          <EstadoVazio
            titulo="Nenhum roteiro preparado"
            descricao="Ainda não há rascunhos gerados para o gerente desta loja."
          />
        ) : (
          /*
           * A lista cuida do próprio estado de abrir/fechar (acordeão):
           * a página só entrega os dados e o nome de quem recebe o roteiro.
           */
          <ListaRoteirosPreparados
            roteiros={preparados}
            vendedorNome={dados.gerente_nome}
          />
        )}
      </section>
    </div>
  );
}
