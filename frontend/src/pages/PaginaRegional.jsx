/**
 * Página da visão regional (Patrícia) sobre a loja do Diego.
 *
 * Lê o consolidado de estado.regional e organiza em resultado mês a mês,
 * acompanhamento dos feedbacks e anotações da regional sobre a liderança.
 * Nada é calculado aqui: os números chegam prontos de
 * GET /api/regional/desempenho-gerente.
 */

import { useEffect } from 'react';

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { AnotacoesRegional } from '../components/AnotacoesRegional.jsx';
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

// Importa o CSS desta página.
import './PaginaRegional.css';

/**
 * Componente PaginaRegional.
 *
 * Não recebe props: lê do contexto o consolidado (estado.regional) e a ação
 * carregarRegional. Devolve o cabeçalho da loja, a tabela de resultado mês a
 * mês, a seção de acompanhamento dos feedbacks e as anotações da regional.
 *
 * Exemplo de uso: <PaginaRegional />
 */
export function PaginaRegional() {
  const { estado, carregarRegional } = useApp();

  const { status, dados, erro } = estado.regional;

  /*
   * useEffect roda um código depois que a tela aparece.
   *
   * Recarregamos TODA vez que a visão regional é aberta: assim a cobertura e
   * a situação dos vendedores incluem os roteiros que o Diego gerou desde a
   * última visita. O contexto guarda o último resultado; sem este pedido, a
   * tela mostraria dados velhos.
   *
   * Em desenvolvimento, o StrictMode executa o efeito duas vezes. O provider
   * cancela o pedido anterior antes de começar o novo, então isso não gera
   * resposta duplicada na tela.
   */
  useEffect(() => {
    carregarRegional();
  }, [carregarRegional]);

  // Primeira carga (ocioso) e recarga aparecem como carregando.
  if (status === STATUS.OCIOSO || status === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando a visão regional…"
        linhas={4}
        variante="cartao"
      />
    );
  }

  if (status === STATUS.ERRO) {
    return (
      <EstadoErro
        mensagem={erro}
        aoTentarDeNovo={() => carregarRegional()}
      />
    );
  }

  if (!dados) {
    return (
      <EstadoVazio
        titulo="Sem dados da regional"
        descricao="Não há consolidado da loja para mostrar agora."
      />
    );
  }

  // O contrato garante estes campos; os padrões evitam quebra se faltar algo.
  const resultado = dados.resultado_loja ?? [];
  const acompanhamento = dados.acompanhamento_feedback ?? {};
  const vendedores = acompanhamento.vendedores ?? [];

  return (
    <div className="pagina-regional">
      {/* ---------- Cabeçalho da loja ---------- */}
      <header className="pagina-regional__cabecalho">
        <h2 className="pagina-regional__titulo">
          Loja {dados.loja_nome} — gerente {dados.gerente_nome}
        </h2>
        <p className="pagina-regional__periodo">
          Período: {textoPeriodo(dados.periodo_inicio, dados.periodo_fim)}
        </p>
      </header>

      {/* ---------- Resultado da loja por mês ---------- */}
      <section
        className="pagina-regional__secao"
        aria-labelledby="titulo-resultado-loja"
      >
        <h3
          id="titulo-resultado-loja"
          className="pagina-regional__subtitulo"
        >
          Resultado da loja por mês
        </h3>

        {resultado.length === 0 ? (
          <p className="pagina-regional__vazio">
            Nenhum mês com dados para mostrar.
          </p>
        ) : (
          /*
           * Container com rolagem horizontal: em telas estreitas a tabela
           * anda para o lado em vez de espremer as oito colunas.
           */
          <div className="pagina-regional__tabela-container">
            {/*
             * Tabela acessível: <caption> explica o conteúdo e <th scope>
             * diz ao leitor de tela se o cabeçalho vale para a coluna
             * ("col") ou para a linha ("row").
             */}
            <table className="pagina-regional__tabela pagina-regional__tabela--resultado">
              <caption className="pagina-regional__legenda-tabela">
                Resultado mês a mês. "Mês parcial" indica um mês ainda em
                andamento.
              </caption>

              <thead>
                <tr>
                  <th scope="col">Mês</th>
                  <th scope="col" className="pagina-regional__numero">
                    Meta da loja
                  </th>
                  <th scope="col" className="pagina-regional__numero">
                    Vendas da loja
                  </th>
                  <th scope="col" className="pagina-regional__numero">
                    Atingimento da loja
                  </th>
                  <th scope="col" className="pagina-regional__numero">
                    Vendas dos vendedores
                  </th>
                  <th scope="col" className="pagina-regional__numero">
                    Atingimento dos vendedores
                  </th>
                  <th scope="col" className="pagina-regional__numero">
                    Vendas do gerente
                  </th>
                  <th scope="col" className="pagina-regional__numero">
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
                      <th scope="row" className="pagina-regional__mes">
                        <span className="pagina-regional__mes-conteudo">
                          <span className="pagina-regional__mes-nome">
                            {formatarMes(mes.mes)}
                          </span>
                          {mes.mes_parcial && (
                            <Selo texto="Mês parcial" tom="atencao" />
                          )}
                        </span>
                      </th>

                      <td className="pagina-regional__numero">
                        {formatarMoeda(mes.meta_loja)}
                      </td>
                      <td className="pagina-regional__numero">
                        {formatarMoeda(mes.vendas_loja)}
                      </td>

                      <td className="pagina-regional__numero">
                        {/* Célula com o número e, embaixo, o selo. */}
                        <span className="pagina-regional__atingimento">
                          <span className="pagina-regional__atingimento-valor">
                            {formatarPercentual(mes.atingimento_loja)}
                          </span>
                          {selo && <Selo texto={selo.texto} tom={selo.tom} />}
                        </span>
                      </td>

                      <td className="pagina-regional__numero">
                        {formatarMoeda(mes.vendas_vendedores)}
                      </td>
                      <td className="pagina-regional__numero">
                        {formatarPercentual(mes.atingimento_vendedores)}
                      </td>
                      <td className="pagina-regional__numero">
                        {formatarMoeda(mes.vendas_gerente)}
                      </td>
                      <td className="pagina-regional__numero">
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
        className="pagina-regional__secao"
        aria-labelledby="titulo-acompanhamento"
      >
        <h3
          id="titulo-acompanhamento"
          className="pagina-regional__subtitulo"
        >
          Acompanhamento dos feedbacks
        </h3>

        <div className="pagina-regional__cartoes">
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
        <p className="pagina-regional__esclarecimento">
          Roteiro preparado significa que o gerente gerou o rascunho no
          sistema. Isso não confirma que a conversa de feedback aconteceu.
        </p>

        {vendedores.length === 0 ? (
          <p className="pagina-regional__vazio">
            Nenhum vendedor para mostrar.
          </p>
        ) : (
          <div className="pagina-regional__tabela-container">
            <table className="pagina-regional__tabela pagina-regional__tabela--acompanhamento">
              <caption className="pagina-regional__legenda-tabela">
                Situação dos roteiros por vendedor. Campos sem data aparecem
                como travessão.
              </caption>

              <thead>
                <tr>
                  <th scope="col">Vendedor</th>
                  <th scope="col">Situação</th>
                  <th scope="col" className="pagina-regional__numero">
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
                    <th scope="row" className="pagina-regional__vendedor">
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

                    <td className="pagina-regional__numero">
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

      {/* ---------- Anotações da regional ---------- */}
      <AnotacoesRegional anotacoes={dados.anotacoes_regional ?? []} />
    </div>
  );
}
