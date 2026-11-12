/**
 * Funções de apoio da lista de roteiros preparados (aba Feedback).
 *
 * "Roteiro preparado" é um roteiro que a IA já GEROU para a pessoa; não
 * significa que a conversa aconteceu. Aqui ficam só contas e conferências
 * sobre esses itens: título, descrição, se o conteúdo veio completo e como
 * acrescentar um roteiro novo no topo da lista.
 *
 * Função pura: para a mesma entrada devolve sempre a mesma saída, sem React,
 * sem rede e sem alterar o que recebeu.
 */

import { formatarDataHora } from './formatadores.js';
import { rotuloPeriodo } from './periodoDoRoteiro.js';

// Texto usado quando não há valor para mostrar (mesmo símbolo do resto do app).
const TRAVESSAO = '—';

// Texto usado quando o item existe mas não traz a data de geração.
const TEXTO_SEM_DATA = 'Data indisponível';

/**
 * Nomes das quatro listas que formam um roteiro completo.
 *
 * Ficam aqui para as conferências e os testes usarem exatamente os mesmos
 * nomes que a API manda (ver backend/contracts/feedback.py).
 */
const NOMES_DAS_LISTAS = [
  'pontos_positivos',
  'pontos_melhoria',
  'possiveis_motivos',
  'roteiro_conversa',
];

/**
 * Diz se um valor é um objeto "de verdade" (e não null, número ou texto).
 *
 * Recebe qualquer valor e devolve true/false. Serve para as funções abaixo
 * recusarem itens inválidos sem repetir a mesma checagem.
 *
 * Exemplo: ehObjeto({}) → true; ehObjeto(null) → false.
 */
function ehObjeto(valor) {
  return typeof valor === 'object' && valor !== null;
}

/**
 * Título de um roteiro preparado: o período que ele analisou.
 *
 * Recebe o item no formato de feedbacks_preparados e devolve "outubro de
 * 2026" ou "Todo o histórico". Um item que não é objeto devolve "—".
 *
 * Observação: um objeto SEM o campo mes_referencia se comporta como null, e
 * null significa "todo o histórico" — é o que a API quer dizer com isso.
 *
 * Exemplo: tituloDoRoteiroPreparado({ mes_referencia: '2026-10' })
 *          → "outubro de 2026"
 */
export function tituloDoRoteiroPreparado(item) {
  if (!ehObjeto(item)) {
    return TRAVESSAO;
  }

  // rotuloPeriodo já resolve "AAAA-MM" → texto e null → "Todo o histórico".
  return rotuloPeriodo(item.mes_referencia);
}

/**
 * Descrição de um roteiro preparado: quando ele foi gerado.
 *
 * Recebe o item e devolve "Gerado em 11/11/2026 às 14:30". Quando o item não
 * é objeto ou a data não é válida, devolve "Data indisponível" (melhor do que
 * mostrar "null" ou um traço solto).
 *
 * Exemplo: descricaoDoRoteiroPreparado({ gerado_em: '2026-11-11T14:30:00' })
 *          → "Gerado em 11/11/2026 às 14:30"
 */
export function descricaoDoRoteiroPreparado(item) {
  if (!ehObjeto(item)) {
    return TEXTO_SEM_DATA;
  }

  // formatarDataHora devolve "—" quando o texto não é uma data válida.
  const dataHora = formatarDataHora(item.gerado_em);

  if (dataHora === TRAVESSAO) {
    return TEXTO_SEM_DATA;
  }

  return `Gerado em ${dataHora}`;
}

/**
 * Diz se o item traz o conteúdo completo do roteiro.
 *
 * Recebe o item e devolve true SOMENTE quando item.roteiro tem as quatro
 * listas (pontos_positivos, pontos_melhoria, possiveis_motivos,
 * roteiro_conversa) como arrays. Arrays vazios valem: a IA pode não ter
 * sugerido nada numa seção, e isso continua sendo um roteiro completo.
 * Qualquer outra coisa (faltando, null, texto, número) devolve false.
 *
 * Exemplo: roteiroTemConteudo({ roteiro: { pontos_positivos: [], ... } })
 *          → true (quando as quatro chaves são listas)
 */
export function roteiroTemConteudo(item) {
  if (!ehObjeto(item) || !ehObjeto(item.roteiro)) {
    return false;
  }

  // every: só é true se TODAS as chaves passarem na conferência.
  return NOMES_DAS_LISTAS.every((nome) =>
    Array.isArray(item.roteiro[nome]),
  );
}

/**
 * Transforma a resposta do POST de geração num item da lista de preparados.
 *
 * Recebe o corpo devolvido por POST /api/feedback/gerar (feedback_id,
 * mes_referencia, gerado_em e roteiro) e devolve só os quatro campos usados
 * na lista — o mesmo formato de feedbacks_preparados no histórico.
 *
 * Devolve null quando não dá para montar um item confiável: resposta que não
 * é objeto, sem feedback_id ou sem as quatro listas do roteiro.
 *
 * Exemplo: itemPreparadoDeResposta(respostaDoPost) →
 *   { feedback_id: 'abc', mes_referencia: '2026-10',
 *     gerado_em: '2026-11-11T14:30:00Z', roteiro: {...} }
 */
export function itemPreparadoDeResposta(resposta) {
  if (!ehObjeto(resposta)) {
    return null;
  }

  // feedback_id precisa ser texto com algo além de espaços.
  if (
    typeof resposta.feedback_id !== 'string' ||
    resposta.feedback_id.trim() === ''
  ) {
    return null;
  }

  // Sem o conteúdo completo não há o que expandir na tela.
  if (!roteiroTemConteudo(resposta)) {
    return null;
  }

  return {
    feedback_id: resposta.feedback_id,
    // ?? null normaliza "campo ausente" para o mesmo valor que a API usa
    // quando o roteiro considerou todo o histórico.
    mes_referencia: resposta.mes_referencia ?? null,
    gerado_em: resposta.gerado_em,
    roteiro: resposta.roteiro,
  };
}

/**
 * Põe um item no INÍCIO da lista, sem repetir o mesmo roteiro.
 *
 * Recebe a lista atual e o item novo. Devolve uma lista NOVA (a original fica
 * intacta): com o item na primeira posição e, se já existir um item com o
 * mesmo feedback_id, ele é substituído em vez de aparecer duas vezes.
 *
 * Casos de borda: lista inválida → lista só com o item; item inválido (null
 * ou não objeto) → cópia da lista como veio.
 *
 * Exemplo: incluirNoInicio([{ feedback_id: 'a' }], { feedback_id: 'b' })
 *          → [{ feedback_id: 'b' }, { feedback_id: 'a' }]
 */
export function incluirNoInicio(lista, item) {
  // Lista inválida conta como vazia; o resultado é sempre um array novo.
  const base = Array.isArray(lista) ? lista : [];

  // Item inválido não entra: devolvemos só uma cópia da lista.
  if (!ehObjeto(item)) {
    return [...base];
  }

  const id = item.feedback_id;

  /*
   * Remove da lista qualquer item com o MESMO feedback_id. Quando o item novo
   * não tem id (texto), não há como comparar: nada é removido.
   */
  const semRepetido = base.filter(
    (existente) =>
      !(typeof id === 'string' && existente?.feedback_id === id),
  );

  return [item, ...semRepetido];
}
