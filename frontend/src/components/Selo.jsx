/**
 * Componente Selo: um marcador pequeno com texto curto e um tom.
 *
 * "Badge" é o nome em inglês desse tipo de etiqueta. O tom (neutro,
 * positivo, atenção ou negativo) muda as cores, mas a informação nunca
 * depende só da cor: o próprio texto do selo já diz o que aconteceu.
 */

// Importa o CSS deste componente.
import './Selo.css';

/**
 * Tons que o componente conhece. Qualquer outro valor vira "neutro".
 */
const TONS_VALIDOS = new Set(['neutro', 'positivo', 'atencao', 'negativo']);

/**
 * Componente Selo.
 *
 * Um componente é uma função do React que devolve um pedaço da tela.
 * As props (dados recebidos de quem usa) são:
 *   texto: texto curto do selo (obrigatório).
 *   tom: "neutro" (padrão), "positivo", "atencao" ou "negativo".
 *   icone: componente de ícone opcional (ex.: TrendingUp, do lucide-react).
 *
 * Devolve um <span> com o texto e, se informado, o ícone ao lado.
 *
 * Exemplo: <Selo texto="Acima da média do time" tom="positivo" />
 */
export function Selo({ texto, tom = 'neutro', icone }) {
  // Tom desconhecido não pode gerar uma cor inventada: cai no neutro.
  const tomFinal = TONS_VALIDOS.has(tom) ? tom : 'neutro';

  // O React só desenha um componente que veio por prop se o nome começar
  // com letra MAIÚSCULA; por isso copiamos o valor para "Icone".
  const Icone = icone;

  return (
    <span className={`selo selo--${tomFinal}`}>
      {/*
       * Ícone opcional e decorativo: aria-hidden="true" evita repetição no
       * leitor de tela, porque o texto ao lado já informa a situação.
       */}
      {Icone && (
        <span className="selo__icone" aria-hidden="true">
          <Icone />
        </span>
      )}

      {/* O texto é a informação principal e nunca é omitido. */}
      <span className="selo__texto">{texto}</span>
    </span>
  );
}
