/**
 * Aba Dados da visão regional (Etapa 8).
 *
 * Mostra o consolidado da loja escolhida: cabeçalho da loja, resultado mês a
 * mês e acompanhamento dos feedbacks do time. Nada é calculado aqui: os
 * números chegam prontos de GET /api/regional/lojas/{id}/historico.
 *
 * Diferenças em relação à página antiga (PaginaRegional):
 * - lê estado.detalhesLoja, preenchido quando a loja é selecionada;
 * - NÃO busca dados sozinha (a seleção da loja já dispara o carregamento);
 * - NÃO mostra as anotações da regional (agora são a aba Anotações).
 */

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { CartaoIndicador } from '../components/CartaoIndicador.jsx';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { Selo } from '../components/Selo.jsx';
import {
  formatarData,
  formatarDataHora,
  formatarInteiro,
  formatarMes,
  formatarMoeda,
  formatarPercentual,
  rotuloSituacaoAcompanhamento,
} from '../utilitarios/formatadores.js';
import {
  seloDoAtingimento,
  textoPeriodo,
  tomDoAcompanhamento,
} from '../utilitarios/visaoRegional.js';

// Importa o CSS desta página (cópia própria; a página antiga será removida).
import './PaginaDadosRegional.css';

/**
 * Componente PaginaDadosRegional.
 *
 * Não recebe props: lê do contexto o histórico da loja (estado.detalhesLoja),
 * a loja selecionada e a ação selecionarLoja (para "tentar de novo").
 *
 * Devolve o cabeçalho da loja, a tabela de resultado mês a mês e a seção de
 * acompanhamento dos feedbacks. Sem useEffect: quem carrega é selecionarLoja.
 *
 * Exemplo de uso: <PaginaDadosRegional />
 */
export function PaginaDadosRegional() {
  const { estado, selecionarLoja } = useApp();

  const { status, dados, erro } = estado.detalhesLoja;
  const lojaId = estado.lojaSelecionadaId;

  // Primeira carga (ocioso) e recarga aparecem como carregando.
  if (status === STATUS.OCIOSO || status === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando os dados da loja…"
        linhas={4}
        variante="cartao"
      />
    );
  }

  if (status === STATUS.ERRO) {
    return (
      <EstadoErro
        mensagem={erro}
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
        descricao="Escolha uma loja no card da barra lateral para ver os dados dela."
      />
    );
  }

  // O contrato garante estes campos; os padrões evitam quebra se faltar algo.
  const resultado = dados.resultado_loja ?? [];
  const acompanhamento = dados.acompanhamento_feedback ?? {};
  const vendedores = acompanhamento.vendedores ?? [];

  return (
    <div className="pagina-dados-regional">
      {/* ---------- Cabeçalho da loja ---------- */}
      <header className="pagina-dados-regional__cabecalho">
        <h2 className="pagina-dados-regional__titulo">
          Loja {dados.loja_nome} — gerente {dados.gerente_nome}
        </h2>
        <p className="pagina-dados-regional__periodo">
          Período: {textoPeriodo(dados.periodo_inicio, dados.periodo_fim)}
        </p>
      </header>

      {/* ---------- Resultado da loja por mês ---------- */}
      <section
        className="pagina-dados-regional__secao"
        aria-labelledby="titulo-resultado-loja-regional"
      >
        <h3
          id="titulo-resultado-loja-regional"
          className="pagina-dados-regional__subtitulo"
        >
          Resultado da loja por mês
        </h3>

        {resultado.length === 0 ? (
          <p className="pagina-dados-regional__vazio">
            Nenhum mês com dados para mostrar.
          </p>
        ) : (
          /*
           * Container com rolagem horizontal: em telas estreitas a tabela
           * anda para o lado em vez de espremer as oito colunas.
           * tabIndex={0} permite chegar nele pelo Tab e rolar com as setas;
           * role="region" + aria-label nomeiam o bloco para o leitor de tela.
           */
          <div
            className="pagina-dados-regional__tabela-container"
            tabIndex={0}
            role="region"
            aria-label="Resultado da loja por mês, tabela com rolagem horizontal"
          >
            {/*
             * Tabela acessível: <caption> explica o conteúdo e <th scope>
             * diz ao leitor de tela se o cabeçalho vale para a coluna
             * ("col") ou para a linha ("row").
             */}
            <table className="pagina-dados-regional__tabela pagina-dados-regional__tabela--resultado">
              <caption className="pagina-dados-regional__legenda-tabela">
                Resultado mês a mês. &quot;Mês parcial&quot; indica um mês
                ainda em andamento.
              </caption>

              <thead>
                <tr>
                  <th scope="col">Mês</th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Meta da loja
                  </th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Vendas da loja
                  </th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Atingimento da loja
                  </th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Vendas dos vendedores
                  </th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Atingimento dos vendedores
                  </th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Vendas do gerente
                  </th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Participação do gerente
                  </th>
                </tr>
              </thead>

              <tbody>
                {resultado.map((mes) => {
                  /*
                   * O selo só escolhe o texto a partir do número já
                   * calculado pelo backend (vendas ÷ meta). Nenhuma conta
                   * nova é feita aqui.
                   */
                  const selo = seloDoAtingimento(mes.atingimento_loja);

                  return (
                    <tr key={mes.mes}>
                      {/* O mês é o cabeçalho da própria linha. */}
                      <th
                        scope="row"
                        className="pagina-dados-regional__mes"
                      >
                        <span className="pagina-dados-regional__mes-conteudo">
                          <span className="pagina-dados-regional__mes-nome">
                            {formatarMes(mes.mes)}
                          </span>
                          {mes.mes_parcial && (
                            <Selo texto="Mês parcial" tom="atencao" />
                          )}
                        </span>
                      </th>

                      <td className="pagina-dados-regional__numero">
                        {formatarMoeda(mes.meta_loja)}
                      </td>
                      <td className="pagina-dados-regional__numero">
                        {formatarMoeda(mes.vendas_loja)}
                      </td>

                      <td className="pagina-dados-regional__numero">
                        {/* Célula com o número e, embaixo, o selo. */}
                        <span className="pagina-dados-regional__atingimento">
                          <span className="pagina-dados-regional__atingimento-valor">
                            {formatarPercentual(mes.atingimento_loja)}
                          </span>
                          {selo && <Selo texto={selo.texto} tom={selo.tom} />}
                        </span>
                      </td>

                      <td className="pagina-dados-regional__numero">
                        {formatarMoeda(mes.vendas_vendedores)}
                      </td>
                      <td className="pagina-dados-regional__numero">
                        {formatarPercentual(mes.atingimento_vendedores)}
                      </td>
                      <td className="pagina-dados-regional__numero">
                        {formatarMoeda(mes.vendas_gerente)}
                      </td>
                      <td className="pagina-dados-regional__numero">
                        {formatarPercentual(mes.participacao_gerente)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* ---------- Acompanhamento dos feedbacks ---------- */}
      <section
        className="pagina-dados-regional__secao"
        aria-labelledby="titulo-acompanhamento-regional"
      >
        <h3
          id="titulo-acompanhamento-regional"
          className="pagina-dados-regional__subtitulo"
        >
          Acompanhamento dos feedbacks
        </h3>

        <div className="pagina-dados-regional__cartoes">
          {/*
           * Cobertura = vendedores com roteiro dividido pelo total de
           * vendedores. A conta é do backend; aqui só formatamos a fração.
           */}
          <CartaoIndicador
            rotulo="Cobertura de roteiros"
            valorFormatado={formatarPercentual(acompanhamento.cobertura)}
            detalhe={`${formatarInteiro(acompanhamento.vendedores_com_roteiro)} de ${formatarInteiro(acompanhamento.total_vendedores)} vendedores com roteiro preparado`}
          />

          <CartaoIndicador
            rotulo="Total de roteiros preparados"
            valorFormatado={formatarInteiro(
              acompanhamento.total_roteiros_preparados,
            )}
          />
        </div>

        {/*
         * Frase fixa: "preparado" é o rascunho gerado, não a conversa feita.
         * O sistema não sabe se o feedback aconteceu.
         */}
        <p className="pagina-dados-regional__esclarecimento">
          Roteiro preparado significa que o gerente gerou o rascunho no
          sistema. Isso não confirma que a conversa de feedback aconteceu.
        </p>

        {vendedores.length === 0 ? (
          <p className="pagina-dados-regional__vazio">
            Nenhum vendedor para mostrar.
          </p>
        ) : (
          /*
           * Tabela larga também: rola dentro do container e pode ser
           * alcançada e rolada pelo teclado (tabIndex={0}).
           */
          <div
            className="pagina-dados-regional__tabela-container"
            tabIndex={0}
            role="region"
            aria-label="Acompanhamento dos feedbacks por vendedor, tabela com rolagem horizontal"
          >
            <table className="pagina-dados-regional__tabela pagina-dados-regional__tabela--acompanhamento">
              <caption className="pagina-dados-regional__legenda-tabela">
                Situação dos roteiros por vendedor. Campos sem data aparecem
                como travessão.
              </caption>

              <thead>
                <tr>
                  <th scope="col">Vendedor</th>
                  <th scope="col">Situação</th>
                  <th scope="col" className="pagina-dados-regional__numero">
                    Anotações do gerente
                  </th>
                  <th scope="col">Última anotação</th>
                  <th scope="col">Último roteiro</th>
                </tr>
              </thead>

              <tbody>
                {vendedores.map((vendedor) => (
                  <tr key={vendedor.vendedor_id}>
                    {/* Nome é o cabeçalho da própria linha. */}
                    <th
                      scope="row"
                      className="pagina-dados-regional__vendedor"
                    >
                      {vendedor.nome}
                    </th>

                    <td>
                      {/*
                       * O texto vem de rotuloSituacaoAcompanhamento e o tom,
                       * de tomDoAcompanhamento. Situação desconhecida fica
                       * neutra em vez de virar alerta.
                       */}
                      <Selo
                        texto={rotuloSituacaoAcompanhamento(
                          vendedor.situacao,
                        )}
                        tom={tomDoAcompanhamento(vendedor.situacao)}
                      />
                    </td>

                    <td className="pagina-dados-regional__numero">
                      {formatarInteiro(vendedor.anotacoes_do_gerente)}
                    </td>
                    <td>{formatarData(vendedor.ultima_anotacao_em)}</td>
                    <td>
                      {formatarDataHora(vendedor.ultimo_roteiro_em)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
