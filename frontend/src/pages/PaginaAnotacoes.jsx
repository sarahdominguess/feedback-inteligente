/**
 * Página da aba Anotações do colaborador selecionado.
 *
 * Mostra o que o gerente escreveu sobre a pessoa e sobre o time, do jeito
 * que escreveu. Lê estado.detalhes; não edita, não resume e não calcula.
 */

import { STATUS } from '../constantes.js';
import { useApp } from '../context/useApp.js';
import { EstadoCarregando } from '../components/EstadoCarregando.jsx';
import { EstadoErro } from '../components/EstadoErro.jsx';
import { EstadoVazio } from '../components/EstadoVazio.jsx';
import { formatarData } from '../utilitarios/formatadores.js';
import { ordenarAnotacoes } from '../utilitarios/ordenarAnotacoes.js';

// Importa o CSS desta página.
import './PaginaAnotacoes.css';

/**
 * Monta a lista visual de anotações.
 *
 * Recebe a lista JÁ ordenada e devolve os itens com data e texto. O texto é
 * exibido como texto simples do React — nunca é interpretado como HTML.
 *
 * O <time> é o elemento que representa uma data. O atributo dateTime guarda
 * a data legível por máquina ("2026-10-08") enquanto o que aparece na tela é
 * o formato brasileiro ("08/10/2026").
 */
function listaDeAnotacoes(anotacoes) {
  return (
    <ul className="pagina-anotacoes__lista">
      {anotacoes.map((anotacao, indice) => (
        /*
         * A chave junta data e posição: mesmo com duas anotações no mesmo
         * dia, cada item continua tendo uma identidade única para o React.
         */
        <li
          key={`${anotacao.data}-${indice}`}
          className="pagina-anotacoes__item"
        >
          <time className="pagina-anotacoes__data" dateTime={anotacao.data}>
            {formatarData(anotacao.data)}
          </time>

          {/* Texto original, sem cortes, sem resumo e sem HTML. */}
          <p className="pagina-anotacoes__texto">{anotacao.texto}</p>
        </li>
      ))}
    </ul>
  );
}

/**
 * Componente PaginaAnotacoes.
 *
 * Não recebe props: lê do contexto o histórico (estado.detalhes), o
 * vendedor selecionado e a ação selecionarVendedor (para "tentar de novo").
 *
 * Devolve uma orientação fixa e duas seções: anotações sobre a pessoa e
 * anotações sobre o time, ambas da mais recente para a mais antiga.
 *
 * Exemplo de uso: <PaginaAnotacoes />
 */
export function PaginaAnotacoes() {
  const { estado, selecionarVendedor } = useApp();

  const { status, dados, erro } = estado.detalhes;
  const vendedorId = estado.vendedorSelecionadoId;

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
        descricao="Escolha um colaborador na lista para ver as anotações."
      />
    );
  }

  // Nome para o título da seção; se faltar, usamos uma expressão genérica.
  const nome =
    typeof dados.nome === 'string' && dados.nome.trim() !== ''
      ? dados.nome
      : 'o colaborador';

  // Cada seção tem a sua própria ordenação (mais recente primeiro).
  const anotacoesDaPessoa = ordenarAnotacoes(dados.anotacoes ?? []);
  const anotacoesDoTime = ordenarAnotacoes(dados.anotacoes_do_time ?? []);

  return (
    <div className="pagina-anotacoes">
      {/*
       * Texto fixo de orientação. Não promete nada além do que o sistema
       * faz: o roteiro é montado a partir destas anotações e dos números.
       */}
      <p className="pagina-anotacoes__orientacao">
        Estas são as suas anotações originais. O roteiro de feedback usa o
        que está escrito aqui, junto com os números.
      </p>

      {/* ---------- Anotações sobre a pessoa ---------- */}
      <section
        className="pagina-anotacoes__secao"
        aria-labelledby="titulo-anotacoes-pessoa"
      >
        <h2
          id="titulo-anotacoes-pessoa"
          className="pagina-anotacoes__titulo"
        >
          Anotações sobre {nome}
        </h2>

        {anotacoesDaPessoa.length === 0 ? (
          <EstadoVazio
            titulo="Nenhuma anotação"
            descricao="Ainda não há anotações sobre esta pessoa."
          />
        ) : (
          listaDeAnotacoes(anotacoesDaPessoa)
        )}
      </section>

      {/* ---------- Anotações sobre o time ---------- */}
      <section
        className="pagina-anotacoes__secao"
        aria-labelledby="titulo-anotacoes-time"
      >
        <h2 id="titulo-anotacoes-time" className="pagina-anotacoes__titulo">
          Anotações sobre o time
        </h2>

        {/*
         * Explica por que estas anotações aparecem aqui: são da loja toda e
         * servem de contexto para a conversa com a pessoa.
         */}
        <p className="pagina-anotacoes__explicacao">
          São observações sobre a loja toda e podem ajudar a entender o
          contexto da conversa.
        </p>

        {anotacoesDoTime.length === 0 ? (
          <EstadoVazio
            titulo="Nenhuma anotação do time"
            descricao="Ainda não há observações sobre a loja toda."
          />
        ) : (
          listaDeAnotacoes(anotacoesDoTime)
        )}
      </section>
    </div>
  );
}
