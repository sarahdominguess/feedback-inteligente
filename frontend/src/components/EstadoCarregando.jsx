/**
 * Componente que mostra o estado de carregamento.
 *
 * Um "esqueleto" cinza animado ocupa o lugar do conteúdo enquanto os dados
 * vêm da API; o texto do título é lido por leitores de tela.
 */

// Importa o CSS deste componente: o Vite aplica o estilo quando ele é usado.
import './EstadoCarregando.css';

/**
 * Monta os índices usados para repetir as linhas do esqueleto.
 *
 * Recebe a quantidade pedida e devolve uma lista de 0 até quantidade - 1.
 * Se o valor não for um inteiro positivo, usa 3 (o padrão do componente).
 *
 * Exemplo: criarLinhas(2) → [0, 1]
 */
function criarLinhas(quantidade) {
  const total =
    Number.isInteger(quantidade) && quantidade > 0 ? quantidade : 3;

  // Array.from com { length } cria uma lista do tamanho pedido; o segundo
  // argumento diz o que colocar em cada posição (aqui, o próprio índice).
  return Array.from({ length: total }, (_, indice) => indice);
}

/**
 * Componente de carregamento.
 *
 * Um componente é uma função do React que devolve um pedaço da tela.
 * As props são os dados que ele recebe de quem o usa:
 *   titulo: texto principal (padrão "Carregando…").
 *   descricao: frase opcional abaixo do título.
 *   linhas: quantos blocos de esqueleto desenhar (padrão 3).
 *   variante: "texto" (compacto) ou "cartao" (com borda); outro valor usa texto.
 *
 * Devolve um bloco com role="status" (papel avisado ao leitor de tela),
 * aria-live="polite" (avisa quando o texto muda, sem interromper a leitura)
 * e aria-busy="true" (indica que o conteúdo ainda está sendo carregado).
 *
 * Exemplo: <EstadoCarregando linhas={4} variante="cartao" />
 */
export function EstadoCarregando({
  titulo = 'Carregando…',
  descricao,
  linhas = 3,
  variante = 'texto',
}) {
  // Só existem duas variantes; qualquer outro texto cai na versão "texto".
  const classeVariante =
    variante === 'cartao'
      ? 'estado-carregando--cartao'
      : 'estado-carregando--texto';

  // Lista de índices que vira a lista de blocos cinza.
  const indices = criarLinhas(linhas);

  return (
    <div
      className={`estado-carregando ${classeVariante}`}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      {/*
       * Esqueleto (skeleton): um esboço cinza que aparece no lugar do
       * conteúdo enquanto ele carrega. aria-hidden="true" esconde esses
       * blocos decorativos do leitor de tela; o texto abaixo é o que importa.
       */}
      <div className="estado-carregando__esqueleto" aria-hidden="true">
        {indices.map((indice) => (
          <span key={indice} className="estado-carregando__linha" />
        ))}
      </div>

      {/* Texto visível e também anunciado pela região role="status". */}
      <p className="estado-carregando__titulo">{titulo}</p>

      {/* A descrição é opcional: só entra na tela quando foi informada. */}
      {descricao && (
        <p className="estado-carregando__descricao">{descricao}</p>
      )}
    </div>
  );
}
