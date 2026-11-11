/**
 * Painel TEMPORÁRIO de verificação da API.
 *
 * Serve só para conferir, no navegador, que o contexto, os serviços e o
 * backend conversam. Ele será substituído pelas telas reais na Etapa 5;
 * por isso o visual é o mais simples possível e nenhum número é formatado.
 *
 * Regra importante: esta tela NÃO calcula nada e NÃO chama axios/fetch.
 * Ela lê o estado e chama as ações do contexto (useApp).
 */

import { useEffect } from 'react';

import { ABAS, STATUS, VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { API_URL } from '../services/api.js';

// Rótulos em português para os botões das abas. O valor de cada aba continua
// sendo o texto técnico de ABAS.
const ROTULOS_ABAS = {
  [ABAS.ANOTACOES]: 'Anotações',
  [ABAS.DADOS]: 'Dados',
  [ABAS.FEEDBACK]: 'Feedback',
};

// Rótulos das visões.
const ROTULOS_VISOES = {
  [VISOES.GERENTE]: 'Gerente',
  [VISOES.REGIONAL]: 'Regional',
};

// Nomes das quatro seções do roteiro, na ordem em que queremos mostrar.
const SECOES_ROTEIRO = [
  ['pontos_positivos', 'Pontos positivos'],
  ['pontos_melhoria', 'Pontos de melhoria'],
  ['possiveis_motivos', 'Possíveis motivos'],
  ['roteiro_conversa', 'Roteiro da conversa'],
];

/**
 * Mostra um valor exatamente como veio da API.
 *
 * Não converte fração em porcentagem, não arredonda e não calcula nada.
 * Valores ausentes (null/undefined) aparecem como o texto "null" para
 * deixar claro que a API não tinha aquele dado.
 */
function bruto(valor) {
  if (valor === null || valor === undefined) {
    return 'null';
  }
  return String(valor);
}

/**
 * Componente com o painel de verificação.
 *
 * Usa o estado e as ações do AppProvider para carregar a lista, selecionar
 * um vendedor, gerar feedback e carregar a visão regional.
 */
export function PainelVerificacao() {
  const {
    estado,
    carregarVendedores,
    selecionarVendedor,
    gerarFeedback,
    carregarRegional,
    mudarAba,
    mudarVisao,
  } = useApp();

  // Carrega a lista uma vez ao abrir a página.
  // Em desenvolvimento, o StrictMode monta e desmonta o componente duas
  // vezes de propósito; por isso o efeito roda duas vezes e a lista é
  // buscada duas vezes. É esperado e inofensivo (o resultado só substitui o
  // anterior). A dependência é a própria função: ela só muda se a loja mudar.
  useEffect(() => {
    carregarVendedores();
  }, [carregarVendedores]);

  const selecionadoId = estado.vendedorSelecionadoId;
  const feedbackDoSelecionado = selecionadoId
    ? estado.feedbacks[selecionadoId]
    : undefined;
  const gerandoFeedback =
    feedbackDoSelecionado?.status === STATUS.CARREGANDO;

  return (
    <div className="painel">
      <header className="painel-cabecalho">
        <h1>Feedback Inteligente — painel de verificação da API (temporário)</h1>
        <p>
          API em uso: <code>{API_URL}</code>
        </p>
      </header>

      {/* ---------- Lista de vendedores ---------- */}
      <section>
        <h2>Vendedores da loja {estado.lojaId}</h2>
        <p>Status da lista: {estado.vendedores.status}</p>

        {/* A mensagem de erro vem do estado (texto do backend). */}
        {estado.vendedores.status === STATUS.ERRO && (
          <p className="erro">{estado.vendedores.erro}</p>
        )}

        <ul className="lista-vendedores">
          {estado.vendedores.dados.map((vendedor) => (
            <li key={vendedor.vendedor_id}>
              <strong>{vendedor.nome}</strong> ({vendedor.vendedor_id} —{' '}
              {vendedor.cargo})
              <button
                type="button"
                onClick={() => selecionarVendedor(vendedor.vendedor_id)}
              >
                Selecionar
              </button>
              {/* Valores brutos, sem nenhuma conta ou formatação. */}
              <div className="valores-brutos">
                valor_vendido: {bruto(vendedor.metricas.valor_vendido)} |
                vendas: {bruto(vendedor.metricas.vendas)} | pecas:{' '}
                {bruto(vendedor.metricas.pecas)} | atendimentos:{' '}
                {bruto(vendedor.metricas.atendimentos)} | ticket_medio:{' '}
                {bruto(vendedor.metricas.ticket_medio)} |
                pecas_por_atendimento:{' '}
                {bruto(vendedor.metricas.pecas_por_atendimento)} | conversao:{' '}
                {bruto(vendedor.metricas.conversao)}
              </div>
            </li>
          ))}
        </ul>

        <p className="legenda">
          Valores brutos; a formatação em % vem na Etapa 5.
        </p>
      </section>

      {/* ---------- Detalhes do vendedor selecionado ---------- */}
      <section>
        <h2>Vendedor selecionado</h2>
        <p>Selecionado: {selecionadoId ?? 'nenhum'}</p>
        <p>Status dos detalhes: {estado.detalhes.status}</p>

        {estado.detalhes.status === STATUS.ERRO && (
          <p className="erro">{estado.detalhes.erro}</p>
        )}

        {estado.detalhes.dados && (
          <ul>
            <li>
              Meses no resumo mensal:{' '}
              {estado.detalhes.dados.resumo_mensal.length}
            </li>
            <li>
              Anotações sobre a pessoa:{' '}
              {estado.detalhes.dados.anotacoes.length}
            </li>
            <li>
              Anotações do time:{' '}
              {estado.detalhes.dados.anotacoes_do_time.length}
            </li>
            <li>
              Roteiros já preparados:{' '}
              {estado.detalhes.dados.feedbacks_preparados.length}
            </li>
          </ul>
        )}
      </section>

      {/* ---------- Geração de feedback ---------- */}
      <section>
        <h2>Feedback do selecionado</h2>

        {!selecionadoId && (
          <p>Selecione um vendedor para habilitar a geração.</p>
        )}

        {selecionadoId && (
          <>
            <button
              type="button"
              onClick={() => gerarFeedback(selecionadoId)}
              disabled={gerandoFeedback}
            >
              {gerandoFeedback
                ? 'Gerando... pode levar até 2 minutos'
                : 'Gerar feedback (consome créditos da IA)'}
            </button>

            {/* O roteiro fica guardado por vendedor no estado; trocar de
                selecionado não apaga o que já foi gerado. */}
            {feedbackDoSelecionado?.status === STATUS.ERRO && (
              <p className="erro">{feedbackDoSelecionado.erro}</p>
            )}

            {feedbackDoSelecionado?.status === STATUS.SUCESSO && (
              <div>
                <p>
                  feedback_id: {feedbackDoSelecionado.dados.feedback_id} |
                  gerado_em: {feedbackDoSelecionado.dados.gerado_em} |
                  mes_referencia:{' '}
                  {bruto(feedbackDoSelecionado.dados.mes_referencia)}
                </p>

                {SECOES_ROTEIRO.map(([chave, rotulo]) => (
                  <div key={chave}>
                    <h3>{rotulo}</h3>
                    <ul>
                      {feedbackDoSelecionado.dados.roteiro[chave].map(
                        (item, indice) => (
                          <li key={`${chave}-${indice}`}>{item}</li>
                        ),
                      )}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </section>

      {/* ---------- Visão regional ---------- */}
      <section>
        <h2>Visão regional</h2>
        <button type="button" onClick={carregarRegional}>
          Carregar visão regional
        </button>

        <p>Status da regional: {estado.regional.status}</p>

        {estado.regional.status === STATUS.ERRO && (
          <p className="erro">{estado.regional.erro}</p>
        )}

        {estado.regional.dados && (
          <div>
            <ul>
              {estado.regional.dados.resultado_loja.map((mes) => (
                <li key={mes.mes}>
                  {mes.mes} — meta_loja: {bruto(mes.meta_loja)} |
                  atingimento_loja: {bruto(mes.atingimento_loja)} |
                  atingimento_vendedores: {bruto(mes.atingimento_vendedores)}
                </li>
              ))}
            </ul>

            <p>
              cobertura:{' '}
              {bruto(estado.regional.dados.acompanhamento_feedback.cobertura)}{' '}
              | total_roteiros_preparados:{' '}
              {estado.regional.dados.acompanhamento_feedback
                .total_roteiros_preparados}
            </p>

            <p>
              Anotações da regional:{' '}
              {estado.regional.dados.anotacoes_regional.length}
            </p>
          </div>
        )}
      </section>

      {/* ---------- Aba e visão ativas ---------- */}
      <section>
        <h2>Navegação</h2>
        <p>
          Aba ativa: <strong>{estado.aba}</strong> | Visão ativa:{' '}
          <strong>{estado.visao}</strong>
        </p>

        <div className="botoes-navegacao">
          {Object.entries(ROTULOS_ABAS).map(([valor, rotulo]) => (
            <button
              key={valor}
              type="button"
              onClick={() => mudarAba(valor)}
              disabled={estado.aba === valor}
            >
              {rotulo}
            </button>
          ))}
        </div>

        <div className="botoes-navegacao">
          {Object.entries(ROTULOS_VISOES).map(([valor, rotulo]) => (
            <button
              key={valor}
              type="button"
              onClick={() => mudarVisao(valor)}
              disabled={estado.visao === valor}
            >
              {rotulo}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
