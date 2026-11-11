/**
 * Ponto de entrada do frontend.
 *
 * Este arquivo é executado pelo Vite quando a página abre no navegador. Ele
 * encontra a div com id "root" no index.html e coloca o componente App dentro
 * dela, iniciando a interface React.
 */

// StrictMode: modo de desenvolvimento do React que avisa no console sobre
// problemas no código. Não aparece na tela e não muda o visual.
import { StrictMode } from 'react'
// createRoot: função do React que cria a "raiz" da interface dentro de um
// elemento do HTML.
import { createRoot } from 'react-dom/client'
// Estilos globais da aplicação (reset e fonte padrão).
import './index.css'
// Componente principal da interface, definido em App.jsx.
import App from './App.jsx'
// AppProvider: componente que guarda o estado global (vendedores, abas,
// feedbacks, visão regional) e entrega as ações para as telas via contexto.
import { AppProvider } from './context/AppProvider.jsx'

// getElementById("root") busca a div vazia declarada no index.html; dentro
// dela o React desenha a aplicação. Por que existe este arquivo: o navegador
// carrega apenas o index.html, e o main.jsx é quem inicia o React.
//
// O AppProvider envolve o App para que qualquer tela (mesmo as que ainda
// serão criadas) possa ler o estado e chamar as ações com o hook useApp().
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppProvider>
      <App />
    </AppProvider>
  </StrictMode>,
)
