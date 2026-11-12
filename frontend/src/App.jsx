/**
 * Componente principal do frontend.
 *
 * Monta a casca do app em três faixas: cabeçalho no topo, corpo no meio
 * (barra lateral + área central) e rodapé no fim. A visão e a aba vêm do
 * estado do contexto; não há router.
 */

// Importa o CSS deste componente (o Vite aplica esse estilo na página).
import './App.css';

import { AreaCentral } from './components/AreaCentral.jsx';
import { BarraLateral } from './components/BarraLateral.jsx';
import { Cabecalho } from './components/Cabecalho.jsx';
import { Rodape } from './components/Rodape.jsx';

/**
 * Componente App.
 *
 * Não recebe props: é o topo da árvore. Não lê o contexto: a barra lateral
 * existe nas DUAS visões e é ela quem decide o conteúdo (colaborador ou
 * loja).
 *
 * Devolve:
 *   - <Cabecalho /> ocupando a largura toda no topo;
 *   - <div class="app__corpo"> com a barra lateral e a área central, que
 *     ocupa todo o espaço restante;
 *   - <Rodape /> no fim da tela.
 *
 * Exemplo (feito em main.jsx): <App />
 */
function App() {
  return (
    <div className="app">
      {/* Topo: título, subtítulo e menu de usuário. */}
      <Cabecalho />

      {/* Meio: lateral à esquerda e conteúdo no restante. */}
      <div className="app__corpo">
        <BarraLateral />

        {/* Área central: mostra a página conforme visão, seleção e aba. */}
        <AreaCentral />
      </div>

      {/* Fim da página: créditos da autora. */}
      <Rodape />
    </div>
  );
}

// export default permite que outro arquivo (main.jsx) importe este componente.
export default App;
