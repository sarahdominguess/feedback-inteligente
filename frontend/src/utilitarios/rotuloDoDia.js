/**
 * Rótulo do dia usado nos separadores do chat de anotações.
 *
 * Função pura: recebe a data da anotação E a data de "hoje" por parâmetro.
 * Nada de olhar o relógio do computador aqui dentro — assim o resultado é
 * sempre o mesmo para a mesma entrada e os testes conseguem fixar o dia.
 */

import { formatarData } from './formatadores.js';

// Texto usado quando não há valor para mostrar (mesmo símbolo do resto do app).
const TRAVESSAO = '—';

/**
 * Transforma o texto "AAAA-MM-DD" em ano, mês e dia (números).
 *
 * Recebe o texto da data. Devolve { ano, mes, dia } quando a data existe de
 * verdade, ou null quando o texto não está no formato ou o dia não existe
 * (ex.: 30 de fevereiro).
 *
 * Por que não usamos new Date("2026-10-10") direto: o JavaScript lê essa
 * forma como meia-noite no fuso universal (UTC). No Brasil, três horas atrás,
 * isso ainda é o dia anterior — a data mudaria de dia sozinha ("problema de
 * fuso horário"). Aqui montamos a data a partir das PARTES do texto e só
 * lemos os valores em UTC, então o fuso do computador nunca entra na conta.
 */
function desmontarData(texto) {
  if (typeof texto !== 'string') {
    return null;
  }

  // ^\d{4} = quatro dígitos; \d{2} = dois dígitos; $ = nada antes nem depois.
  const partes = /^(\d{4})-(\d{2})-(\d{2})$/.exec(texto.trim());

  if (partes === null) {
    return null;
  }

  const ano = Number(partes[1]);
  const mes = Number(partes[2]);
  const dia = Number(partes[3]);

  /*
   * Date.UTC cria a data no fuso universal. Se o dia não existir no mês
   * (30/02, por exemplo), o JavaScript "escorrega" para o mês seguinte;
   * comparando as partes de volta, descobrimos isso e recusamos.
   */
  const data = new Date(Date.UTC(ano, mes - 1, dia));

  if (
    data.getUTCFullYear() !== ano ||
    data.getUTCMonth() !== mes - 1 ||
    data.getUTCDate() !== dia
  ) {
    return null;
  }

  return { ano, mes, dia };
}

/**
 * Devolve o dia anterior a uma data.
 *
 * Recebe { ano, mes, dia } e devolve o mesmo formato. A conta é feita pelo
 * próprio Date: "dia - 1" com dia 1 vira o último dia do mês anterior, e em
 * 1º de janeiro vira 31 de dezembro do ano anterior. Assim não precisamos
 * saber quantos dias tem cada mês.
 *
 * Exemplo: diaAnterior({ ano: 2026, mes: 11, dia: 1 })
 *          → { ano: 2026, mes: 10, dia: 31 }
 */
function diaAnterior(data) {
  const anterior = new Date(Date.UTC(data.ano, data.mes - 1, data.dia - 1));

  return {
    ano: anterior.getUTCFullYear(),
    mes: anterior.getUTCMonth() + 1,
    dia: anterior.getUTCDate(),
  };
}

/**
 * Diz se duas datas desmontadas são o mesmo dia.
 *
 * Recebe dois objetos { ano, mes, dia } e devolve true/false.
 */
function mesmoDia(a, b) {
  return a.ano === b.ano && a.mes === b.mes && a.dia === b.dia;
}

/**
 * Monta o rótulo do separador de dia do chat.
 *
 * Recebe:
 *   dataTexto: a data da anotação, em "AAAA-MM-DD".
 *   hojeTexto: a data de hoje, também em "AAAA-MM-DD" (quem chama decide
 *     qual é o "hoje"; a função não olha o relógio).
 *
 * Devolve "Hoje" quando é o mesmo dia, "Ontem" quando é o dia anterior e a
 * data no formato brasileiro ("08/10/2026") nos demais casos. Texto inválido
 * (ou dia que não existe) devolve "—".
 *
 * Exemplo: rotuloDoDia('2026-10-08', '2026-10-08') → 'Hoje'
 *          rotuloDoDia('2026-10-07', '2026-10-08') → 'Ontem'
 *          rotuloDoDia('2026-08-06', '2026-10-08') → '06/08/2026'
 */
export function rotuloDoDia(dataTexto, hojeTexto) {
  const dia = desmontarData(dataTexto);
  const hoje = desmontarData(hojeTexto);

  // Sem as duas datas válidas não há como comparar: mostramos o travessão.
  if (dia === null || hoje === null) {
    return TRAVESSAO;
  }

  if (mesmoDia(dia, hoje)) {
    return 'Hoje';
  }

  if (mesmoDia(dia, diaAnterior(hoje))) {
    return 'Ontem';
  }

  // Demais dias: a data comum, no padrão brasileiro, com a mesma função
  // usada no resto do app (que também devolve "—" se algo estiver errado).
  return formatarData(dataTexto);
}
