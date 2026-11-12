/**
 * Cabeçalho fixo do app.
 *
 * Em toda a largura: à esquerda a identidade do produto (título e subtítulo)
 * e, à direita, o menu de usuário (Diego/Patrícia), que também é quem troca a
 * visão do app. Em telas estreitas o conteúdo quebra em duas linhas.
 */

import { MenuUsuario } from './MenuUsuario.jsx';

// Importa o CSS deste componente.
import './Cabecalho.css';

/**
 * Componente Cabecalho.
 *
 * Não recebe props e não usa o contexto: a identidade é fixa e quem cuida de
 * mostrar o usuário e trocar a visão é o MenuUsuario.
 *
 * O título é o único h1 da página e o subtítulo é fixo (não muda com a
 * visão). A área do usuário fica à direita, num bloco próprio.
 *
 * Exemplo de uso: <Cabecalho />
 */
export function Cabecalho() {
  return (
    <header className="cabecalho">
      {/* Identidade do produto: título e subtítulo, à esquerda. */}
      <div className="cabecalho__identidade">
        <h1 className="cabecalho__titulo">Feedback Inteligente</h1>
        <p className="cabecalho__subtitulo">
          Assistente de IA para feedback
        </p>
      </div>

      {/*
       * Área do usuário, à direita: mostra quem está usando o sistema e
       * permite trocar entre os dois perfis (Diego/Patrícia). Escolher um
       * deles troca a visão do app.
       */}
      <div className="cabecalho__area-usuario">
        <MenuUsuario />
      </div>
    </header>
  );
}
