/**
 * Aba Anotações da visão regional (Etapa 8).
 *
 * Mostra as anotações que a gerente regional escreveu sobre a loja escolhida,
 * em formato de conversa, e permite gravar uma nova. Usa o ChatAnotacoes
 * (o mesmo do gerente) e cuida só do que é específico da regional: estados,
 * orientação e a derivação de textos a partir dos dados da loja.
 *
 * A autora NÃO aparece em cada balão (é sempre a regional); o nome dela entra
 * no rótulo acessível da região de mensagens quando há anotação.
 *
 * A página não busca dados sozinha: quem carrega é a seleção da loja.
 */

import { ANOTACAO_TEXTO_MAXIMO, STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { ChatAnotacoes } from '../components/ChatAnotacoes.jsx';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { ordenarDaMaisAntigaParaMaisRecente } from '../utilitarios/ordenarAnotacoes.js';

// Importa o CSS desta página (estrutura e orientação próprias).
import './PaginaAnotacoesRegional.css';

/**
 * Componente PaginaAnotacoesRegional.
 *
 * Não recebe props: lê do contexto o histórico da loja (estado.detalhesLoja),
 * o envio (estado.novaAnotacaoRegional), a loja selecionada e as ações
 * selecionarLoja (para "tentar de novo") e adicionarAnotacaoRegional.
 *
 * Exemplo de uso: <PaginaAnotacoesRegional />
 */
export function PaginaAnotacoesRegional() {
  const { estado, selecionarLoja, adicionarAnotacaoRegional } = useApp();

  const { status, dados, erro } = estado.detalhesLoja;
  const lojaId = estado.lojaSelecionadaId;

  // Primeira carga (ocioso) e recarga aparecem como carregando.
  if (status === STATUS.OCIOSO || status === STATUS.CARREGANDO) {
    return (
      <EstadoCarregando
        titulo="Carregando as anotações da loja…"
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
          lojaId ? () => selecionarLoja(lojaId) : undefined
        }
      />
    );
  }

  if (!dados) {
    return (
      <EstadoVazio
        titulo="Sem dados da loja"
        descricao="Escolha uma loja no card da barra lateral para ver as anotações dela."
      />
    );
  }

  // Nomes vindos da API; se faltarem, usamos expressões genéricas.
  const lojaNome =
    typeof dados.loja_nome === 'string' && dados.loja_nome.trim() !== ''
      ? dados.loja_nome.trim()
      : 'da loja';

  const gerenteNome =
    typeof dados.gerente_nome === 'string' &&
    dados.gerente_nome.trim() !== ''
      ? dados.gerente_nome.trim()
      : null;

  // Primeiro nome do gerente: entra no texto de exemplo do campo.
  const primeiroNomeDoGerente = gerenteNome
    ? gerenteNome.split(/\s+/)[0]
    : null;

  // Conversa: da mais antiga para a mais recente (o Chat agrupa por dia).
  const anotacoes = ordenarDaMaisAntigaParaMaisRecente(
    dados.anotacoes_regional ?? [],
  );

  // A autora das anotações é sempre a mesma; usamos a que veio no dado.
  const autora = anotacoes.find(
    (anotacao) =>
      typeof anotacao?.autora === 'string' && anotacao.autora.trim() !== '',
  )?.autora;

  const titulo = `Anotações sobre a loja ${lojaNome}`;

  // Rótulo acessível do log: inclui a autora quando ela é conhecida.
  const rotuloDoLog = autora
    ? `${titulo}, escritas por ${autora}`
    : titulo;

  /*
   * Texto de exemplo: derivado dos dados (loja + primeiro nome do gerente).
   * Sem nome de pessoa fixo no código.
   */
  const placeholder = primeiroNomeDoGerente
    ? `Escreva uma observação sobre a loja e o ${primeiroNomeDoGerente}…`
    : 'Escreva uma observação sobre a loja…';

  const { status: statusEnvio, erro: erroDoEnvio } =
    estado.novaAnotacaoRegional;

  /**
   * Envia a anotação digitada no chat.
   *
   * Recebe o texto (do componente) e devolve a Promise da ação do contexto:
   * true quando gravou. Sem loja selecionada não há o que gravar.
   */
  async function enviarAnotacao(texto) {
    if (!lojaId) {
      return false;
    }

    return adicionarAnotacaoRegional(lojaId, texto);
  }

  return (
    <div className="pagina-anotacoes-regional">
      {/* Orientação no topo, como na aba do gerente. */}
      <p className="pagina-anotacoes-regional__orientacao">
        Escreva aqui o que observar nas visitas à loja. As anotações ficam
        guardadas e entram no feedback para o gerente.
      </p>

      <ChatAnotacoes
        titulo={titulo}
        // O nome alimenta o aviso de vazio; o texto de exemplo é o derivado
        // acima, que cita a loja e o gerente.
        nome={gerenteNome ?? 'a loja'}
        placeholder={placeholder}
        rotuloLog={rotuloDoLog}
        anotacoes={anotacoes}
        aoEnviar={enviarAnotacao}
        enviando={statusEnvio === STATUS.CARREGANDO}
        erroEnvio={erroDoEnvio}
        textoMaximo={ANOTACAO_TEXTO_MAXIMO}
        rotuloAcessivel="Nova anotação da regional"
        idCampo="nova-anotacao-regional"
      />
    </div>
  );
}
