/**
 * Área central do app.
 *
 * Decide o que aparece no centro conforme a visão e a aba escolhidas: as
 * páginas reais (Dados, Anotações e Feedback), a página da regional ou o
 * pedido para escolher um colaborador.
 */

import { ABAS, ID_PAINEL_ABAS, VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';
// Páginas reais das abas do gerente e da visão regional.
import { PaginaAnotacoes } from '../pages/PaginaAnotacoes.jsx';
import { PaginaDados } from '../pages/PaginaDados.jsx';
import { PaginaFeedback } from '../pages/PaginaFeedback.jsx';
import { PaginaRegional } from '../pages/PaginaRegional.jsx';
import { EstadoVazio } from './EstadoVazio.jsx';

// Importa o CSS deste componente.
import './AreaCentral.css';

/**
 * Componente AreaCentral.
 *
 * Não recebe props: lê do contexto a visão, o colaborador selecionado e a
 * aba ativa. O estado é a única fonte de verdade.
 *
 * Devolve:
 *   - visão regional: a página da loja (PaginaRegional);
 *   - visão do gerente sem seleção: EstadoVazio pedindo para escolher alguém;
 *   - visão do gerente com seleção: a página da aba escolhida (Dados,
 *     Anotações ou Feedback).
 *
 * As duas raízes são <main>: a área central é o conteúdo principal da
 * página, e cabeçalho e barra lateral ficam fora dela.
 *
 * Exemplo de uso: <AreaCentral />
 */
export function AreaCentral() {
  const { estado } = useApp();

  // Atalhos para os três pedaços do estado usados aqui.
  const { visao, vendedorSelecionadoId, aba } = estado;

  // A regional não escolhe colaborador: tem uma visão própria da loja.
  if (visao === VISOES.REGIONAL) {
    return (
      <main className="area-central" aria-label="Visão regional">
        <PaginaRegional />
      </main>
    );
  }

  return (
    <main className="area-central" aria-label="Conteúdo do colaborador">
      {!vendedorSelecionadoId ? (
        // Gerente sem ninguém escolhido: explica o próximo passo.
        <EstadoVazio
          titulo="Escolha um colaborador"
          descricao="Selecione alguém na lista à esquerda para ver as anotações, os dados e o feedback."
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

          {aba === ABAS.ANOTACOES && <PaginaAnotacoes />}

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
