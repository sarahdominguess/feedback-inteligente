/**
 * Formatadores de exibição do frontend.
 *
 * Transformam valores crus da API em texto bonito para a tela (moeda, número,
 * porcentagem, mês, data e rótulos). São funções puras: para a mesma entrada
 * devolvem sempre a mesma saída — sem rede, sem estado e sem calcular métrica.
 */

/**
 * Texto que aparece quando não há valor para mostrar.
 *
 * "Travessão" (—) é o traço horizontal longo, diferente do hífen do teclado
 * (-). A API manda null quando o dado não existe; a tela nunca deve mostrar
 * "null", "NaN" ou "undefined".
 */
const TRAVESSAO = '—';

/**
 * Sinal de menos "tipográfico" (−), maior que o hífen do teclado (-).
 *
 * Usamos o mesmo símbolo no código e nos testes para que a comparação seja
 * exata e o texto fique alinhado com a tipografia do app.
 */
const SINAL_NEGATIVO = '\u2212';

/**
 * Nomes dos meses em português, na ordem do calendário (janeiro = posição 0).
 *
 * Ficam escritos aqui porque o app fala português; assim não dependemos do
 * idioma configurado no navegador nem baixamos nada da internet.
 */
const NOMES_DOS_MESES = [
  'janeiro',
  'fevereiro',
  'março',
  'abril',
  'maio',
  'junho',
  'julho',
  'agosto',
  'setembro',
  'outubro',
  'novembro',
  'dezembro',
];

/**
 * Diz se o valor é um número utilizável na formatação.
 *
 * Recebe qualquer valor e devolve true apenas para números finitos.
 *
 * Por que não basta "typeof valor === 'number'": NaN (do inglês "not a
 * number", ou "não é um número") é um valor numérico inválido que aparece em
 * contas impossíveis, como 0 dividido por 0. Infinity representa o infinito.
 * Nenhum dos dois existe em JSON nem deve aparecer na tela, então
 * Number.isFinite recusa os dois.
 *
 * Exemplo: ehNumero(10) → true; ehNumero(NaN) → false; ehNumero('10') → false.
 */
function ehNumero(valor) {
  return typeof valor === 'number' && Number.isFinite(valor);
}

/**
 * Confere se a quantidade de casas decimais pedida serve para o Intl.
 *
 * Recebe a quantidade recebida e o padrão da função. Devolve um inteiro
 * maior ou igual a zero.
 *
 * Por que existe: o Intl.NumberFormat lança erro se receber número negativo
 * de casas; sem esta proteção, uma chamada errada quebraria a tela inteira.
 *
 * Exemplo: casasSeguras(3, 2) → 3; casasSeguras(-1, 2) → 2.
 */
function casasSeguras(casas, padrao) {
  if (!Number.isInteger(casas) || casas < 0) {
    return padrao;
  }
  return casas;
}

/**
 * Formata um número em português do Brasil com casas decimais fixas.
 *
 * Recebe o valor (número) e quantas casas devem aparecer depois da vírgula.
 * Devolve texto com ponto no milhar e vírgula no decimal (ex.: "1.234,50").
 *
 * Intl.NumberFormat é um recurso do JavaScript que formata números conforme o
 * idioma pedido — "Intl" vem de internacionalização. Com 'pt-BR' ele usa
 * ponto para milhar e vírgula para decimal, como se escreve no Brasil.
 *
 * Exemplo: formatarComCasas(1234.5, 2) → "1.234,50"
 */
function formatarComCasas(valor, casas) {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  }).format(valor);
}

/**
 * Mostra um valor em reais no padrão brasileiro.
 *
 * Recebe o valor em reais (número) ou null/undefined. Devolve texto como
 * "R$ 1.234,50"; quando não há número válido, devolve "—".
 *
 * Observação: o espaço depois de "R$" pode vir como espaço especial (não
 * separável). Na tela ele aparece igual; só os testes precisam normalizá-lo.
 *
 * Exemplo: formatarMoeda(1234.5) → "R$ 1.234,50"
 */
export function formatarMoeda(valor) {
  // Sem número válido não existe valor para mostrar: travessão.
  if (!ehNumero(valor)) {
    return TRAVESSAO;
  }

  // style "currency" + currency "BRL" faz o Intl escrever "R$" e usar as duas
  // casas decimais padrão do real.
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor);
}

/**
 * Mostra um número decimal no padrão brasileiro.
 *
 * Recebe o valor (número) e, opcionalmente, quantas casas decimais mostrar
 * (padrão 2). Devolve texto como "1,20"; sem número válido, devolve "—".
 *
 * Exemplo: formatarNumero(1.2) → "1,20"
 *          formatarNumero(1234.567, 1) → "1.234,6"
 */
export function formatarNumero(valor, casas = 2) {
  if (!ehNumero(valor)) {
    return TRAVESSAO;
  }

  return formatarComCasas(valor, casasSeguras(casas, 2));
}

/**
 * Mostra um número inteiro com separador de milhar.
 *
 * Recebe o valor (número). Devolve texto como "3.250"; sem número válido,
 * devolve "—".
 *
 * Exemplo: formatarInteiro(3250) → "3.250"
 */
export function formatarInteiro(valor) {
  if (!ehNumero(valor)) {
    return TRAVESSAO;
  }

  // Zero casas decimais: contagens (vendas, peças, atendimentos) não têm
  // "meia unidade" para mostrar.
  return formatarComCasas(valor, 0);
}

/**
 * Mostra uma fração como porcentagem.
 *
 * Recebe a fração (número de 0 a 1, em que 0,325 = 32,5%) e, opcionalmente,
 * quantas casas decimais mostrar (padrão 1). Devolve texto como "32,5%";
 * sem número válido, devolve "—".
 *
 * A multiplicação por 100 é só de EXIBIÇÃO: a API manda a taxa como fração
 * de 0 a 1 e a conta serve apenas para escrever o símbolo %. Nenhum
 * indicador é calculado aqui.
 *
 * Exemplo: formatarPercentual(0.325) → "32,5%"
 */
export function formatarPercentual(fracao, casas = 1) {
  if (!ehNumero(fracao)) {
    return TRAVESSAO;
  }

  const digitos = casasSeguras(casas, 1);

  // 0.325 * 100 pode dar 32.500000000000004 por causa do jeito que o
  // computador guarda decimais; o Intl arredonda para as casas pedidas e o
  // texto final sai certo.
  return `${formatarComCasas(fracao * 100, digitos)}%`;
}

/**
 * Mostra a diferença em relação à média do time, com sinal explícito.
 *
 * Recebe o valor como FRAÇÃO. Devolve texto como "+12,3%" (acima da média),
 * "−8,0%" (abaixo) ou "0,0%" (na média); sem número válido, devolve "—".
 *
 * Conferido em backend/contracts/metricas.py: a descrição do campo
 * diferenca_percentual diz "como fração: (valor menos média) dividido pela
 * média; -0,20 significa 20% abaixo". Por isso a multiplicação por 100
 * abaixo é só exibição, igual à de formatarPercentual.
 *
 * Exemplo: formatarDiferencaPercentual(0.123) → "+12,3%"
 */
export function formatarDiferencaPercentual(valor) {
  if (!ehNumero(valor)) {
    return TRAVESSAO;
  }

  // Math.abs tira o sinal porque o sinal é escrito à parte, com o símbolo
  // escolhido aqui. Math.abs(-0.08) → 0.08.
  const numero = formatarComCasas(Math.abs(valor) * 100, 1);

  if (valor > 0) {
    return `+${numero}%`;
  }

  if (valor < 0) {
    return `${SINAL_NEGATIVO}${numero}%`;
  }

  // Zero não é "melhor" nem "pior" que a média: fica sem sinal.
  return `${numero}%`;
}

/**
 * Mostra um mês no formato "AAAA-MM" por extenso.
 *
 * Recebe um texto como "2026-10". Devolve "outubro de 2026"; quando o texto
 * não é um mês válido, devolve "—".
 *
 * Exemplo: formatarMes('2026-10') → "outubro de 2026"
 */
export function formatarMes(mesAAAAMM) {
  if (typeof mesAAAAMM !== 'string') {
    return TRAVESSAO;
  }

  // ^\d{4} = quatro dígitos; (0[1-9]|1[0-2]) = mês de 01 a 12; $ = só isso,
  // sem nada antes ou depois.
  const partes = /^(\d{4})-(0[1-9]|1[0-2])$/.exec(mesAAAAMM.trim());

  if (partes === null) {
    return TRAVESSAO;
  }

  // "10" vira a posição 9 da lista de meses (janeiro é a posição 0).
  const numeroDoMes = Number(partes[2]);

  return `${NOMES_DOS_MESES[numeroDoMes - 1]} de ${partes[1]}`;
}

/**
 * Confere se o dia existe de verdade naquele mês (ex.: 30 de fevereiro não).
 *
 * Recebe ano, mês (de 1 a 12) e dia como números. Devolve true ou false.
 *
 * Usamos Date.UTC (data no fuso universal, sem horário local) só para deixar
 * o JavaScript validar o calendário. Depois comparamos as partes: se o dia
 * não existir, o Date "escorrega" para o mês seguinte (30/02 vira 02/03) e a
 * comparação falha. O fuso do computador nunca entra na conta.
 */
function dataExiste(ano, mes, dia) {
  const data = new Date(Date.UTC(ano, mes - 1, dia));

  return (
    data.getUTCFullYear() === ano &&
    data.getUTCMonth() === mes - 1 &&
    data.getUTCDate() === dia
  );
}

/**
 * Mostra uma data no formato "AAAA-MM-DD" como "DD/MM/AAAA".
 *
 * Recebe o texto da data. Aceita também data com hora ISO e usa só a data.
 * Devolve "10/10/2026"; texto inválido ou dia que não existe devolve "—".
 *
 * Por que NÃO usamos new Date("2026-10-10") direto: o JavaScript lê essa
 * forma como meia-noite no fuso universal (UTC). No Brasil (três horas atrás
 * do UTC) isso ainda é o dia anterior, e a tela mostraria 09/10/2026.
 * Montando a data a partir das partes do texto, nada muda de dia.
 *
 * Exemplo: formatarData('2026-10-10') → "10/10/2026"
 */
export function formatarData(valor) {
  if (typeof valor !== 'string') {
    return TRAVESSAO;
  }

  // ^\d{4} = quatro dígitos; \d{2} = dois dígitos. O fim aceita o término do
  // texto ou o "T"/espaço que separa a hora em uma data ISO.
  const partes = /^(\d{4})-(\d{2})-(\d{2})(?:$|[T ])/.exec(valor.trim());

  if (partes === null) {
    return TRAVESSAO;
  }

  const ano = Number(partes[1]);
  const mes = Number(partes[2]);
  const dia = Number(partes[3]);

  if (!dataExiste(ano, mes, dia)) {
    return TRAVESSAO;
  }

  // Devolvemos os próprios pedaços de texto: "01" continua "01".
  return `${partes[3]}/${partes[2]}/${partes[1]}`;
}

/**
 * Mostra data e hora ISO como "DD/MM/AAAA às HH:MM".
 *
 * Recebe um texto ISO como "2026-11-11T14:30:00". Aceita também segundos,
 * frações de segundo e fuso no fim. Devolve "11/11/2026 às 14:30"; texto
 * inválido devolve "—".
 *
 * Importante: NÃO convertemos o horário para o fuso do computador. O backend
 * manda a data e a hora em UTC; converter poderia trocar o dia sem ninguém
 * perceber. Os números exibidos são exatamente os que vieram no texto.
 *
 * Exemplo: formatarDataHora('2026-11-11T14:30:00') → "11/11/2026 às 14:30"
 */
export function formatarDataHora(valor) {
  if (typeof valor !== 'string') {
    return TRAVESSAO;
  }

  // Grupos: ano, mês, dia, hora e minuto. As partes seguintes são opcionais e
  // cobrem segundos, frações de segundo e o fuso ("Z" ou "-03:00").
  const molde =
    /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?$/;

  const partes = molde.exec(valor.trim());

  if (partes === null) {
    return TRAVESSAO;
  }

  const ano = Number(partes[1]);
  const mes = Number(partes[2]);
  const dia = Number(partes[3]);
  const hora = Number(partes[4]);
  const minuto = Number(partes[5]);

  // Data inexistente ou hora/minuto fora da faixa não viram texto bonito.
  if (!dataExiste(ano, mes, dia) || hora > 23 || minuto > 59) {
    return TRAVESSAO;
  }

  // Mantemos os dois dígitos como vieram: 07:05 continua "07:05".
  return `${partes[3]}/${partes[2]}/${partes[1]} às ${partes[4]}:${partes[5]}`;
}

/**
 * Traduz um nome técnico usando um mapa, com as mesmas regras para todos.
 *
 * Recebe o texto vindo da API e um objeto de traduções. Devolve o rótulo
 * conhecido; quando o texto é desconhecido, devolve o próprio texto (melhor
 * mostrar o que a API mandou do que esconder o dado); sem texto útil, "—".
 *
 * Object.hasOwn confere se a chave é realmente nossa. Sem isso, um nome como
 * "constructor" encontraria uma função herdada do próprio JavaScript em vez
 * de cair no caso "desconhecido".
 */
function traduzirRotulo(nome, rotulos) {
  if (typeof nome !== 'string') {
    return TRAVESSAO;
  }

  const texto = nome.trim();

  if (texto === '') {
    return TRAVESSAO;
  }

  return Object.hasOwn(rotulos, texto) ? rotulos[texto] : texto;
}

/**
 * Rótulos das métricas comparadas, indexados pelo nome técnico da API.
 */
const ROTULOS_METRICAS = {
  ticket_medio: 'Ticket médio',
  pecas_por_atendimento: 'Peças por atendimento (P.A.)',
  conversao: 'Taxa de conversão',
};

/**
 * Traduz o nome técnico de uma métrica para um rótulo de tela.
 *
 * Recebe o nome técnico (ex.: "ticket_medio"). Devolve o rótulo em português;
 * nome desconhecido volta como veio; valor inválido vira "—".
 *
 * Exemplo: rotuloMetrica('ticket_medio') → "Ticket médio"
 */
export function rotuloMetrica(nome) {
  return traduzirRotulo(nome, ROTULOS_METRICAS);
}

/**
 * Rótulos da situação de uma métrica em relação à média do time.
 */
const ROTULOS_SITUACAO_METRICA = {
  acima: 'Acima da média do time',
  abaixo: 'Abaixo da média do time',
  na_media: 'Na média do time',
  indisponivel: 'Sem dados para comparar',
};

/**
 * Traduz a situação de uma métrica em relação ao time.
 *
 * Recebe a situação vinda da API ("acima", "abaixo", "na_media" ou
 * "indisponivel"). Devolve a frase pronta para a tela; situação desconhecida
 * volta como veio; valor inválido vira "—".
 *
 * Exemplo: rotuloSituacaoMetrica('abaixo') → "Abaixo da média do time"
 */
export function rotuloSituacaoMetrica(situacao) {
  return traduzirRotulo(situacao, ROTULOS_SITUACAO_METRICA);
}

/**
 * Rótulos da situação de acompanhamento de feedback de um vendedor.
 */
const ROTULOS_SITUACAO_ACOMPANHAMENTO = {
  com_roteiro: 'Roteiro preparado',
  sem_roteiro: 'Sem roteiro',
};

/**
 * Traduz a situação de acompanhamento de um vendedor.
 *
 * Recebe "com_roteiro" ou "sem_roteiro". Devolve "Roteiro preparado" ou
 * "Sem roteiro"; situação desconhecida volta como veio; valor inválido vira
 * "—".
 *
 * Lembrete de vocabulário: "preparado" quer dizer que o roteiro foi GERADO;
 * não significa que a conversa chegou a acontecer.
 *
 * Exemplo: rotuloSituacaoAcompanhamento('sem_roteiro') → "Sem roteiro"
 */
export function rotuloSituacaoAcompanhamento(situacao) {
  return traduzirRotulo(situacao, ROTULOS_SITUACAO_ACOMPANHAMENTO);
}
