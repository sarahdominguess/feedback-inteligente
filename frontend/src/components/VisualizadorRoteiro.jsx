/**
 * Visualizador do roteiro de feedback gerado pela IA.
 *
 * Mostra as quatro listas de forma organizada para usar durante a conversa.
 * Recebe tudo por props: não usa o contexto, não altera o texto e não valida
 * o conteúdo — só exibe o que a API devolveu.
 */

import {
  MessageSquare,
  Search,
  Target,
  TrendingUp,
} from 'lucide-react';

import { formatarDataHora } from '../utilitarios/formatadores.js';
import { rotuloPeriodo } from '../utilitarios/periodoDoRoteiro.js';

import './VisualizadorRoteiro.css';

/**
 * Configuração das quatro seções: título, ícone, tom e textos de apoio.
 *
 * O método SBI (Situação, Comportamento e Impacto) descreve o que aconteceu,
 * o que a pessoa fez e o efeito disso. O aviso do topo lembra que os pontos
 * de melhoria e o roteiro seguem esse método.
 */
const SECOES = {
  pontos_positivos: {
    titulo: 'Pontos positivos',
    Icone: TrendingUp,
    tom: 'positiva',
  },
  pontos_melhoria: {
    titulo: 'Pontos de melhoria',
    Icone: Target,
    tom: 'atencao',
  },
  possiveis_motivos: {
    titulo: 'Possíveis motivos',
    Icone: Search,
    tom: 'neutra',
    legenda: 'São hipóteses para investigar na conversa, não conclusões.',
  },
  roteiro_conversa: {
    titulo: 'Roteiro de conversa sugerido',
    Icone: MessageSquare,
    tom: 'neutra',
    numerada: true,
  },
};

/**
 * Desenha uma seção do roteiro.
 *
 * Recebe a chave da seção e o objeto com as quatro listas. Devolve a seção
 * com título, ícone, legenda (quando existe) e a lista.
 *
 * A lista do roteiro de conversa é um <ol> (lista numerada semântica): o
 * número não é enfeite, ele indica a ordem da conversa — abertura, perguntas
 * e combinados. As demais são <ul>, porque a ordem não importa.
 */
function renderizarSecao(chave, roteiro) {
  const { titulo, Icone, tom, legenda, numerada } = SECOES[chave];

  /*
   * Não julgamos o conteúdo: só garantimos que exista uma lista para
   * desenhar. Se vier vazia, a seção mostra a mensagem padrão.
   */
  const itens = Array.isArray(roteiro?.[chave]) ? roteiro[chave] : [];

  // Cada texto da IA é um <li> com chave própria (chave + posição).
  const itensJsx = itens.map((item, indice) => (
    <li key={`${chave}-${indice}`}>{item}</li>
  ));

  return (
    <section
      className={`visualizador-roteiro__secao visualizador-roteiro__secao--${tom}`}
    >
      <div className="visualizador-roteiro__cabecalho-secao">
        {/*
         * Ícone decorativo: aria-hidden evita que o leitor de tela repita o
         * que o título ao lado já diz.
         */}
        <span className="visualizador-roteiro__icone" aria-hidden="true">
          <Icone />
        </span>

        <h4 className="visualizador-roteiro__titulo-secao">{titulo}</h4>
      </div>

      {legenda && (
        <p className="visualizador-roteiro__legenda">{legenda}</p>
      )}

      {itens.length === 0 ? (
        <p className="visualizador-roteiro__vazio">
          Nada sugerido nesta seção.
        </p>
      ) : numerada ? (
        <ol className="visualizador-roteiro__lista">{itensJsx}</ol>
      ) : (
        <ul className="visualizador-roteiro__lista">{itensJsx}</ul>
      )}
    </section>
  );
}

/**
 * Componente VisualizadorRoteiro.
 *
 * Props (os dados que o componente recebe de quem o usa):
 *   roteiro: as quatro listas (pontos_positivos, pontos_melhoria,
 *     possiveis_motivos e roteiro_conversa).
 *   vendedorNome: nome de quem recebe o feedback.
 *   mesReferencia: "AAAA-MM" ou null quando foi todo o histórico.
 *   geradoEm: data e hora em texto ISO, como a API manda.
 *
 * Devolve o cabeçalho, a nota do método SBI e as quatro seções em duas
 * colunas a partir de 1024px (uma coluna em telas estreitas).
 *
 * Exemplo:
 *   <VisualizadorRoteiro
 *     roteiro={roteiroDaApi}
 *     vendedorNome="Bianca Rocha"
 *     mesReferencia="2026-10"
 *     geradoEm="2026-11-11T14:30:00"
 *   />
 */
export function VisualizadorRoteiro({
  roteiro,
  vendedorNome,
  mesReferencia,
  geradoEm,
}) {
  return (
    <div className="visualizador-roteiro">
      <header className="visualizador-roteiro__cabecalho">
        {/*
         * h3 porque a página já tem um h2 ("Gerar feedback");
         * as seções internas usam h4. A ordem h2 → h3 → h4 fica coerente.
         */}
        <h3 className="visualizador-roteiro__titulo">
          Roteiro para {vendedorNome}
        </h3>

        <p className="visualizador-roteiro__meta">
          {rotuloPeriodo(mesReferencia)} · Gerado em{' '}
          {formatarDataHora(geradoEm)}
        </p>
      </header>

      {/*
       * Nota fixa e curta. Não promete nada além do método usado na geração:
       * a conversa continua sendo do gerente.
       */}
      <p className="visualizador-roteiro__nota">
        Os pontos de melhoria e o roteiro seguem o método SBI (Situação,
        Comportamento e Impacto). Adapte ao seu jeito: a conversa é sua.
      </p>

      {/*
       * Duas colunas a partir de 1024px: positivos e melhoria à esquerda;
       * possíveis motivos e roteiro à direita. Em telas estreitas, a grade
       * tem uma coluna só e as seções empilham na ordem do JSX.
       */}
      <div className="visualizador-roteiro__grade">
        <div className="visualizador-roteiro__coluna">
          {renderizarSecao('pontos_positivos', roteiro)}
          {renderizarSecao('pontos_melhoria', roteiro)}
        </div>

        <div className="visualizador-roteiro__coluna">
          {renderizarSecao('possiveis_motivos', roteiro)}
          {renderizarSecao('roteiro_conversa', roteiro)}
        </div>
      </div>
    </div>
  );
}
