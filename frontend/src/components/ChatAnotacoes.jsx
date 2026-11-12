/**
 * Chat de anotações reutilizável (gerente e regional).
 *
 * Apresenta uma conversa em formato de balões (um grupo por dia), com campo de
 * escrita embaixo. Não conhece a API nem o contexto: recebe a lista de
 * anotações e uma função de envio. O rascunho digitado fica DENTRO deste
 * componente e só é limpo quando aoEnviar devolve true.
 *
 * Toda a apresentação do chat mora aqui: título, área de mensagens, separador
 * de dia, balões, rolagem automática, formulário, contador, botão e erro.
 */

import { Send } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

import { EstadoVazio } from './EstadoVazio.jsx';
import { agruparPorDia } from '../utilitarios/agruparPorDia.js';
import { formatarData } from '../utilitarios/formatadores.js';
import { ordenarDaMaisAntigaParaMaisRecente } from '../utilitarios/ordenarAnotacoes.js';
import { rotuloDoDia } from '../utilitarios/rotuloDoDia.js';

// Importa o CSS do chat (as mesmas classes usadas pela página antiga).
import './ChatAnotacoes.css';

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
 * Componente ChatAnotacoes.
 *
 * Props:
 *   titulo: texto visível do cabeçalho (ex.: "Anotações sobre Bianca Rocha").
 *   nome: nome usado no placeholder e no aviso de vazio.
 *   placeholder: opcional; texto de exemplo do campo. Sem ele, o padrão é
 *     "Escreva uma observação sobre {nome}…".
 *   rotuloLog: opcional; nome acessível da região de mensagens. Sem ele, usa
 *     o mesmo texto do título.
 *   anotacoes: lista de { data, texto } já vinda da API (ordem livre).
 *   aoEnviar(texto): função async que devolve true quando gravou.
 *   enviando: true enquanto o envio está em andamento.
 *   erroEnvio: texto do erro (ou null quando não há).
 *   textoMaximo: limite de caracteres do campo (mesmo número do backend).
 *   rotuloAcessivel: nome falado do campo (o label fica oculto na tela).
 *   idCampo: identificador do campo; o título usa `${idCampo}-titulo` para
 *     dois chats na mesma tela não repetirem ids.
 *   children: conteúdo opcional exibido depois do formulário.
 *
 * Exemplo de uso:
 *   <ChatAnotacoes
 *     titulo="Anotações sobre Bianca Rocha"
 *     nome="Bianca Rocha"
 *     anotacoes={dados.anotacoes}
 *     aoEnviar={(texto) => adicionarAnotacao('C0031', texto)}
 *     enviando={false}
 *     erroEnvio={null}
 *     textoMaximo={1000}
 *     rotuloAcessivel="Nova anotação"
 *     idCampo="nova-anotacao"
 *   />
 */
export function ChatAnotacoes({
  titulo,
  nome,
  placeholder,
  rotuloLog,
  anotacoes = [],
  aoEnviar,
  enviando = false,
  erroEnvio = null,
  textoMaximo,
  rotuloAcessivel,
  idCampo,
  children,
}) {
  // O rascunho mora aqui: cada chat tem o seu, e trocar de tela com "key"
  // diferente (como a página faz por vendedor) zera tudo.
  const [texto, setTexto] = useState('');

  // useRef: uma "caixa" que guarda um elemento da tela entre renderizações,
  // sem provocar nova renderização. Guardamos o campo de escrita (para
  // devolver o foco) e o fim da lista (para rolar até lá).
  const campoRef = useRef(null);
  const fimRef = useRef(null);

  const idTitulo = `${idCampo}-titulo`;

  /*
   * Garante uma lista de verdade e ESTÁVEL entre renderizações. Se o valor
   * recebido não for uma lista, devolvemos sempre a MESMA lista vazia (via
   * useMemo); sem isso, o efeito de rolagem rodaria a cada renderização.
   */
  const lista = useMemo(
    () => (Array.isArray(anotacoes) ? anotacoes : []),
    [anotacoes],
  );

  /*
   * Texto de exemplo e rótulo acessível do log são personalizáveis pelas
   * telas; sem eles, o componente mantém os textos originais (usados pelo
   * gerente), então nada muda para quem não passa as props.
   */
  const textoPlaceholder =
    placeholder ?? `Escreva uma observação sobre ${nome}…`;
  const rotuloDoLog = rotuloLog ?? titulo;

  // --- Conversa: da mais antiga para a mais nova, agrupada por dia ---
  const grupos = agruparPorDia(
    ordenarDaMaisAntigaParaMaisRecente(lista),
  );

  const hoje = dataDeHoje();

  /*
   * Rola até o fim quando a conversa muda (inclusive logo depois de enviar,
   * porque a página troca o objeto de anotações ao acrescentar a nova).
   */
  useEffect(() => {
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
  }, [lista]);

  const podeEnviar = !enviando && texto.trim() !== '';

  /**
   * Envia a anotação digitada.
   *
   * Recebe o evento do formulário (submit) ou nada, quando chamada pelo
   * Enter. Devolve uma Promise (é uma função async).
   *
   * Se a função recebida devolver true, a anotação foi gravada: limpamos o
   * campo e devolvemos o foco a ele. Se devolver false, MANTEMOS o texto
   * digitado (ninguém perde o que escreveu) e a mensagem de erro aparece
   * embaixo, vinda da prop erroEnvio.
   */
  async function enviar(evento) {
    // O formulário, por padrão, recarrega a página ao enviar. Precisamos
    // impedir isso para continuar no app.
    evento?.preventDefault?.();

    if (!podeEnviar) {
      return;
    }

    const deuCerto = await aoEnviar?.(texto);

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
    enviar();
  }

  return (
    <>
      {/* ---------- Conversa ---------- */}
      <section
        className="pagina-anotacoes__chat"
        aria-labelledby={idTitulo}
      >
        <h2 id={idTitulo} className="pagina-anotacoes__titulo">
          {titulo}
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
          aria-label={rotuloDoLog}
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
      <form className="pagina-anotacoes__formulario" onSubmit={enviar}>
        {/*
         * O label fica escondido da tela (ui-visualmente-oculto) mas continua
         * ligado ao campo pelo htmlFor/id: leitores de tela anunciam o rótulo
         * ao chegar no campo.
         */}
        <label htmlFor={idCampo} className="ui-visualmente-oculto">
          {rotuloAcessivel}
        </label>

        {/*
         * textarea = campo de texto com várias linhas.
         * maxLength usa o mesmo número do backend: o navegador nem deixa
         * passar do limite; o backend valida de novo por segurança.
         */}
        <textarea
          id={idCampo}
          ref={campoRef}
          className="pagina-anotacoes__campo"
          placeholder={textoPlaceholder}
          value={texto}
          onChange={(evento) => setTexto(evento.target.value)}
          onKeyDown={aoTeclarNoCampo}
          maxLength={textoMaximo}
          rows={2}
        />

        <div className="pagina-anotacoes__acoes">
          {/* Contador discreto: só orienta, não bloqueia nada. */}
          <span className="pagina-anotacoes__contador">
            {texto.length}/{textoMaximo}
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
        {erroEnvio && (
          <p className="pagina-anotacoes__erro" role="alert">
            {erroEnvio}
          </p>
        )}
      </form>

      {/* Conteúdo opcional depois do formulário (ex.: anotações do time). */}
      {children}
    </>
  );
}
