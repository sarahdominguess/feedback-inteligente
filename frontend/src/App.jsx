/**
 * Componente principal do frontend.
 *
 * Monta a casca do app: cabeçalho, barra lateral (só na visão do gerente) e
 * área central. A visão e a aba vêm do estado do contexto; não há router.
 */

// Importa o CSS deste componente (o Vite aplica esse estilo na página).
import './App.css';

import { AreaCentral } from './components/AreaCentral.jsx';
import { BarraLateral } from './components/BarraLateral.jsx';
import { Cabecalho } from './components/Cabecalho.jsx';
import { VISOES } from './constantes.js';
import { useApp } from './context/useApp.js';

/**
 * Componente App.
 *
 * Não recebe props: é o topo da árvore. Usa o useApp() apenas para saber a
 * visão atual, que decide se a coluna lateral existe.
 *
 * Devolve o layout em grade com o cabeçalho ocupando a largura toda e, na
 * visão do gerente, a lateral à esquerda e a área central à direita.
 *
 * Exemplo (feito em main.jsx): <App />
 */
function App() {
  const { estado } = useApp();

  // Na visão do gerente existe a coluna do menu do colaborador; na regional, não.
  const mostrarLateral = estado.visao === VISOES.GERENTE;

  return (
    <div
      className={
        mostrarLateral ? 'app-layout app-layout--com-lateral' : 'app-layout'
      }
    >
      {/* Cabeçalho: título, subtítulo e alternador de visão. */}
      <Cabecalho />

      {/* A lateral só entra no DOM quando faz sentido. */}
      {mostrarLateral && <BarraLateral />}

      {/* Área central: mostra a página conforme visão, seleção e aba. */}
      <AreaCentral />
    </div>
  );
}

// export default permite que outro arquivo (main.jsx) importe este componente.
export default App;
