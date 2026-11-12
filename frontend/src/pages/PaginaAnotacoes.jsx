/**
 * Página da aba Anotações do colaborador selecionado, em formato de conversa.
 *
 * A conversa (título, balões, campo de escrita, contador, botão e erro) vive
 * no componente reutilizável ChatAnotacoes. Esta página cuida do que é
 * específico do gerente: estados de carregamento/erro/vazio, orientação e a
 * seção recolhível com as anotações do time.
 *
 * A página NÃO calcula nada nem fala com a API: lê estado.detalhes e
 * estado.novaAnotacao e chama as ações do contexto.
 */

import { ANOTACAO_TEXTO_MAXIMO, STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { ChatAnotacoes } from '../components/ChatAnotacoes.jsx';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { formatarData } from '../utilitarios/formatadores.js';
import { ordenarAnotacoes } from '../utilitarios/ordenarAnotacoes.js';

// Importa o CSS desta página (estrutura, orientação e seção do time).
import './PaginaAnotacoes.css';

/**
 * Componente PaginaAnotacoes.
 *
 * Não recebe props: lê do contexto o histórico (estado.detalhes), o envio de
 * anotação (estado.novaAnotacao), o vendedor selecionado e as ações
 * selecionarVendedor (para "tentar de novo") e adicionarAnotacao (para
 * enviar).
 *
 * Exemplo de uso (com key, para o rascunho zerar ao trocar de pessoa):
 *   <PaginaAnotacoes key={vendedorSelecionadoId} />
 */
export function PaginaAnotacoes() {
  const { estado, selecionarVendedor, adicionarAnotacao } = useApp();

  const { status, dados, erro } = estado.detalhes;
  const vendedorId = estado.vendedorSelecionadoId;

  // "ocioso" também conta como carregando: ao trocar de vendedor, o reducer
  // zera os detalhes e o pedido começa logo em seguida.
  if (status === STATUS.OCIOSO || status === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando as anotações…"
        linhas={3}
        variante="cartao"
      />
    );
  }

  if (status === STATUS.ERRO) {
    return (
      <EstadoErro
        mensagem={erro}
        aoTentarDeNovo={
          vendedorId ? () => selecionarVendedor(vendedorId) : undefined
        }
      />
    );
  }

  if (!dados) {
    return (
      <EstadoVazio
        titulo="Sem dados do colaborador"
        descricao="Escolha um colaborador para ver as anotações."
      />
    );
  }

  // Nome para os textos da página; se faltar, usamos uma expressão genérica.
  const nome =
    typeof dados.nome === 'string' && dados.nome.trim() !== ''
      ? dados.nome
      : 'o colaborador';

  // --- Time: só leitura, da mais recente para a mais antiga ---
  const anotacoesDoTime = ordenarAnotacoes(dados.anotacoes_do_time ?? []);

  const { status: statusEnvio, erro: erroDoEnvio } = estado.novaAnotacao;

  /**
   * Envia a anotação digitada no chat.
   *
   * Recebe o texto (do componente) e devolve a Promise da ação do contexto:
   * true quando gravou. Sem vendedor selecionado não há o que gravar.
   */
  async function enviarAnotacao(texto) {
    if (!vendedorId) {
      return false;
    }

    return adicionarAnotacao(vendedorId, texto);
  }

  return (
    <div className="pagina-anotacoes">
      {/*
       * Orientação curta e verdadeira: as anotações ficam gravadas (arquivo
       * próprio do backend, testado) e entram no prompt da IA.
       */}
      <p className="pagina-anotacoes__orientacao">
        Escreva aqui o que observar durante o mês. As anotações ficam
        guardadas e entram no feedback.
      </p>

      <ChatAnotacoes
        titulo={`Anotações sobre ${nome}`}
        nome={nome}
        anotacoes={dados.anotacoes ?? []}
        aoEnviar={enviarAnotacao}
        enviando={statusEnvio === STATUS.CARREGANDO}
        erroEnvio={statusEnvio === STATUS.ERRO ? erroDoEnvio : null}
        textoMaximo={ANOTACAO_TEXTO_MAXIMO}
        rotuloAcessivel="Nova anotação"
        idCampo="nova-anotacao"
      >
        {/*
         * <details> é o bloco que abre e fecha ao clicar no <summary> (o
         * título). Fecha por padrão para não competir com a conversa.
         */}
        <details className="pagina-anotacoes__time">
          <summary className="pagina-anotacoes__time-resumo">
            Anotações sobre o time ({anotacoesDoTime.length})
          </summary>

          <p className="pagina-anotacoes__explicacao">
            Observações sobre a loja toda, que ajudam a entender o contexto.
          </p>

          {anotacoesDoTime.length === 0 ? (
            <EstadoVazio
              titulo="Nenhuma anotação do time"
              descricao="Ainda não há observações sobre a loja toda."
            />
          ) : (
            <ul className="pagina-anotacoes__lista-time">
              {anotacoesDoTime.map((anotacao, indice) => (
                <li
                  key={`time-${anotacao.data}-${indice}`}
                  className="pagina-anotacoes__item-time"
                >
                  <time dateTime={anotacao.data}>
                    {formatarData(anotacao.data)}
                  </time>

                  <p className="pagina-anotacoes__texto">{anotacao.texto}</p>
                </li>
              ))}
            </ul>
          )}
        </details>
      </ChatAnotacoes>
    </div>
  );
}
