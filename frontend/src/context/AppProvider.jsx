/**
 * Provider do estado global da aplicação.
 *
 * Provider: o componente que "abraça" a árvore e oferece o contexto para
 * todos os filhos. Aqui ele guarda o estado (useReducer), expõe as ações
 * assíncronas (que chamam os serviços HTTP) e cuida de cancelar pedidos
 * pendentes quando a tela sai.
 */

import { useCallback, useEffect, useMemo, useReducer, useRef } from 'react';

import { criarEstadoInicial, appReducer, TIPOS } from './appReducer.js';
import { AppContext } from './appContext.js';
import { erroFoiCancelamento } from '../services/erroApi.js';
import {
  obterVendedoresPorLoja,
  obterDetalhesVendedor,
} from '../services/vendedorService.js';
import { gerarFeedback as gerarFeedbackDaApi } from '../services/feedbackService.js';
import { obterDesempenhoGerente } from '../services/regionalService.js';

/**
 * Serviços reais usados por padrão.
 *
 * O Provider aceita "servicos" como parâmetro para que testes (ou uma tela
 * de demonstração) possam trocar a rede por versões falsas sem alterar este
 * componente.
 */
const SERVICOS_REAIS = {
  obterVendedoresPorLoja,
  obterDetalhesVendedor,
  gerarFeedback: gerarFeedbackDaApi,
  obterDesempenhoGerente,
};

/**
 * Componente que fornece estado e ações para toda a aplicação.
 *
 * Recebe:
 *   children: os componentes que recebem o contexto.
 *   servicos: opcional; por padrão, os serviços reais de src/services/.
 */
export function AppProvider({ children, servicos = SERVICOS_REAIS }) {
  // useReducer: guarda o estado e entrega "despachar" para enviar ações ao
  // reducer (função pura testada em appReducer.test.js).
  const [estado, despachar] = useReducer(
    appReducer,
    undefined,
    criarEstadoInicial,
  );

  // useRef: uma "caixa" que guarda um valor entre renderizações sem
  // provocar nova renderização. Usamos para os canceladores (AbortController)
  // e para saber quais gerações já estão em andamento.
  const detalhesControlador = useRef(null);
  const regionalControlador = useRef(null);
  const geracoes = useRef(new Map());

  /**
   * Busca a lista de vendedores da loja.
   *
   * Recebe opcionalmente { mes } ("AAAA-MM"). Despacha carregando, sucesso
   * (com a lista) ou erro (com a mensagem). Cancelamentos não viram erro.
   */
  const carregarVendedores = useCallback(
    async ({ mes } = {}) => {
      despachar({ tipo: TIPOS.VENDEDORES_CARREGANDO });

      try {
        const dados = await servicos.obterVendedoresPorLoja(estado.lojaId, {
          mes,
        });
        despachar({ tipo: TIPOS.VENDEDORES_SUCESSO, dados });
      } catch (erro) {
        // Cancelamento é escolha nossa, não falha: não mostramos nada.
        if (erroFoiCancelamento(erro)) {
          return;
        }
        despachar({ tipo: TIPOS.VENDEDORES_ERRO, erro });
      }
    },
    [estado.lojaId, servicos],
  );

  /**
   * Seleciona um vendedor e carrega o histórico dele.
   *
   * Se havia uma requisição de detalhes em andamento, ela é cancelada antes
   * (evita duas respostas competindo pela mesma tela). O reducer também
   * descarta respostas antigas, como segunda proteção.
   */
  const selecionarVendedor = useCallback(
    async (vendedorId) => {
      // Aborta (cancela) o pedido anterior, se ainda estiver rodando.
      detalhesControlador.current?.abort();

      const controlador = new AbortController();
      detalhesControlador.current = controlador;

      despachar({ tipo: TIPOS.SELECIONAR_VENDEDOR, vendedorId });
      despachar({ tipo: TIPOS.DETALHES_CARREGANDO, vendedorId });

      try {
        const dados = await servicos.obterDetalhesVendedor(vendedorId, {
          signal: controlador.signal,
        });
        despachar({ tipo: TIPOS.DETALHES_SUCESSO, vendedorId, dados });
      } catch (erro) {
        if (erroFoiCancelamento(erro)) {
          return;
        }
        despachar({ tipo: TIPOS.DETALHES_ERRO, vendedorId, erro });
      }
    },
    [servicos],
  );

  /**
   * Gera o roteiro de feedback de um vendedor.
   *
   * Se já existe uma geração em andamento para a MESMA pessoa, a nova
   * chamada é ignorada: duplo clique não pode gastar créditos de IA duas
   * vezes. Não há retry automático — repetir também custaria créditos.
   */
  const gerarFeedback = useCallback(
    async (vendedorId, { mesReferencia } = {}) => {
      if (geracoes.current.has(vendedorId)) {
        return;
      }

      const controlador = new AbortController();
      geracoes.current.set(vendedorId, controlador);

      despachar({ tipo: TIPOS.FEEDBACK_CARREGANDO, vendedorId });

      try {
        const dados = await servicos.gerarFeedback(vendedorId, {
          mesReferencia,
          signal: controlador.signal,
        });
        despachar({ tipo: TIPOS.FEEDBACK_SUCESSO, vendedorId, dados });
      } catch (erro) {
        if (!erroFoiCancelamento(erro)) {
          despachar({ tipo: TIPOS.FEEDBACK_ERRO, vendedorId, erro });
        }
      } finally {
        // Libera a trava para a pessoa poder gerar de novo depois.
        geracoes.current.delete(vendedorId);
      }
    },
    [servicos],
  );

  /**
   * Carrega o consolidado da visão regional.
   *
   * Também cancela o pedido anterior, caso a pessoa peça de novo rápido.
   */
  const carregarRegional = useCallback(async () => {
    regionalControlador.current?.abort();

    const controlador = new AbortController();
    regionalControlador.current = controlador;

    despachar({ tipo: TIPOS.REGIONAL_CARREGANDO });

    try {
      const dados = await servicos.obterDesempenhoGerente({
        signal: controlador.signal,
      });
      despachar({ tipo: TIPOS.REGIONAL_SUCESSO, dados });
    } catch (erro) {
      if (erroFoiCancelamento(erro)) {
        return;
      }
      despachar({ tipo: TIPOS.REGIONAL_ERRO, erro });
    }
  }, [servicos]);

  /** Troca a aba do gerente. O reducer recusa valores desconhecidos. */
  const mudarAba = useCallback((aba) => {
    despachar({ tipo: TIPOS.MUDAR_ABA, aba });
  }, []);

  /** Troca a visão (gerente/regional). O reducer valida o valor. */
  const mudarVisao = useCallback((visao) => {
    despachar({ tipo: TIPOS.MUDAR_VISAO, visao });
  }, []);

  // Ao desmontar o Provider, cancelamos tudo o que estiver pendente.
  //
  // Em desenvolvimento, o StrictMode do React monta e desmonta o componente
  // duas vezes de propósito, para revelar efeitos mal feitos. Sem cancelar,
  // a primeira montagem deixaria uma requisição correndo e a resposta dela
  // poderia chegar depois, mexendo no estado da segunda montagem.
  useEffect(() => {
    const controladoresDeGeracao = geracoes.current;

    return () => {
      detalhesControlador.current?.abort();
      regionalControlador.current?.abort();

      for (const controlador of controladoresDeGeracao.values()) {
        controlador.abort();
      }
      controladoresDeGeracao.clear();
    };
  }, []);

  // useMemo: monta o valor do contexto uma vez por mudança de estado/ações,
  // em vez de criar um objeto novo em cada renderização dos filhos.
  const valor = useMemo(
    () => ({
      estado,
      carregarVendedores,
      selecionarVendedor,
      gerarFeedback,
      carregarRegional,
      mudarAba,
      mudarVisao,
    }),
    [
      estado,
      carregarVendedores,
      selecionarVendedor,
      gerarFeedback,
      carregarRegional,
      mudarAba,
      mudarVisao,
    ],
  );

  return <AppContext.Provider value={valor}>{children}</AppContext.Provider>;
}
