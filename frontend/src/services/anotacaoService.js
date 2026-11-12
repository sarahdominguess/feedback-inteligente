/**
 * Serviço de anotações do gerente.
 *
 * Cuida da chamada HTTP que grava uma anotação nova sobre um vendedor. Nenhuma
 * regra de negócio mora aqui: o limite de caracteres, a data ("hoje", no
 * servidor) e o nome da pessoa ("sobre") são decididos pelo backend. O
 * frontend só evita mandar um pedido sem sentido (texto vazio).
 */

import { api } from './api.js';
import { ErroApi } from './erroApi.js';

/**
 * Confere se o identificador do vendedor é texto e não está vazio.
 *
 * Recebe o valor recebido. Devolve o texto já sem espaços nas pontas; se for
 * inválido, lança um ErroApi de tipo "validacao" e a API nem é chamada.
 *
 * Exemplo: validarVendedorId(' C0031 ') devolve 'C0031'.
 */
function validarVendedorId(valor) {
  if (typeof valor !== 'string' || valor.trim() === '') {
    throw new ErroApi('Informe o código do vendedor para continuar.', {
      tipo: 'validacao',
    });
  }

  return valor.trim();
}

/**
 * Confere e limpa o texto da anotação.
 *
 * Recebe o que a pessoa digitou. Devolve o texto sem espaços, tabulações e
 * quebras de linha das PONTAS — as quebras de linha do MEIO continuam lá,
 * porque são parte do que foi escrito.
 *
 * Lança ErroApi de tipo "validacao" quando não é texto ou quando fica vazio
 * depois da limpeza.
 *
 * O limite de caracteres NÃO é conferido aqui de propósito: o backend é a
 * autoridade (responde 400 com mensagem clara). Duplicar a regra no frontend
 * só criaria duas verdades que podem divergir.
 *
 * Exemplo: validarTexto('  primeira linha\nsegunda  ') devolve
 * 'primeira linha\nsegunda'.
 */
function validarTexto(valor) {
  if (typeof valor !== 'string') {
    throw new ErroApi('Escreva a anotação como texto.', {
      tipo: 'validacao',
    });
  }

  // trim() só mexe nas pontas: o texto do meio fica exatamente como digitado.
  const textoLimpo = valor.trim();

  if (textoLimpo === '') {
    throw new ErroApi('Escreva alguma coisa antes de salvar a anotação.', {
      tipo: 'validacao',
    });
  }

  return textoLimpo;
}

/**
 * Cria o serviço de anotações usando um cliente HTTP.
 *
 * "Fábrica de serviço" é uma função que devolve funções já ligadas a um
 * cliente. Nos testes passamos um cliente falso (com um adapter simulado,
 * que finge ser a rede); em produção a fábrica é chamada sem argumento e usa
 * o cliente real exportado por api.js.
 *
 * Recebe: cliente (instância do Axios; padrão = cliente real).
 * Devolve: { registrarAnotacao }.
 */
export function criarAnotacaoService(cliente = api) {
  /**
   * Grava uma anotação nova sobre um vendedor.
   *
   * Recebe:
   *   vendedorId: código da pessoa (ex.: "C0031"), obrigatório.
   *   texto: o que o gerente escreveu, obrigatório e não vazio.
   *   signal: opcional; é o "sinal" de um AbortController (um objeto que
   *     permite cancelar a chamada em andamento, por exemplo quando a pessoa
   *     troca de tela antes da resposta chegar).
   *
   * Devolve o corpo da resposta SEM transformar (AnotacaoDTO):
   * { data, sobre, texto, e_do_time }.
   *
   * Exemplo: registrarAnotacao('C0031', 'elogiou o caixa')
   * devolve a anotação já gravada, com a data de hoje do servidor.
   */
  async function registrarAnotacao(vendedorId, texto, { signal } = {}) {
    // 1) Validação local: recusa id/texto inválidos antes de tocar na rede.
    const id = validarVendedorId(vendedorId);
    const textoLimpo = validarTexto(texto);

    // 2) POST no caminho do vendedor. encodeURIComponent protege o caminho:
    // "C/0031" vira "C%2F0031" e não quebra a URL em dois pedaços.
    // O corpo leva SÓ o texto: data e "sobre" são decisão do backend.
    return cliente.post(
      `/api/vendedores/${encodeURIComponent(id)}/anotacoes`,
      { texto: textoLimpo },
      { signal },
    );
  }

  return { registrarAnotacao };
}

// Função já ligada ao cliente HTTP real, pronta para a tela usar.
export const { registrarAnotacao } = criarAnotacaoService();
