/**
 * Página da aba Anotações do colaborador selecionado, em formato de conversa.
 *
 * As anotações sobre a pessoa aparecem como mensagens (da mais antiga para a
 * mais nova, separadas por dia) e, embaixo, há um campo para escrever uma nova
 * anotação — que fica guardada no sistema e passa a valer para o feedback.
 * As anotações sobre o time ficam numa seção recolhível, só de leitura.
 *
 * A página NÃO calcula nada nem fala com a API: lê estado.detalhes e
 * estado.novaAnotacao e chama as ações do contexto.
 */

import { Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { ANOTACAO_TEXTO_MAXIMO, STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { agruparPorDia } from '../utilitarios/agruparPorDia.js';
import { formatarData } from '../utilitarios/formatadores.js';
import {
  ordenarAnotacoes,
  ordenarDaMaisAntigaParaMaisRecente,
} from '../utilitarios/ordenarAnotacoes.js';
import { rotuloDoDia } from '../utilitarios/rotuloDoDia.js';

// Importa o CSS desta página.
import './PaginaAnotacoes.css';

/**
 * Devolve a data de hoje no formato "AAAA-MM-DD".
 *
 * Usa o calendário LOCAL do computador (getFullYear/getMonth/getDate), que é
 * o "hoje" que a pessoa vê na parede. A conta é feita com as partes da data,
 * sem new Date("AAAA-MM-DD"), para não esbarrar em fuso horário.
 *
 * Exemplo: em 12/11/2026 devolve "2026-11-12".
 */
function dataDeHoje() {
  const agora = new Date();
  const ano = agora.getFullYear();
  // getMonth começa em 0 (janeiro); +1 acerta o calendário. padStart garante
  // dois dígitos ("11" continua "11", "1" vira "01").
  const mes = String(agora.getMonth() + 1).padStart(2, '0');
  const dia = String(agora.getDate()).padStart(2, '0');

  return `${ano}-${mes}-${dia}`;
}

/**
 * Diz se a pessoa pediu ao sistema para reduzir animações.
 *
 * Quando a resposta é true, a rolagem automática usa o modo "auto" (salto
 * direto, sem deslizar), que é mais confortável para quem sente desconforto
 * com movimento na tela.
 */
function prefereMenosMovimento() {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }

  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Monta o balão de uma anotação.
 *
 * Recebe a anotação (formato da API) e devolve um item de lista alinhado à
 * direita, com o texto exatamente como veio e a data em <time>.
 *
 * O <time> é o elemento que representa data/hora; o atributo dateTime guarda
 * a data legível por máquina ("2026-10-08") enquanto a tela mostra o formato
 * brasileiro ("08/10/2026").
 */
function balaoDeAnotacao(anotacao, indice) {
  return (
    <li key={`${anotacao.data}-${indice}`} className="pagina-anotacoes__linha">
      <div className="pagina-anotacoes__balao">
        {/* Texto simples do React: nunca é interpretado como HTML. */}
        <p className="pagina-anotacoes__texto">{anotacao.texto}</p>

        <time className="pagina-anotacoes__data" dateTime={anotacao.data}>
          {formatarData(anotacao.data)}
        </time>
      </div>
    </li>
  );
}

/**
 * Componente PaginaAnotacoes.
 *
 * Não recebe props: lê do contexto o histórico (estado.detalhes), o envio de
 * anotação (estado.novaAnotacao), o vendedor selecionado e as ações
 * selecionarVendedor (para "tentar de novo") e adicionarAnotacao (para
 * enviar).
 *
 * Exemplo de uso (com key, para o rascunho zerar ao trocar de pessoa):
 *   <PaginaAnotacoes key={vendedorSelecionadoId} />
 */
export function PaginaAnotacoes() {
  const { estado, selecionarVendedor, adicionarAnotacao } = useApp();

  const { status, dados, erro } = estado.detalhes;
  const vendedorId = estado.vendedorSelecionadoId;

  // "Hook" é uma função do React que começa com "use". Todos ficam aqui em
  // cima, ANTES dos returns de carregando/erro, porque hook nunca pode ser
  // chamado dentro de um "if" (a ordem de chamada tem de ser sempre a mesma).
  const [texto, setTexto] = useState('');

  // useRef: uma "caixa" que guarda um elemento da tela entre renderizações,
  // sem provocar nova renderização. Guardamos o campo de escrita (para
  // devolver o foco) e o fim da lista (para rolar até lá).
  const campoRef = useRef(null);
  const fimRef = useRef(null);

  const enviando = estado.novaAnotacao.status === STATUS.CARREGANDO;

  /*
   * useMemo não é necessário aqui: as listas são pequenas e a ordenação é
   * barata. Este useEffect roda quando o histórico chega (status/dados mudam)
   * — inclusive logo depois de enviar, porque o reducer troca o objeto
   * "dados" ao acrescentar a anotação nova.
   */
  useEffect(() => {
    // Enquanto carrega (ou deu erro) não há conversa para rolar.
    if (status !== STATUS.SUCESSO || !dados) {
      return;
    }

    const fim = fimRef.current;

    if (fim === null) {
      return;
    }

    fim.scrollIntoView({
      // "auto" = salto direto; "smooth" = desliza. Respeita quem prefere
      // menos movimento (prefers-reduced-motion).
      behavior: prefereMenosMovimento() ? 'auto' : 'smooth',
      block: 'nearest',
    });
  }, [status, dados]);

  // "ocioso" também conta como carregando: ao trocar de vendedor, o reducer
  // zera os detalhes e o pedido começa logo em seguida.
  if (status === STATUS.OCIOSO || status === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando as anotações…"
        linhas={3}
        variante="cartao"
      />
    );
  }

  if (status === STATUS.ERRO) {
    return (
      <EstadoErro
        mensagem={erro}
        aoTentarDeNovo={
          vendedorId ? () => selecionarVendedor(vendedorId) : undefined
        }
      />
    );
  }

  if (!dados) {
    return (
      <EstadoVazio
        titulo="Sem dados do colaborador"
        descricao="Escolha um colaborador para ver as anotações."
      />
    );
  }

  // Nome para os textos da página; se faltar, usamos uma expressão genérica.
  const nome =
    typeof dados.nome === 'string' && dados.nome.trim() !== ''
      ? dados.nome
      : 'o colaborador';

  const hoje = dataDeHoje();

  // --- Conversa: da mais antiga para a mais nova, agrupada por dia ---
  const anotacoesDaPessoa = ordenarDaMaisAntigaParaMaisRecente(
    dados.anotacoes ?? [],
  );
  const grupos = agruparPorDia(anotacoesDaPessoa);

  // --- Time: só leitura, da mais recente para a mais antiga ---
  const anotacoesDoTime = ordenarAnotacoes(dados.anotacoes_do_time ?? []);

  const textoSemEspacos = texto.trim();
  const podeEnviar =
    !enviando && textoSemEspacos !== '' && Boolean(vendedorId);

  /**
   * Envia a anotação digitada.
   *
   * Recebe o evento do formulário (submit) ou nada, quando chamada pelo
   * Enter. Devolve uma Promise (é uma função async).
   *
   * Se o contexto devolver true, a anotação foi gravada: limpamos o campo e
   * devolvemos o foco a ele. Se devolver false, MANTEMOS o texto digitado
   * (ninguém perde o que escreveu) e a mensagem de erro aparece embaixo,
   * vinda de estado.novaAnotacao.erro.
   */
  async function aoEnviar(evento) {
    // O formulário, por padrão, recarrega a página ao enviar. Precisamos
    // impedir isso para continuar no app.
    evento?.preventDefault?.();

    if (!podeEnviar) {
      return;
    }

    const deuCerto = await adicionarAnotacao(vendedorId, texto);

    if (deuCerto) {
      setTexto('');
      campoRef.current?.focus();
    }
  }

  /**
   * Trata as teclas dentro do campo de escrita.
   *
   * Enter envia; Shift+Enter quebra a linha (comportamento normal do campo).
   * Durante a composição de texto por IME (isComposing) o Enter NÃO envia:
   * IME é o método usado para digitar idiomas como japonês e chinês, em que o
   * Enter também serve para confirmar o caractere. Sem essa checagem, a
   * pessoa enviaria a anotação no meio da digitação.
   */
  function aoTeclarNoCampo(evento) {
    if (evento.key !== 'Enter' || evento.shiftKey) {
      return;
    }

    if (evento.nativeEvent?.isComposing === true) {
      return;
    }

    // Evita a quebra de linha que o Enter causaria no campo.
    evento.preventDefault();
    aoEnviar();
  }

  return (
    <div className="pagina-anotacoes">
      {/*
       * Orientação curta e verdadeira: as anotações ficam gravadas (arquivo
       * próprio do backend, testado) e entram no prompt da IA (testado em
       * test_data_loader_anotacoes_novas.py).
       */}
      <p className="pagina-anotacoes__orientacao">
        Escreva aqui o que observar durante o mês. As anotações ficam
        guardadas e entram no feedback.
      </p>

      {/* ---------- Conversa ---------- */}
      <section
        className="pagina-anotacoes__chat"
        aria-labelledby="titulo-anotacoes-pessoa"
      >
        <h2
          id="titulo-anotacoes-pessoa"
          className="pagina-anotacoes__titulo"
        >
          Anotações sobre {nome}
        </h2>

        {/*
         * role="log" diz ao leitor de tela que este bloco é uma lista de
         * mensagens em ordem cronológica; aria-live="polite" faz ele anunciar
         * o que entra sem interromper a leitura em andamento.
         */}
        <div
          className="pagina-anotacoes__mensagens"
          role="log"
          aria-live="polite"
          aria-label={`Anotações sobre ${nome}`}
        >
          {grupos.length === 0 ? (
            <EstadoVazio
              titulo={`Ainda não há anotações sobre ${nome}`}
              descricao="Escreva a primeira abaixo."
            />
          ) : (
            grupos.map((grupo) => (
              <div key={grupo.data} className="pagina-anotacoes__dia">
                {/* Separador de dia: "Hoje", "Ontem" ou a data. */}
                <p className="pagina-anotacoes__separador">
                  {rotuloDoDia(grupo.data, hoje)}
                </p>

                <ul className="pagina-anotacoes__lista">
                  {grupo.itens.map((anotacao, indice) =>
                    balaoDeAnotacao(anotacao, indice),
                  )}
                </ul>
              </div>
            ))
          )}

          {/*
           * Sentinela invisível no fim: é para cá que a rolagem automática
           * aponta quando chega mensagem nova.
           */}
          <div ref={fimRef} />
        </div>
      </section>

      {/* ---------- Campo de escrita ---------- */}
      <form className="pagina-anotacoes__formulario" onSubmit={aoEnviar}>
        {/*
         * O label fica escondido da tela (ui-visualmente-oculto) mas continua
         * ligado ao campo pelo htmlFor/id: leitores de tela anunciam "Nova
         * anotação" ao chegar no campo.
         */}
        <label htmlFor="nova-anotacao" className="ui-visualmente-oculto">
          Nova anotação
        </label>

        {/*
         * textarea = campo de texto com várias linhas.
         * maxLength usa o mesmo número do backend: o navegador nem deixa
         * passar do limite; o backend valida de novo por segurança.
         */}
        <textarea
          id="nova-anotacao"
          ref={campoRef}
          className="pagina-anotacoes__campo"
          placeholder={`Escreva uma observação sobre ${nome}…`}
          value={texto}
          onChange={(evento) => setTexto(evento.target.value)}
          onKeyDown={aoTeclarNoCampo}
          maxLength={ANOTACAO_TEXTO_MAXIMO}
          rows={2}
        />

        <div className="pagina-anotacoes__acoes">
          {/* Contador discreto: só orienta, não bloqueia nada. */}
          <span className="pagina-anotacoes__contador">
            {texto.length}/{ANOTACAO_TEXTO_MAXIMO}
          </span>

          <button
            type="submit"
            className="ui-botao-primario pagina-anotacoes__botao"
            /*
             * aria-label dá o nome do botão ao leitor de tela. Ele acompanha
             * o texto visível ("Enviar" / "Enviando…") para o nome falado
             * nunca contradizer o que está escrito na tela.
             */
            aria-label={
              enviando ? 'Enviando anotação' : 'Enviar anotação'
            }
            disabled={!podeEnviar}
          >
            {/* Ícone decorativo: o texto ao lado já diz o que o botão faz. */}
            <Send aria-hidden="true" />
            {enviando ? 'Enviando…' : 'Enviar'}
          </button>
        </div>

        {/*
         * Erro do envio: o texto vem pronto do estado (mensagem do backend) e
         * role="alert" faz o leitor de tela anunciá-lo na hora. O texto
         * digitado continua no campo, então dá para tentar de novo.
         */}
        {estado.novaAnotacao.status === STATUS.ERRO &&
          estado.novaAnotacao.erro && (
            <p className="pagina-anotacoes__erro" role="alert">
              {estado.novaAnotacao.erro}
            </p>
          )}
      </form>

      {/*
       * <details> é o bloco que abre e fecha ao clicar no <summary> (o
       * título). Fecha por padrão para não competir com a conversa.
       */}
      <details className="pagina-anotacoes__time">
        <summary className="pagina-anotacoes__time-resumo">
          Anotações sobre o time ({anotacoesDoTime.length})
        </summary>

        <p className="pagina-anotacoes__explicacao">
          Observações sobre a loja toda, que ajudam a entender o contexto.
        </p>

        {anotacoesDoTime.length === 0 ? (
          <EstadoVazio
            titulo="Nenhuma anotação do time"
            descricao="Ainda não há observações sobre a loja toda."
          />
        ) : (
          <ul className="pagina-anotacoes__lista-time">
            {anotacoesDoTime.map((anotacao, indice) => (
              <li
                key={`time-${anotacao.data}-${indice}`}
                className="pagina-anotacoes__item-time"
              >
                <time dateTime={anotacao.data}>
                  {formatarData(anotacao.data)}
                </time>

                <p className="pagina-anotacoes__texto">{anotacao.texto}</p>
              </li>
            ))}
          </ul>
        )}
      </details>
    </div>
  );
}
