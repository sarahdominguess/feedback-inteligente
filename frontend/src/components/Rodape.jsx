/**
 * Rodapé do app, com os créditos da autora do projeto.
 *
 * Mostra "Desenvolvido por Sarah Domingues" e o link do Instagram. O nome e o
 * usuário vêm de constantes.js para não ficarem escritos à mão em dois
 * lugares. Não usa contexto nem rede: é só apresentação.
 */

import { AUTORA_INSTAGRAM, AUTORA_NOME } from '../constantes.js';

// Importa o CSS deste componente.
import './Rodape.css';

/**
 * Endereço completo do perfil no Instagram.
 *
 * Montado a partir da constante (que guarda só o nome de usuário, sem "@").
 * A barra no fim é o formato que o Instagram usa nos links de perfil.
 */
const URL_INSTAGRAM = `https://www.instagram.com/${AUTORA_INSTAGRAM}/`;

/**
 * Componente Rodape.
 *
 * Não recebe props: lê os créditos das constantes do projeto.
 *
 * Devolve um <footer> com o texto de crédito e o link do Instagram, um ao
 * lado do outro em telas largas e um embaixo do outro (centralizados) no
 * celular.
 *
 * Exemplo de uso: <Rodape />
 */
export function Rodape() {
  return (
    <footer className="rodape">
      {/* Texto de crédito simples. */}
      <p className="rodape__texto">Desenvolvido por {AUTORA_NOME}</p>

      {/*
       * Link para o Instagram.
       *
       * target="_blank" abre o perfil em uma ABA NOVA, sem sair do app.
       * rel="noopener noreferrer" é a proteção recomendada nesse caso:
       * - noopener impede que a página aberta mexa na nossa janela (via
       *   window.opener), o que seria um risco de segurança;
       * - noreferrer evita enviar a informação de qual página trouxe o
       *   visitante.
       *
       * aria-label: o texto visível é só "@sarahdev.css", que não diz de quem
       * é nem que abre outra aba. O rótulo falado completa essa informação
       * para quem usa leitor de tela.
       */}
      <a
        className="rodape__link"
        href={URL_INSTAGRAM}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Instagram de ${AUTORA_NOME} (abre em nova aba)`}
      >
        @{AUTORA_INSTAGRAM}
      </a>
    </footer>
  );
}
