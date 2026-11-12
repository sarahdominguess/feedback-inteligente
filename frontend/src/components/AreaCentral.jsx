/**
 * Área central do app.
 *
 * Decide o que aparece no centro conforme a visão e a aba escolhidas. As duas
 * visões usam o MESMO esqueleto: um pedido para escolher (colaborador ou
 * loja) quando nada está selecionado e, com seleção, o painel da aba ativa.
 */

import { ABAS, ID_PAINEL_ABAS, VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';
// Páginas das abas do gerente.
import { PaginaAnotacoes } from '../pages/PaginaAnotacoes.jsx';
import { PaginaDados } from '../pages/PaginaDados.jsx';
import { PaginaFeedback } from '../pages/PaginaFeedback.jsx';
// Páginas das abas da regional (Etapa 8).
import { PaginaAnotacoesRegional } from '../pages/PaginaAnotacoesRegional.jsx';
import { PaginaDadosRegional } from '../pages/PaginaDadosRegional.jsx';
import { PaginaFeedbackRegional } from '../pages/PaginaFeedbackRegional.jsx';
import { EstadoVazio } from './EstadoVazio.jsx';

// Importa o CSS deste componente.
import './AreaCentral.css';

/**
 * Componente AreaCentral.
 *
 * Não recebe props: lê do contexto a visão, a aba ativa e a seleção de cada
 * visão (vendedor no gerente, loja na regional). O estado é a única fonte de
 * verdade.
 *
 * Devolve:
 *   - visão regional sem loja: EstadoVazio pedindo para escolher uma loja;
 *   - visão regional com loja: a página da aba escolhida (Feedback,
 *     Anotações ou Dados) daquela loja;
 *   - visão do gerente sem colaborador: EstadoVazio pedindo para escolher;
 *   - visão do gerente com colaborador: a página da aba escolhida.
 *
 * As duas raízes são <main>: a área central é o conteúdo principal da página,
 * e cabeçalho e barra lateral ficam fora dela.
 *
 * Exemplo de uso: <AreaCentral />
 */
export function AreaCentral() {
  const { estado } = useApp();

  // Atalhos para os pedaços do estado usados aqui.
  const { visao, vendedorSelecionadoId, lojaSelecionadaId, aba } = estado;

  // A regional acompanha uma LOJA; o gerente, um colaborador.
  if (visao === VISOES.REGIONAL) {
    return (
      <main className="area-central" aria-label="Conteúdo da loja">
        {!lojaSelecionadaId ? (
          <EstadoVazio
            titulo="Escolha uma loja"
            descricao="Escolha uma loja no card da barra lateral para ver as anotações, os dados e o feedback do gerente."
          />
        ) : (
          /*
           * Mesmo painel de abas do gerente: role="tabpanel", id combinado
           * com as abas (ID_PAINEL_ABAS) e aria-labelledby apontando para o
           * botão da aba ativa. tabIndex={0} deixa o painel alcançável pelo
           * Tab enquanto não tem elemento focável dentro.
           */
          <div
            className="area-central__painel"
            role="tabpanel"
            id={ID_PAINEL_ABAS}
            aria-labelledby={`aba-${aba}`}
            tabIndex={0}
          >
            {aba === ABAS.DADOS && <PaginaDadosRegional />}

            {aba === ABAS.ANOTACOES && (
              /*
               * key={lojaSelecionadaId} reinicia a página quando a loja muda:
               * o rascunho digitado para uma loja não pode aparecer no campo
               * da próxima.
               */
              <PaginaAnotacoesRegional key={lojaSelecionadaId} />
            )}

            {aba === ABAS.FEEDBACK && (
              /*
               * key={lojaSelecionadaId} reinicia o estado local da página
               * (o período escolhido) quando a loja muda.
               */
              <PaginaFeedbackRegional key={lojaSelecionadaId} />
            )}
          </div>
        )}
      </main>
    );
  }

  return (
    <main className="area-central" aria-label="Conteúdo do colaborador">
      {!vendedorSelecionadoId ? (
        // Gerente sem ninguém escolhido: explica o próximo passo.
        <EstadoVazio
          titulo="Escolha um colaborador"
          descricao="Escolha um colaborador no card da barra lateral para ver as anotações, os dados e o feedback."
        />
      ) : (
        /*
         * Painel da aba ativa. role="tabpanel" é o papel que o leitor de
         * tela espera depois das abas; aria-labelledby aponta para o botão
         * da aba (id "aba-<valor>") e as abas apontam de volta com
         * aria-controls (id definido em ID_PAINEL_ABAS).
         *
         * tabIndex={0} deixa o painel alcançável pelo Tab enquanto ele não
         * tem nenhum elemento focável dentro.
         */
        <div
          className="area-central__painel"
          role="tabpanel"
          id={ID_PAINEL_ABAS}
          aria-labelledby={`aba-${aba}`}
          tabIndex={0}
        >
          {aba === ABAS.DADOS && <PaginaDados />}

          {aba === ABAS.ANOTACOES && (
            /*
             * key={vendedorSelecionadoId} reinicia a página quando a pessoa
             * muda: o rascunho digitado para um colaborador não pode aparecer
             * no campo do próximo. Mesmo padrão da PaginaFeedback.
             */
            <PaginaAnotacoes key={vendedorSelecionadoId} />
          )}

          {aba === ABAS.FEEDBACK && (
            /*
             * key={vendedorSelecionadoId} reinicia o estado local da página
             * (o período escolhido) quando a pessoa muda.
             */
            <PaginaFeedback key={vendedorSelecionadoId} />
          )}
        </div>
      )}
    </main>
  );
}
