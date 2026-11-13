/**
 * Componente CartaoIndicador: um cartão que mostra uma métrica.
 *
 * Recebe o valor JÁ formatado (ex.: "R$ 150,20") e, opcionalmente, a
 * situação em relação ao time, que vira um Selo com o tom correspondente.
 * Não calcula, não formata e não chama a API.
 */

// Traduz a situação técnica ("acima") para o texto que aparece no selo.
import { rotuloSituacaoMetrica } from '../utilitarios/formatadores.js';
// Converte a situação em tom visual (positivo, atencao, neutro...).
import { tomDaSituacao } from '../utilitarios/tomDaSituacao.js';
// Selo reutilizável que mostra a situação.
import { Selo } from './Selo.jsx';

// Importa o CSS deste componente.
import './CartaoIndicador.css';

/**
 * Componente CartaoIndicador.
 *
 * Um componente é uma função do React que devolve um pedaço da tela.
 * As props (dados recebidos de quem usa) são:
 *   rotulo: nome da métrica (ex.: "Ticket médio").
 *   valorFormatado: texto já pronto para exibir (ex.: "R$ 150,20").
 *   detalhe: linha pequena opcional (ex.: "Média do time: R$ 210,00").
 *   situacao: opcional; "acima", "abaixo", "na_media" ou "indisponivel".
 *
 * Devolve um <div> com rótulo, valor, detalhe e (quando há situação) um
 * Selo com o texto e o tom certos. Usamos <div> (e não <article>) porque o
 * cartão não tem título próprio e não precisa virar um marco de conteúdo
 * sem nome para leitores de tela.
 *
 * O tom de "abaixo" é "atencao", e não "negativo", porque ficar abaixo da
 * média do time é um ponto de desenvolvimento para a conversa, não uma
 * falha. Essa regra mora em utilitarios/tomDaSituacao.js.
 *
 * Exemplo: <CartaoIndicador rotulo="Ticket médio" valorFormatado="R$ 150,20" detalhe="Média do time: R$ 210,00" situacao="abaixo" />
 */
export function CartaoIndicador({
  rotulo,
  valorFormatado,
  detalhe,
  situacao,
}) {
  // O selo só aparece quando a situação foi informada.
  const temSituacao = typeof situacao === 'string' && situacao !== '';

  /*
   * Tom do cartão: a barra da esquerda acompanha a situação (verde quando vai
   * bem, roxo nos pontos de atenção). Sem situação, fica verde — é o estado
   * neutro do novo visual.
   */
  const tom = temSituacao ? tomDaSituacao(situacao) : 'sem-situacao';

  return (
    /*
     * <div> em vez de <article>: um <article> sem título vira um marco sem
     * nome para leitores de tela. O cartão é só um bloco visual.
     */
    <div className={`cartao-indicador cartao-indicador--${tom}`}>
      {/* Nome da métrica, em texto menor. */}
      <p className="cartao-indicador__rotulo">{rotulo}</p>

      {/* Valor principal: já vem formatado de quem usa o componente. */}
      <p className="cartao-indicador__valor">{valorFormatado}</p>

      {/* Detalhe opcional, como a média do time ou o mês analisado. */}
      {detalhe && <p className="cartao-indicador__detalhe">{detalhe}</p>}

      {/* Situação: texto vindo dos formatadores + tom vindo da função pura. */}
      {temSituacao && (
        <div className="cartao-indicador__situacao">
          <Selo
            texto={rotuloSituacaoMetrica(situacao)}
            tom={tomDaSituacao(situacao)}
          />
        </div>
      )}
    </div>
  );
}
