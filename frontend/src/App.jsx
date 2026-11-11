/**
 * Componente principal do frontend.
 *
 * Por enquanto ele só mostra o painel TEMPORÁRIO de verificação da API, que
 * existe para conferir no navegador que o contexto e os serviços funcionam.
 * Na Etapa 5 este arquivo passa a escolher entre a visão do gerente e a visão
 * da regional.
 */

// Importa o CSS deste componente (o Vite aplica esse estilo na página).
import './App.css';
// Painel temporário que lê o estado e chama as ações do contexto.
import { PainelVerificacao } from './components/PainelVerificacao.jsx';

/**
 * Componente raiz: devolve o conteúdo principal da página.
 *
 * React é uma biblioteca JavaScript para montar interfaces em pedaços
 * chamados "componentes"; cada componente é uma função que devolve a
 * estrutura visual (JSX). O estado compartilhado vem do AppProvider, que
 * envolve este componente no main.jsx.
 */
function App() {
  return (
    <main className="app">
      <PainelVerificacao />
    </main>
  );
}

// export default permite que outro arquivo (main.jsx) importe este componente.
export default App;
