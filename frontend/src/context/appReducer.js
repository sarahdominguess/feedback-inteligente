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
 * mais abaixo). Quando a geração dá certo, o roteiro novo entra também no
 * topo da lista de "Roteiros já preparados" do histórico carregado — sem
 * recarregar nada da API.
 *
 * Este arquivo não usa React de propósito: assim a lógica pode ser testada
 * direto no Node, sem navegador.
 */

import { ABAS, LOJA_PADRAO_ID, STATUS, VISOES } from '../constantes.js';
import {
  incluirNoInicio,
  itemPreparadoDeResposta,
} from '../utilitarios/roteirosPreparados.js';

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

  // Visão da regional POR LOJA (Etapa 8).
  LOJAS_CARREGANDO: 'lojas/carregando',
  LOJAS_SUCESSO: 'lojas/sucesso',
  LOJAS_ERRO: 'lojas/erro',

  SELECIONAR_LOJA: 'loja/selecionar',

  DETALHES_LOJA_CARREGANDO: 'detalhes-loja/carregando',
  DETALHES_LOJA_SUCESSO: 'detalhes-loja/sucesso',
  DETALHES_LOJA_ERRO: 'detalhes-loja/erro',

  FEEDBACK_REGIONAL_CARREGANDO: 'feedback-regional/carregando',
  FEEDBACK_REGIONAL_SUCESSO: 'feedback-regional/sucesso',
  FEEDBACK_REGIONAL_ERRO: 'feedback-regional/erro',

  ANOTACAO_REGIONAL_ENVIANDO: 'anotacao-regional/enviando',
  ANOTACAO_REGIONAL_SUCESSO: 'anotacao-regional/sucesso',
  ANOTACAO_REGIONAL_ERRO: 'anotacao-regional/erro',

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

    // ----- Visão da regional POR LOJA (Etapa 8) --------------------------
    // Lista de lojas que a regional pode acompanhar (hoje só a L004).
    lojas: { status: STATUS.OCIOSO, dados: [], erro: null },

    // Qual loja está escolhida no seletor da barra lateral.
    lojaSelecionadaId: null,

    // Histórico da loja escolhida (consolidado + roteiros do gerente).
    detalhesLoja: { status: STATUS.OCIOSO, dados: null, erro: null },

    // Roteiros do gerente por loja: { [loja_id]: { status, dados, erro } }.
    // Fica separado de "feedbacks" (que é por vendedor) para não misturar as
    // duas gerações, que usam registros e prompts diferentes no backend.
    feedbacksRegional: {},

    // Situação do envio de uma anotação nova da regional (aba Anotações).
    novaAnotacaoRegional: { status: STATUS.OCIOSO, erro: null },
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
 * Põe um roteiro recém-gerado no topo da lista de "Roteiros já preparados".
 *
 * Recebe o estado, o código do vendedor e a resposta da geração. Devolve o
 * estado com os detalhes atualizados — ou o MESMO estado quando não é o caso:
 *
 * 1) os detalhes ainda não foram carregados com sucesso (não há lista);
 * 2) os detalhes são de OUTRA pessoa (resposta atrasada de uma troca de
 *    colaborador): mexer neles mostraria o roteiro na pessoa errada;
 * 3) a resposta não permite montar um item válido (sem feedback_id ou sem as
 *    quatro listas).
 *
 * Em todos esses casos nada quebra: o feedback continua guardado em
 * estado.feedbacks[vendedorId], e a lista do histórico espera a próxima
 * carga para aparecer.
 *
 * Por que existe: sem isso, a lista só se atualizaria ao recarregar os dados
 * do colaborador. Como a resposta da geração já traz tudo, dá para atualizar
 * na hora, sem nenhuma chamada HTTP a mais.
 */
function incluirPreparadoNoHistorico(estado, vendedorId, dados) {
  const detalhes = estado.detalhes;

  if (detalhes.status !== STATUS.SUCESSO || !detalhes.dados) {
    return estado;
  }

  if (detalhes.dados.vendedor_id !== vendedorId) {
    return estado;
  }

  const item = itemPreparadoDeResposta(dados);

  if (item === null) {
    return estado;
  }

  return {
    ...estado,
    detalhes: {
      ...detalhes,
      dados: {
        ...detalhes.dados,
        // Lista NOVA: o estado antigo nunca é alterado. O item novo entra na
        // frente porque a lista mostra o mais recente primeiro.
        feedbacks_preparados: incluirNoInicio(
          detalhes.dados.feedbacks_preparados,
          item,
        ),
      },
    },
  };
}

/**
 * Diz se a ação é da loja que está selecionada AGORA.
 *
 * Mesma proteção de "resposta antiga" usada para vendedor: quando a pessoa
 * troca de loja no seletor, a resposta da loja anterior não pode sobrescrever
 * a tela da nova.
 */
function ehDaLojaSelecionada(estado, lojaId) {
  return (
    typeof lojaId === 'string' && lojaId === estado.lojaSelecionadaId
  );
}

/**
 * Atualiza a entrada de uma loja no mapa de roteiros do gerente.
 *
 * Recebe o estado, o código da loja e os campos que mudaram. Devolve um estado
 * NOVO com o mapa copiado; os outros registros continuam intactos.
 */
function atualizarFeedbackRegional(estado, lojaId, entrada) {
  if (typeof lojaId !== 'string' || lojaId === '') {
    return estado;
  }

  const anterior = estado.feedbacksRegional[lojaId];
  return {
    ...estado,
    feedbacksRegional: {
      ...estado.feedbacksRegional,
      [lojaId]: {
        // Campos não informados mantêm o valor anterior; "dados" preserva o
        // roteiro já exibido enquanto uma nova geração está em andamento.
        ...anterior,
        ...entrada,
      },
    },
  };
}

/**
 * Põe um roteiro do gerente no topo de "Roteiros já preparados" da loja.
 *
 * Recebe o estado, o código da loja e a resposta da geração. Devolve o estado
 * com detalhesLoja atualizados ou o MESMO estado quando:
 *
 * 1) o histórico da loja ainda não foi carregado (não há lista);
 * 2) a resposta é de OUTRA loja (troca no seletor no meio da geração);
 * 3) a resposta não permite montar um item válido (sem feedback_id ou sem as
 *    quatro listas).
 *
 * O roteiro continua guardado em estado.feedbacksRegional[lojaId] nos três
 * casos; a lista do histórico espera a próxima carga para aparecer.
 */
function incluirPreparadoNoHistoricoDaLoja(estado, lojaId, dados) {
  const detalhes = estado.detalhesLoja;

  if (detalhes.status !== STATUS.SUCESSO || !detalhes.dados) {
    return estado;
  }

  if (detalhes.dados.loja_id !== lojaId) {
    return estado;
  }

  const item = itemPreparadoDeResposta(dados);

  if (item === null) {
    return estado;
  }

  return {
    ...estado,
    detalhesLoja: {
      ...detalhes,
      dados: {
        ...detalhes.dados,
        // Lista NOVA e item no início: o histórico mostra o mais novo antes.
        feedbacks_preparados: incluirNoInicio(
          detalhes.dados.feedbacks_preparados,
          item,
        ),
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

    case TIPOS.FEEDBACK_SUCESSO: {
      /*
       * O roteiro novo fica guardado por vendedor (é o que a aba Feedback
       * mostra em destaque)...
       */
      const comFeedback = atualizarFeedback(estado, acao.vendedorId, {
        status: STATUS.SUCESSO,
        dados: acao.dados ?? null,
        erro: null,
      });

      /*
       * ...e, quando o histórico da MESMA pessoa está na tela, ele também
       * entra no topo de "Roteiros já preparados" — sem nova chamada HTTP,
       * porque a resposta da geração já traz tudo. Se não for o caso, a
       * função devolve o estado como está.
       */
      return incluirPreparadoNoHistorico(
        comFeedback,
        acao.vendedorId,
        acao.dados,
      );
    }

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

    // ----- Visão da regional POR LOJA (Etapa 8) --------------------------
    case TIPOS.LOJAS_CARREGANDO:
      return {
        ...estado,
        lojas: {
          ...estado.lojas,
          status: STATUS.CARREGANDO,
          erro: null,
        },
      };

    case TIPOS.LOJAS_SUCESSO:
      return {
        ...estado,
        lojas: {
          status: STATUS.SUCESSO,
          dados: Array.isArray(acao.dados) ? acao.dados : [],
          erro: null,
        },
      };

    case TIPOS.LOJAS_ERRO:
      return {
        ...estado,
        lojas: {
          ...estado.lojas,
          status: STATUS.ERRO,
          erro: mensagemDeErro(acao.erro),
        },
      };

    case TIPOS.SELECIONAR_LOJA:
      // Trocar de loja reinicia o histórico e o envio de anotação. Os
      // roteiros já gerados continuam no mapa por loja, como acontece com os
      // feedbacks por vendedor.
      return {
        ...estado,
        lojaSelecionadaId: acao.lojaId ?? null,
        detalhesLoja: { status: STATUS.OCIOSO, dados: null, erro: null },
        novaAnotacaoRegional: { status: STATUS.OCIOSO, erro: null },
      };

    case TIPOS.DETALHES_LOJA_CARREGANDO:
      // Resposta atrasada de outra loja: ignora sem criar estado novo.
      if (!ehDaLojaSelecionada(estado, acao.lojaId)) {
        return estado;
      }
      return {
        ...estado,
        detalhesLoja: {
          ...estado.detalhesLoja,
          status: STATUS.CARREGANDO,
          erro: null,
        },
      };

    case TIPOS.DETALHES_LOJA_SUCESSO:
      if (!ehDaLojaSelecionada(estado, acao.lojaId)) {
        return estado;
      }
      return {
        ...estado,
        detalhesLoja: {
          status: STATUS.SUCESSO,
          dados: acao.dados ?? null,
          erro: null,
        },
      };

    case TIPOS.DETALHES_LOJA_ERRO:
      if (!ehDaLojaSelecionada(estado, acao.lojaId)) {
        return estado;
      }
      return {
        ...estado,
        detalhesLoja: {
          ...estado.detalhesLoja,
          status: STATUS.ERRO,
          erro: mensagemDeErro(acao.erro),
        },
      };

    case TIPOS.FEEDBACK_REGIONAL_CARREGANDO:
      return atualizarFeedbackRegional(estado, acao.lojaId, {
        status: STATUS.CARREGANDO,
        erro: null,
      });

    case TIPOS.FEEDBACK_REGIONAL_SUCESSO: {
      // O roteiro do gerente fica guardado por loja...
      const comFeedback = atualizarFeedbackRegional(estado, acao.lojaId, {
        status: STATUS.SUCESSO,
        dados: acao.dados ?? null,
        erro: null,
      });

      // ...e entra no topo da lista quando o histórico da MESMA loja está na
      // tela (sem chamada HTTP extra, como no fluxo do vendedor).
      return incluirPreparadoNoHistoricoDaLoja(
        comFeedback,
        acao.lojaId,
        acao.dados,
      );
    }

    case TIPOS.FEEDBACK_REGIONAL_ERRO:
      return atualizarFeedbackRegional(estado, acao.lojaId, {
        status: STATUS.ERRO,
        erro: mensagemDeErro(acao.erro),
      });

    case TIPOS.ANOTACAO_REGIONAL_ENVIANDO:
      // Limpa o erro anterior: uma falha velha não pode aparecer na tela
      // enquanto a nova tentativa acontece.
      return {
        ...estado,
        novaAnotacaoRegional: { status: STATUS.CARREGANDO, erro: null },
      };

    case TIPOS.ANOTACAO_REGIONAL_SUCESSO: {
      // Resposta de outra loja: descartamos. A anotação já foi gravada no
      // servidor e aparece quando aquele histórico for recarregado.
      if (!ehDaLojaSelecionada(estado, acao.lojaId)) {
        return estado;
      }

      const dados = estado.detalhesLoja.dados;
      const anotacoes = Array.isArray(dados?.anotacoes_regional)
        ? dados.anotacoes_regional
        : null;

      // Mesma decisão do fluxo do vendedor: a gravação aconteceu, então o
      // envio é SUCESSO mesmo sem uma lista onde acrescentar.
      const comSucesso = {
        ...estado,
        novaAnotacaoRegional: { status: STATUS.SUCESSO, erro: null },
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
        detalhesLoja: {
          ...estado.detalhesLoja,
          dados: {
            ...dados,
            // Lista NOVA e anotação no FIM: é a ordem cronológica que o
            // histórico da loja usa.
            anotacoes_regional: [...anotacoes, acao.dados],
          },
        },
      };
    }

    case TIPOS.ANOTACAO_REGIONAL_ERRO:
      if (!ehDaLojaSelecionada(estado, acao.lojaId)) {
        return estado;
      }
      return {
        ...estado,
        novaAnotacaoRegional: {
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
