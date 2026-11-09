/**
 * Tela inicial do FullStore Feedback Inteligente.
 *
 * Este arquivo define o componente App, a raiz visual do frontend. Por enquanto
 * ele só mostra o título e o subtítulo do produto; as telas reais entram nas
 * próximas etapas.
 */

// Importa o CSS deste componente (o Vite aplica esse estilo na página).
import './App.css'

/**
 * Componente React: uma função que devolve a estrutura visual da tela.
 *
 * React é uma biblioteca JavaScript para montar interfaces em pedaços
 * chamados "componentes". JSX é a sintaxe parecida com HTML usada dentro do
 * JavaScript para descrever o que aparece na tela.
 */
function App() {
  // Tudo o que está dentro do return é o que aparece na tela.
  // <main> é a tag que indica o conteúdo principal da página.
  return (
    <main className="app">
      {/* className é o jeito do JSX de escrever o atributo class do HTML. */}
      <h1>Feedback Inteligente</h1>
      <p>Co-piloto de feedback para a liderança da Rede Aurora</p>
    </main>
  )
}

// export default permite que outro arquivo (main.jsx) importe este componente.
export default App
