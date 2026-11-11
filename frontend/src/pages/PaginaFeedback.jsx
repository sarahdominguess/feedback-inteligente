/**
 * Página da aba Feedback do colaborador selecionado.
 *
 * Tem o seletor de período, o botão que gera o roteiro com IA, os estados da
 * geração e a lista de roteiros já preparados. O visual final do roteiro
 * entra na próxima fatia; aqui ele aparece como texto simples.
 */

import { useState } from 'react';

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import {
  formatarDataHora,
  formatarMes,
} from '../utilitarios/formatadores.js';
import { montarOpcoesDePeriodo } from '../utilitarios/opcoesDePeriodo.js';

// Importa o CSS desta página.
import './PaginaFeedback.css';

/**
 * Nomes das quatro seções do roteiro, na ordem em que aparecem.
 */
const SECOES_ROTEIRO = [
  ['pontos_positivos', 'Pontos positivos'],
  ['pontos_melhoria', 'Pontos de melhoria'],
  ['possiveis_motivos', 'Possíveis motivos'],
  ['roteiro_conversa', 'Roteiro da conversa'],
];

/**
 * Monta o resumo simples do roteiro gerado.
 *
 * Recebe o objeto devolvido pela API (FeedbackGerarResposta). Devolve o nome
 * da pessoa, o período, a data/hora e as quatro listas em texto simples.
 * O texto da IA é exibido como texto do React: nunca é interpretado como HTML.
 */
function resumoDoRoteiro(dados) {
  // mes_referencia nulo significa que a geração usou todo o histórico.
  const periodo = dados.mes_referencia
    ? formatarMes(dados.mes_referencia)
    : 'Todo o histórico';

  return (
    <div className="pagina-feedback__resumo">
      <h3 className="pagina-feedback__resumo-titulo">
        {dados.vendedor_nome}
      </h3>

      <p className="pagina-feedback__resumo-meta">
        Período: {periodo} · Gerado em {formatarDataHora(dados.gerado_em)}
      </p>

      {SECOES_ROTEIRO.map(([chave, rotulo]) => {
        /*
         * O contrato garante uma lista em cada chave, mas o Array.isArray
         * evita que um formato inesperado quebre a página.
         */
        const itens = Array.isArray(dados.roteiro?.[chave])
          ? dados.roteiro[chave]
          : [];

        return (
          <section key={chave} className="pagina-feedback__secao-roteiro">
            <h4 className="pagina-feedback__rotulo-secao">{rotulo}</h4>

            {itens.length === 0 ? (
              <p className="pagina-feedback__sem-itens">Nenhum item.</p>
            ) : (
              <ul className="pagina-feedback__lista-roteiro">
                {itens.map((item, indice) => (
                  <li key={`${chave}-${indice}`}>{item}</li>
                ))}
              </ul>
            )}
          </section>
        );
      })}
    </div>
  );
}

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
    <div className="pagina-feedback">
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
            resumoDoRoteiro(feedback.dados)
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
                  {item.mes_referencia
                    ? formatarMes(item.mes_referencia)
                    : 'Todo o histórico'}
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
