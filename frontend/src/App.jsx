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
import { VISOES } from './constantes.js';
import { useApp } from './context/useApp.js';

/**
 * Componente App.
 *
 * Não recebe props: é o topo da árvore. Usa o useApp() apenas para saber a
 * visão atual, que decide se a coluna lateral existe.
 *
 * Devolve:
 *   - <Cabecalho /> ocupando a largura toda no topo;
 *   - <div class="app__corpo"> com a barra lateral (só na visão do gerente)
 *     e a área central, que ocupa todo o espaço restante;
 *   - <Rodape /> no fim da tela.
 *
 * Exemplo (feito em main.jsx): <App />
 */
function App() {
  const { estado } = useApp();

  // Na visão do gerente existe a coluna do menu do colaborador; na regional,
  // não — e aí a área central usa a largura inteira.
  const mostrarLateral = estado.visao === VISOES.GERENTE;

  return (
    <div className="app">
      {/* Topo: título, subtítulo e alternador de visão. */}
      <Cabecalho />

      {/* Meio: lateral à esquerda (quando existe) e conteúdo no restante. */}
      <div className="app__corpo">
        {mostrarLateral && <BarraLateral />}

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
