/**
 * Provider do estado global da aplicação.
 *
 * Provider: o componente que "abraça" a árvore e oferece o contexto para
 * todos os filhos. Aqui ele guarda o estado (useReducer), expõe as ações
 * assíncronas (carregar a lista, selecionar alguém, gerar feedback, gravar
 * uma ANOTAÇÃO NOVA, carregar a regional e as ações POR LOJA da Etapa 8) e
 * cuida de cancelar pedidos pendentes quando a tela sai.
 */

import { useCallback, useEffect, useMemo, useReducer, useRef } from 'react';

import { criarEstadoInicial, appReducer, TIPOS } from './appReducer.js';
import { AppContext } from './appContext.js';
import { erroFoiCancelamento } from '../services/erroApi.js';
import { registrarAnotacao } from '../services/anotacaoService.js';
import {
  obterVendedoresPorLoja,
  obterDetalhesVendedor,
} from '../services/vendedorService.js';
import { gerarFeedback as gerarFeedbackDaApi } from '../services/feedbackService.js';
import {
  listarLojas,
  obterHistoricoLoja,
  registrarAnotacaoRegional,
  gerarFeedbackRegional as gerarFeedbackRegionalDaApi,
} from '../services/regionalService.js';

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
  registrarAnotacao,
  listarLojas,
  obterHistoricoLoja,
  registrarAnotacaoRegional,
  gerarFeedbackRegional: gerarFeedbackRegionalDaApi,
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
  const geracoes = useRef(new Map());
  // Controlador do envio de anotação em andamento (null = nenhum).
  const anotacaoControlador = useRef(null);

  // ----- Regional POR LOJA (Etapa 8) ----------------------------------
  // Controladores próprios para não misturar com os pedidos do gerente.
  const lojasControlador = useRef(null);
  const detalhesLojaControlador = useRef(null);
  const geracoesRegionais = useRef(new Map());
  const anotacaoRegionalControlador = useRef(null);

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
        // A API devolve o envelope { loja_id, loja_nome, mes, vendedores }.
        // O reducer guarda SOMENTE a lista, então extraímos "vendedores"
        // aqui. Sem isso, o reducer receberia um objeto, descartaria tudo e
        // a tela mostraria sempre a lista vazia.
        const resposta = await servicos.obterVendedoresPorLoja(estado.lojaId, {
          mes,
        });
        despachar({
          tipo: TIPOS.VENDEDORES_SUCESSO,
          dados: resposta.vendedores,
        });
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
   * Grava uma anotação nova sobre um vendedor.
   *
   * Recebe o código da pessoa e o texto digitado. Devolve uma Promise com
   * TRUE quando gravou e FALSE quando falhou — a tela usa esse retorno para
   * limpar o campo de texto só quando deu certo (se falhou, o texto continua
   * lá para a pessoa tentar de novo sem digitar tudo outra vez).
   *
   * Enquanto um envio está em andamento, uma nova chamada é ignorada: duplo
   * clique não pode gravar a mesma anotação duas vezes. Não há tentativa
   * automática: se falhou, quem decide repetir é a pessoa.
   */
  const adicionarAnotacao = useCallback(
    async (vendedorId, texto) => {
      // Já existe um envio em andamento: não dispara outro.
      if (anotacaoControlador.current !== null) {
        return false;
      }

      const controlador = new AbortController();
      anotacaoControlador.current = controlador;

      despachar({ tipo: TIPOS.ANOTACAO_ENVIANDO });

      try {
        const dados = await servicos.registrarAnotacao(vendedorId, texto, {
          signal: controlador.signal,
        });
        despachar({ tipo: TIPOS.ANOTACAO_SUCESSO, vendedorId, dados });
        return true;
      } catch (erro) {
        // Cancelamento é escolha nossa (troca de tela), não falha do usuário.
        if (!erroFoiCancelamento(erro)) {
          despachar({ tipo: TIPOS.ANOTACAO_ERRO, vendedorId, erro });
        }
        return false;
      } finally {
        // Libera a trava para a próxima anotação poder ser enviada.
        anotacaoControlador.current = null;
      }
    },
    [servicos],
  );

  /**
   * Carrega a lista de lojas que a regional pode acompanhar.
   *
   * Cancela o pedido anterior (se a pessoa pedir de novo rápido) e extrai
   * SOMENTE a lista "lojas" do envelope da API, como carregarVendedores faz.
   */
  const carregarLojas = useCallback(async () => {
    lojasControlador.current?.abort();

    const controlador = new AbortController();
    lojasControlador.current = controlador;

    despachar({ tipo: TIPOS.LOJAS_CARREGANDO });

    try {
      const resposta = await servicos.listarLojas({
        signal: controlador.signal,
      });
      despachar({ tipo: TIPOS.LOJAS_SUCESSO, dados: resposta.lojas });
    } catch (erro) {
      if (erroFoiCancelamento(erro)) {
        return;
      }
      despachar({ tipo: TIPOS.LOJAS_ERRO, erro });
    }
  }, [servicos]);

  /**
   * Seleciona uma loja e carrega o histórico dela.
   *
   * Aborta o pedido anterior antes de começar (duas respostas não competem
   * pela mesma tela) e despacha a seleção + o carregamento. O reducer também
   * descarta respostas de outra loja, como segunda proteção.
   */
  const selecionarLoja = useCallback(
    async (lojaId) => {
      detalhesLojaControlador.current?.abort();

      const controlador = new AbortController();
      detalhesLojaControlador.current = controlador;

      despachar({ tipo: TIPOS.SELECIONAR_LOJA, lojaId });
      despachar({ tipo: TIPOS.DETALHES_LOJA_CARREGANDO, lojaId });

      try {
        const dados = await servicos.obterHistoricoLoja(lojaId, {
          signal: controlador.signal,
        });
        despachar({ tipo: TIPOS.DETALHES_LOJA_SUCESSO, lojaId, dados });
      } catch (erro) {
        if (erroFoiCancelamento(erro)) {
          return;
        }
        despachar({ tipo: TIPOS.DETALHES_LOJA_ERRO, lojaId, erro });
      }
    },
    [servicos],
  );

  /**
   * Grava uma anotação nova da regional sobre a loja.
   *
   * Devolve TRUE quando gravou e FALSE quando falhou, como adicionarAnotacao:
   * a tela limpa o campo só no sucesso. Enquanto um envio está em andamento,
   * uma nova chamada é ignorada (duplo clique não grava duas vezes).
   */
  const adicionarAnotacaoRegional = useCallback(
    async (lojaId, texto) => {
      if (anotacaoRegionalControlador.current !== null) {
        return false;
      }

      const controlador = new AbortController();
      anotacaoRegionalControlador.current = controlador;

      despachar({ tipo: TIPOS.ANOTACAO_REGIONAL_ENVIANDO });

      try {
        const dados = await servicos.registrarAnotacaoRegional(
          lojaId,
          texto,
          { signal: controlador.signal },
        );
        despachar({
          tipo: TIPOS.ANOTACAO_REGIONAL_SUCESSO,
          lojaId,
          dados,
        });
        return true;
      } catch (erro) {
        if (!erroFoiCancelamento(erro)) {
          despachar({ tipo: TIPOS.ANOTACAO_REGIONAL_ERRO, lojaId, erro });
        }
        return false;
      } finally {
        anotacaoRegionalControlador.current = null;
      }
    },
    [servicos],
  );

  /**
   * Gera o roteiro de feedback do gerente da loja com a IA.
   *
   * Se já existe uma geração em andamento para a MESMA loja, a nova chamada
   * é ignorada: duplo clique não pode gastar créditos de IA duas vezes. Não
   * há retry automático, pelo mesmo motivo.
   */
  const gerarFeedbackRegional = useCallback(
    async (lojaId, { mesReferencia } = {}) => {
      if (geracoesRegionais.current.has(lojaId)) {
        return;
      }

      const controlador = new AbortController();
      geracoesRegionais.current.set(lojaId, controlador);

      despachar({
        tipo: TIPOS.FEEDBACK_REGIONAL_CARREGANDO,
        lojaId,
      });

      try {
        const dados = await servicos.gerarFeedbackRegional(lojaId, {
          mesReferencia,
          signal: controlador.signal,
        });
        despachar({
          tipo: TIPOS.FEEDBACK_REGIONAL_SUCESSO,
          lojaId,
          dados,
        });
      } catch (erro) {
        if (!erroFoiCancelamento(erro)) {
          despachar({ tipo: TIPOS.FEEDBACK_REGIONAL_ERRO, lojaId, erro });
        }
      } finally {
        // Libera a trava para a pessoa poder gerar de novo depois.
        geracoesRegionais.current.delete(lojaId);
      }
    },
    [servicos],
  );

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
    const controladoresDeGeracaoRegional = geracoesRegionais.current;

    return () => {
      detalhesControlador.current?.abort();
      // Envio de anotação em andamento também é cancelado.
      anotacaoControlador.current?.abort();

      // Ações por loja da Etapa 8.
      lojasControlador.current?.abort();
      detalhesLojaControlador.current?.abort();
      anotacaoRegionalControlador.current?.abort();

      for (const controlador of controladoresDeGeracao.values()) {
        controlador.abort();
      }
      controladoresDeGeracao.clear();

      for (const controlador of controladoresDeGeracaoRegional.values()) {
        controlador.abort();
      }
      controladoresDeGeracaoRegional.clear();
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
      adicionarAnotacao,
      carregarLojas,
      selecionarLoja,
      adicionarAnotacaoRegional,
      gerarFeedbackRegional,
      mudarAba,
      mudarVisao,
    }),
    [
      estado,
      carregarVendedores,
      selecionarVendedor,
      gerarFeedback,
      adicionarAnotacao,
      carregarLojas,
      selecionarLoja,
      adicionarAnotacaoRegional,
      gerarFeedbackRegional,
      mudarAba,
      mudarVisao,
    ],
  );

  return <AppContext.Provider value={valor}>{children}</AppContext.Provider>;
}
