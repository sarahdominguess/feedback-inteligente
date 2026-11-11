/**
 * Área central do app.
 *
 * Decide o que aparece no centro conforme a visão e a aba escolhidas:
 * aviso da regional, pedido para escolher um colaborador ou o aviso da aba
 * ativa. As páginas reais entram nas próximas fatias.
 */

import { ID_PAINEL_ABAS, ROTULOS_ABAS, VISOES } from '../constantes.js';
import { useApp } from '../context/useApp.js';
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
 *   - visão regional: o aviso "Visão regional em construção";
 *   - visão do gerente sem seleção: EstadoVazio pedindo para escolher alguém;
 *   - visão do gerente com seleção: painel de aba com "Aba ... em construção".
 *
 * É NESTE arquivo que as próximas fatias trocam cada aviso pela página real
 * (Anotacoes, Dados, Feedback e a página da regional).
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
      <section className="area-central" aria-label="Visão regional">
        <div className="area-central__aviso">
          <h2 className="area-central__titulo">
            Visão regional em construção
          </h2>
          <p className="area-central__texto">
            Nas próximas fatias, esta área mostra o consolidado da loja e a
            cobertura dos roteiros preparados.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="area-central" aria-label="Conteúdo do colaborador">
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
          <div className="area-central__aviso">
            <h2 className="area-central__titulo">
              Aba {ROTULOS_ABAS[aba]} em construção
            </h2>
            <p className="area-central__texto">
              Nas próximas fatias, esta aba passa a mostrar a página real do
              colaborador.
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
