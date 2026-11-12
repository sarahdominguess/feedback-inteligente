/**
 * Reducer do estado da aplicação.
 *
 * Reducer: uma função pura que recebe o estado atual e uma ação (um objeto
 * com "tipo" e dados) e devolve o PRÓXIMO estado. Pura significa que ela não
 * altera o estado recebido, não faz chamadas HTTP e não usa datas/aleatórios:
 * o mesmo par (estado, ação) sempre produz o mesmo resultado.
 *
 * Imutabilidade: em vez de mudar o objeto existente, criamos um novo com
 * "espalhamento" ({ ...estado }). O React compara as referências para saber
 * o que mudou na tela.
 *
 * As ações cobrem carregar a lista de vendedores, selecionar alguém, buscar o
 * histórico, gerar feedback, carregar a regional, navegar entre aba/visão e
 * ENVIAR UMA ANOTAÇÃO NOVA (as ações de anotação ficam num bloco próprio,
 * mais abaixo).
 *
 * Este arquivo não usa React de propósito: assim a lógica pode ser testada
 * direto no Node, sem navegador.
 */

import { ABAS, LOJA_PADRAO_ID, STATUS, VISOES } from '../constantes.js';

/**
 * Nomes das ações que o reducer entende. Usar constantes evita erro de
 * digitação em textos que aparecem em vários arquivos.
 */
export const TIPOS = {
  VENDEDORES_CARREGANDO: 'vendedores/carregando',
  VENDEDORES_SUCESSO: 'vendedores/sucesso',
  VENDEDORES_ERRO: 'vendedores/erro',

  SELECIONAR_VENDEDOR: 'vendedor/selecionar',

  DETALHES_CARREGANDO: 'detalhes/carregando',
  DETALHES_SUCESSO: 'detalhes/sucesso',
  DETALHES_ERRO: 'detalhes/erro',

  FEEDBACK_CARREGANDO: 'feedback/carregando',
  FEEDBACK_SUCESSO: 'feedback/sucesso',
  FEEDBACK_ERRO: 'feedback/erro',

  ANOTACAO_ENVIANDO: 'anotacao/enviando',
  ANOTACAO_SUCESSO: 'anotacao/sucesso',
  ANOTACAO_ERRO: 'anotacao/erro',

  REGIONAL_CARREGANDO: 'regional/carregando',
  REGIONAL_SUCESSO: 'regional/sucesso',
  REGIONAL_ERRO: 'regional/erro',

  MUDAR_ABA: 'aba/mudar',
  MUDAR_VISAO: 'visao/mudar',
};

/**
 * Extrai a mensagem de erro em texto.
 *
 * Recebe uma string (já é a mensagem) ou um objeto de erro (Error/ErroApi,
 * que têm "message"). Devolve sempre texto. Regra: o estado guarda só a
 * mensagem, nunca o objeto inteiro com URL, cabeçalhos ou outros detalhes.
 */
function mensagemDeErro(valor) {
  if (typeof valor === 'string' && valor.trim() !== '') {
    return valor;
  }

  if (typeof valor?.message === 'string' && valor.message.trim() !== '') {
    return valor.message;
  }

  return 'Não foi possível concluir a operação.';
}

/**
 * Cria o estado inicial da aplicação.
 *
 * Devolve objetos e arrays NOVOS a cada chamada; assim um teste (ou uma
 * remontagem da tela) nunca compartilha estruturas com outra execução.
 */
export function criarEstadoInicial() {
  return {
    lojaId: LOJA_PADRAO_ID,
    visao: VISOES.GERENTE,
    // O app abre na aba Feedback porque é o fluxo principal do gerente:
    // preparar o roteiro da conversa. Anotações e Dados dão apoio a ele.
    aba: ABAS.FEEDBACK,

    // Lista de vendedores da loja.
    vendedores: { status: STATUS.OCIOSO, dados: [], erro: null },

    // Quem está selecionado na tela do gerente.
    vendedorSelecionadoId: null,

    // Histórico detalhado do vendedor selecionado.
    detalhes: { status: STATUS.OCIOSO, dados: null, erro: null },

    // Roteiros por vendedor: { [vendedor_id]: { status, dados, erro } }.
    feedbacks: {},

    // Situação do envio de uma anotação nova (o formulário da aba Anotações).
    // É um pedaço separado porque descreve um ENVIO em andamento, e não o
    // histórico da pessoa: { status, erro }.
    novaAnotacao: { status: STATUS.OCIOSO, erro: null },

    // Consolidado da visão da regional.
    regional: { status: STATUS.OCIOSO, dados: null, erro: null },
  };
}

/**
 * Verifica se um valor pertence a um objeto de constantes (ABAS, VISOES).
 *
 * Object.values(obj) devolve a lista dos valores; includes diz se o valor
 * está nela. Serve para recusar aba/visão inventada.
 */
function valorPermitido(valor, constantes) {
  return Object.values(constantes).includes(valor);
}

/**
 * Guarda uma falha de DETALHES apenas se ela ainda for do vendedor escolhido.
 *
 * Explicação da "corrida": quando a pessoa clica rápido em dois vendedores,
 * duas requisições ficam em andamento. A resposta da primeira pode chegar
 * DEPOIS da segunda; se fosse aplicada, a tela mostraria dados do vendedor
 * errado. Por isso comparamos o vendedorId da ação com o selecionado agora e
 * ignoramos respostas antigas.
 */
function ehDoVendedorSelecionado(estado, vendedorId) {
  return (
    typeof vendedorId === 'string' &&
    vendedorId === estado.vendedorSelecionadoId
  );
}

/**
 * Atualiza a entrada de um vendedor no mapa de feedbacks, sem tocar nos
 * outros vendedores nem no objeto antigo.
 */
function atualizarFeedback(estado, vendedorId, entrada) {
  if (typeof vendedorId !== 'string' || vendedorId === '') {
    return estado;
  }

  const anterior = estado.feedbacks[vendedorId];
  return {
    ...estado,
    feedbacks: {
      ...estado.feedbacks,
      [vendedorId]: {
        // Campos não informados mantêm o valor anterior; "dados" preserva o
        // roteiro já exibido enquanto uma nova geração está em andamento.
        ...anterior,
        ...entrada,
      },
    },
  };
}

/**
 * Aplica uma ação ao estado, devolvendo o próximo estado.
 *
 * Recebe: estado atual e ação ({ tipo, ...dados }).
 * Devolve: novo estado (ou o mesmo, quando a ação é ignorada/desconhecida).
 */
export function appReducer(estado, acao) {
  switch (acao?.tipo) {
    // ----- Lista de vendedores -------------------------------------------
    case TIPOS.VENDEDORES_CARREGANDO:
      return {
        ...estado,
        vendedores: {
          ...estado.vendedores,
          status: STATUS.CARREGANDO,
          erro: null,
        },
      };

    case TIPOS.VENDEDORES_SUCESSO:
      return {
        ...estado,
        vendedores: {
          status: STATUS.SUCESSO,
          dados: Array.isArray(acao.dados) ? acao.dados : [],
          erro: null,
        },
      };

    case TIPOS.VENDEDORES_ERRO:
      return {
        ...estado,
        vendedores: {
          ...estado.vendedores,
          status: STATUS.ERRO,
          erro: mensagemDeErro(acao.erro),
        },
      };

    // ----- Seleção de vendedor -------------------------------------------
    case TIPOS.SELECIONAR_VENDEDOR:
      // Trocar de pessoa reinicia o histórico (detalhes) para "ocioso".
      // Os feedbacks já gerados continuam guardados: eles são por vendedor
      // e não têm relação com quem está selecionado agora.
      // O envio de anotação também volta ao início: um erro ou um "enviando"
      // da pessoa anterior não pode aparecer na tela da próxima.
      return {
        ...estado,
        vendedorSelecionadoId: acao.vendedorId ?? null,
        detalhes: { status: STATUS.OCIOSO, dados: null, erro: null },
        novaAnotacao: { status: STATUS.OCIOSO, erro: null },
      };

    // ----- Detalhes do vendedor selecionado ------------------------------
    case TIPOS.DETALHES_CARREGANDO:
      // Ignora se o pedido é de outra pessoa (resposta atrasada).
      if (!ehDoVendedorSelecionado(estado, acao.vendedorId)) {
        return estado;
      }
      return {
        ...estado,
        detalhes: {
          ...estado.detalhes,
          status: STATUS.CARREGANDO,
          erro: null,
        },
      };

    case TIPOS.DETALHES_SUCESSO:
      if (!ehDoVendedorSelecionado(estado, acao.vendedorId)) {
        return estado;
      }
      return {
        ...estado,
        detalhes: {
          status: STATUS.SUCESSO,
          dados: acao.dados ?? null,
          erro: null,
        },
      };

    case TIPOS.DETALHES_ERRO:
      if (!ehDoVendedorSelecionado(estado, acao.vendedorId)) {
        return estado;
      }
      return {
        ...estado,
        detalhes: {
          ...estado.detalhes,
          status: STATUS.ERRO,
          erro: mensagemDeErro(acao.erro),
        },
      };

    // ----- Feedback (roteiro) por vendedor -------------------------------
    case TIPOS.FEEDBACK_CARREGANDO:
      return atualizarFeedback(estado, acao.vendedorId, {
        status: STATUS.CARREGANDO,
        erro: null,
      });

    case TIPOS.FEEDBACK_SUCESSO:
      return atualizarFeedback(estado, acao.vendedorId, {
        status: STATUS.SUCESSO,
        dados: acao.dados ?? null,
        erro: null,
      });

    case TIPOS.FEEDBACK_ERRO:
      return atualizarFeedback(estado, acao.vendedorId, {
        status: STATUS.ERRO,
        erro: mensagemDeErro(acao.erro),
      });

    // ----- Anotação nova do gerente (aba Anotações) -----------------------
    case TIPOS.ANOTACAO_ENVIANDO:
      // O envio começou: limpa o erro anterior para a tela não mostrar uma
      // falha velha enquanto a nova tentativa acontece.
      return {
        ...estado,
        novaAnotacao: { status: STATUS.CARREGANDO, erro: null },
      };

    case TIPOS.ANOTACAO_SUCESSO: {
      // Resposta de outra pessoa (a pessoa trocou de colaborador no meio do
      // envio): descartamos, como já fazemos com os detalhes. O texto já foi
      // gravado no servidor e aparece quando aquele histórico for recarregado.
      if (!ehDoVendedorSelecionado(estado, acao.vendedorId)) {
        return estado;
      }

      // Atalhos para o histórico carregado e para a lista de anotações dele.
      const dados = estado.detalhes.dados;
      const anotacoes = Array.isArray(dados?.anotacoes)
        ? dados.anotacoes
        : null;

      /*
       * Decisão: mesmo quando não há onde acrescentar (histórico ainda não
       * carregado ou resposta sem os campos esperados), marcamos SUCESSO.
       * A anotação FOI gravada no servidor; marcar erro seria mentira. Ela
       * aparece na próxima vez que o histórico for carregado.
       */
      const comSucesso = {
        ...estado,
        novaAnotacao: { status: STATUS.SUCESSO, erro: null },
      };

      if (
        anotacoes === null ||
        acao.dados === undefined ||
        acao.dados === null
      ) {
        return comSucesso;
      }

      return {
        ...comSucesso,
        detalhes: {
          ...estado.detalhes,
          dados: {
            ...dados,
            // Lista NOVA (o estado antigo nunca é alterado) e a anotação no
            // FIM, que é a ordem cronológica usada pelo histórico.
            anotacoes: [...anotacoes, acao.dados],
          },
        },
      };
    }

    case TIPOS.ANOTACAO_ERRO:
      // Falha de outra pessoa: a tela já mostra o colaborador novo, então o
      // aviso não teria a ver com ele. Mesma proteção de "resposta antiga".
      if (!ehDoVendedorSelecionado(estado, acao.vendedorId)) {
        return estado;
      }
      return {
        ...estado,
        novaAnotacao: {
          status: STATUS.ERRO,
          // Só o texto da mensagem: nunca URL, cabeçalho ou objeto de erro.
          erro: mensagemDeErro(acao.erro),
        },
      };

    // ----- Visão regional -------------------------------------------------
    case TIPOS.REGIONAL_CARREGANDO:
      return {
        ...estado,
        regional: {
          ...estado.regional,
          status: STATUS.CARREGANDO,
          erro: null,
        },
      };

    case TIPOS.REGIONAL_SUCESSO:
      return {
        ...estado,
        regional: {
          status: STATUS.SUCESSO,
          dados: acao.dados ?? null,
          erro: null,
        },
      };

    case TIPOS.REGIONAL_ERRO:
      return {
        ...estado,
        regional: {
          ...estado.regional,
          status: STATUS.ERRO,
          erro: mensagemDeErro(acao.erro),
        },
      };

    // ----- Navegação ------------------------------------------------------
    case TIPOS.MUDAR_ABA:
      // Valor inválido: devolve o mesmo estado, sem criar objeto novo.
      if (!valorPermitido(acao.aba, ABAS)) {
        return estado;
      }
      return { ...estado, aba: acao.aba };

    case TIPOS.MUDAR_VISAO:
      if (!valorPermitido(acao.visao, VISOES)) {
        return estado;
      }
      return { ...estado, visao: acao.visao };

    // Ação desconhecida: nada muda.
    default:
      return estado;
  }
}
