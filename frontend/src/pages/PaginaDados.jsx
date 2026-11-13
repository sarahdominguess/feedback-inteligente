/**
 * Página da aba Dados do colaborador selecionado.
 *
 * Lê o histórico pronto de estado.detalhes e organiza em indicadores,
 * totais e uma tabela mês a mês. Não calcula nada: só formata para exibição.
 */

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { CartaoIndicador } from '../components/CartaoIndicador.jsx';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { Selo } from '../components/Selo.jsx';
import {
  formatarInteiro,
  formatarMes,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
  rotuloMetrica,
} from '../utilitarios/formatadores.js';
import {
  acharComparativo,
  montarDetalheComparativo,
} from '../utilitarios/dadosDoVendedor.js';

// Importa o CSS desta página.
import './PaginaDados.css';

/**
 * Componente PaginaDados.
 *
 * Não recebe props: lê do contexto o histórico (estado.detalhes), o
 * vendedor selecionado e a ação selecionarVendedor (usada no "tentar de
 * novo"). O estado é a única fonte de verdade.
 *
 * Devolve a página com três seções: indicadores do período, totais e
 * resultado mês a mês.
 *
 * Exemplo de uso: <PaginaDados />
 */
export function PaginaDados() {
  const { estado, selecionarVendedor } = useApp();

  // Atalhos para o pedaço do estado que esta página usa.
  const { status, dados, erro } = estado.detalhes;
  const vendedorId = estado.vendedorSelecionadoId;

  // "ocioso" também é tratado como carregando: ao trocar de vendedor, o
  // reducer zera os detalhes e o pedido começa logo em seguida.
  if (status === STATUS.OCIOSO || status === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando os dados do colaborador…"
        linhas={4}
        variante="cartao"
      />
    );
  }

  if (status === STATUS.ERRO) {
    return (
      <EstadoErro
        mensagem={erro}
        // Só oferece "tentar de novo" se existe alguém selecionado.
        aoTentarDeNovo={
          vendedorId ? () => selecionarVendedor(vendedorId) : undefined
        }
      />
    );
  }

  // Deu certo, mas sem histórico: explica em vez de mostrar uma tela vazia.
  if (!dados) {
    return (
      <EstadoVazio
        titulo="Sem dados do colaborador"
        descricao="Escolha um colaborador na lista para ver os indicadores."
      />
    );
  }

  // O contrato garante estes campos; os padrões evitam quebra se algo faltar.
  const metricas = dados.metricas ?? {};
  const comparativo = dados.comparativo ?? [];
  const resumoMensal = dados.resumo_mensal ?? [];

  /*
   * Configuração dos três cartões. Cada item diz:
   * - nome: nome técnico usado para achar o comparativo;
   * - valorFormatado: texto já pronto da métrica;
   * - formatarMedia: como formatar a média do time do MESMO jeito.
   */
  const indicadores = [
    {
      nome: 'ticket_medio',
      valorFormatado: formatarMoeda(metricas.ticket_medio),
      formatarMedia: formatarMoeda,
    },
    {
      nome: 'pecas_por_atendimento',
      valorFormatado: formatarNumero(metricas.pecas_por_atendimento, 2),
      formatarMedia: (valor) => formatarNumero(valor, 2),
    },
    {
      nome: 'conversao',
      valorFormatado: formatarPercentual(metricas.conversao),
      formatarMedia: formatarPercentual,
    },
  ];

  // Totais do período, também só formatados (nada é somado aqui).
  const totais = [
    { rotulo: 'Valor vendido', valor: formatarMoeda(metricas.valor_vendido) },
    { rotulo: 'Vendas', valor: formatarInteiro(metricas.vendas) },
    { rotulo: 'Peças', valor: formatarInteiro(metricas.pecas) },
    {
      rotulo: 'Atendimentos',
      valor: formatarInteiro(metricas.atendimentos),
    },
  ];

  return (
    <div className="pagina-dados">
      {/* ---------- Indicadores do período ---------- */}
      <section
        className="pagina-dados__secao"
        aria-labelledby="titulo-indicadores"
      >
        <h2
          id="titulo-indicadores"
          className="pagina-dados__titulo pagina-dados__titulo--principal"
        >
          Indicadores do período
        </h2>

        <div className="pagina-dados__cartoes">
          {indicadores.map(({ nome, valorFormatado, formatarMedia }) => {
            // O comparativo do time pode não ter esta métrica: nesse caso o
            // cartão aparece sem selo e sem a linha de detalhe.
            const itemComparativo = acharComparativo(comparativo, nome);

            const detalhe = itemComparativo
              ? montarDetalheComparativo(
                  itemComparativo,
                  formatarMedia(itemComparativo.media_time),
                )
              : undefined;

            return (
              <CartaoIndicador
                key={nome}
                rotulo={rotuloMetrica(nome)}
                valorFormatado={valorFormatado}
                detalhe={detalhe}
                situacao={itemComparativo?.situacao}
              />
            );
          })}
        </div>
      </section>

      {/* ---------- Totais do período ---------- */}
      <section
        className="pagina-dados__secao"
        aria-labelledby="titulo-totais"
      >
        <h2 id="titulo-totais" className="pagina-dados__titulo">
          Totais do período
        </h2>

        {/*
         * <dl> é a lista de termos: cada <dt> é o nome do indicador e cada
         * <dd> é o valor. O <div> apenas agrupa o par para o CSS.
         */}
        <dl className="pagina-dados__totais">
          {totais.map((total) => (
            <div key={total.rotulo} className="pagina-dados__total">
              <dt className="pagina-dados__total-rotulo">{total.rotulo}</dt>
              <dd className="pagina-dados__total-valor">{total.valor}</dd>
            </div>
          ))}
        </dl>
      </section>

      {/* ---------- Resultado por mês ---------- */}
      <section
        className="pagina-dados__secao"
        aria-labelledby="titulo-mensal"
      >
        <h2 id="titulo-mensal" className="pagina-dados__titulo">
          Resultado por mês
        </h2>

        {resumoMensal.length === 0 ? (
          <p className="pagina-dados__vazio">
            Nenhum mês com dados para mostrar.
          </p>
        ) : (
          /*
           * O container permite rolar a tabela na horizontal em telas
           * estreitas, sem espremer as colunas nem quebrar a página.
           *
           * tabIndex={0} coloca o container na ordem do Tab, para rolar com
           * as setas. role="region" + aria-label dão um nome ao bloco para o
           * leitor de tela avisar onde a pessoa está.
           */
          <div
            className="pagina-dados__tabela-container"
            tabIndex={0}
            role="region"
            aria-label="Resultado por mês, tabela com rolagem horizontal"
          >
            {/*
             * Tabela acessível: <caption> explica o conteúdo; <th scope>
             * diz ao leitor de tela se o cabeçalho vale para a coluna toda
             * ("col") ou para a linha ("row").
             */}
            <table className="pagina-dados__tabela">
              <caption className="pagina-dados__legenda-tabela">
                Indicadores mês a mês. "Mês parcial" indica um mês ainda em
                andamento.
              </caption>

              <thead>
                <tr>
                  <th scope="col">Mês</th>
                  <th scope="col" className="pagina-dados__numero">
                    Valor vendido
                  </th>
                  <th scope="col" className="pagina-dados__numero">
                    Vendas
                  </th>
                  <th scope="col" className="pagina-dados__numero">
                    Ticket médio
                  </th>
                  <th scope="col" className="pagina-dados__numero">
                    P.A.
                  </th>
                  <th scope="col" className="pagina-dados__numero">
                    Conversão
                  </th>
                  <th scope="col" className="pagina-dados__numero">
                    Meta
                  </th>
                  <th scope="col" className="pagina-dados__numero">
                    Atingimento
                  </th>
                </tr>
              </thead>

              <tbody>
                {resumoMensal.map((mes) => (
                  <tr key={mes.mes}>
                    {/* Mês é o cabeçalho da própria linha. */}
                    <th scope="row" className="pagina-dados__mes">
                      <span className="pagina-dados__mes-conteudo">
                        <span className="pagina-dados__mes-nome">
                          {formatarMes(mes.mes)}
                        </span>
                        {mes.mes_parcial && (
                          <Selo texto="Mês parcial" tom="atencao" />
                        )}
                      </span>
                    </th>

                    <td className="pagina-dados__numero">
                      {formatarMoeda(mes.valor_vendido)}
                    </td>
                    <td className="pagina-dados__numero">
                      {formatarInteiro(mes.vendas)}
                    </td>
                    <td className="pagina-dados__numero">
                      {formatarMoeda(mes.ticket_medio)}
                    </td>
                    <td className="pagina-dados__numero">
                      {formatarNumero(mes.pecas_por_atendimento, 2)}
                    </td>
                    <td className="pagina-dados__numero">
                      {formatarPercentual(mes.conversao)}
                    </td>
                    <td className="pagina-dados__numero">
                      {formatarMoeda(mes.meta)}
                    </td>
                    <td className="pagina-dados__numero">
                      {formatarPercentual(mes.atingimento_meta)}
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
