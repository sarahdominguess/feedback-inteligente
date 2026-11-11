/**
 * Componente que mostra o estado "sem dados".
 *
 * Explica por que aquele lugar está vazio (ex.: nenhuma anotação ainda) e
 * aceita um ícone opcional do lucide-react. Recebe tudo por props.
 */

// Importa o CSS deste componente.
import './EstadoVazio.css';

/**
 * Componente de lista vazia.
 *
 * Um componente é uma função do React que devolve um pedaço da tela.
 * As props (dados recebidos de quem usa) são:
 *   titulo: frase curta que resume o vazio.
 *   descricao: explicação simples de por que não há dados.
 *   icone: componente de ícone opcional (ex.: Inbox, do lucide-react).
 *
 * Devolve um bloco centralizado com o ícone (se houver), o título e a
 * descrição. Não usa contexto nem rede.
 *
 * Exemplo: <EstadoVazio titulo="Nenhuma anotação" descricao="Ainda não há anotações para esta pessoa." icone={Inbox} />
 */
export function EstadoVazio({ titulo, descricao, icone }) {
  // Para o React desenhar um componente que veio por prop, o nome precisa
  // começar com letra MAIÚSCULA. Por isso copiamos o valor para "Icone".
  const Icone = icone;

  return (
    <div className="estado-vazio">
      {/*
       * Ícone decorativo e opcional: aria-hidden="true" evita que o leitor
       * de tela o anuncie, porque o texto já explica o vazio.
       */}
      {Icone && (
        <span className="estado-vazio__icone" aria-hidden="true">
          <Icone />
        </span>
      )}

      {/* Título curto: diz o que está vazio. */}
      <p className="estado-vazio__titulo">{titulo}</p>

      {/* Descrição opcional: diz por que está vazio e o que fazer. */}
      {descricao && (
        <p className="estado-vazio__descricao">{descricao}</p>
      )}
    </div>
  );
}
