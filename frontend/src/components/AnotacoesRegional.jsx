/**
 * Seção de anotações da regional sobre a liderança da loja.
 *
 * Mostra as observações que a gerente regional registrou nas visitas, da
 * mais recente para a mais antiga. Recebe as anotações por props e não usa o
 * contexto.
 */

import { EstadoVazio } from './EstadoVazio.jsx';
import { formatarData } from '../utilitarios/formatadores.js';
import { ordenarAnotacoes } from '../utilitarios/ordenarAnotacoes.js';

// Importa o CSS desta seção.
import './AnotacoesRegional.css';

/**
 * Componente AnotacoesRegional.
 *
 * Recebe:
 *   anotacoes: lista no formato da API ({ data, autora, texto }).
 *
 * Devolve a seção com título, frase de contexto e a lista de cartões (ou o
 * aviso de vazio). A ordenação reaproveita ordenarAnotacoes: a função só olha
 * o campo "data", então serve tanto para as anotações do gerente quanto para
 * as da regional.
 *
 * Exemplo de uso: <AnotacoesRegional anotacoes={dados.anotacoes_regional} />
 */
export function AnotacoesRegional({ anotacoes }) {
  // A função devolve uma lista NOVA, sem alterar a recebida.
  const ordenadas = ordenarAnotacoes(anotacoes);

  return (
    <section
      className="anotacoes-regional"
      aria-labelledby="titulo-anotacoes-regional"
    >
      <h3
        id="titulo-anotacoes-regional"
        className="anotacoes-regional__titulo"
      >
        Anotações da regional sobre a liderança da loja
      </h3>

      {/*
       * Explica de onde vêm estas anotações e para que servem: são a base do
       * feedback que o próprio gerente precisa receber.
       */}
      <p className="anotacoes-regional__contexto">
        Observações registradas nas visitas à loja. Servem de base para o
        feedback ao gerente.
      </p>

      {ordenadas.length === 0 ? (
        <EstadoVazio
          titulo="Nenhuma anotação da regional"
          descricao="Ainda não há observações registradas nas visitas."
        />
      ) : (
        <ul className="anotacoes-regional__lista">
          {ordenadas.map((anotacao, indice) => (
            /*
             * A chave junta data e posição: mesmo com duas anotações no
             * mesmo dia, cada item tem uma identidade única para o React.
             */
            <li
              key={`${anotacao.data}-${indice}`}
              className="anotacoes-regional__item"
            >
              {/*
               * Cabeçalho do cartão: data (elemento <time>, com a data
               * legível por máquina no atributo dateTime) e autoria.
               */}
              <div className="anotacoes-regional__cabecalho">
                <time
                  className="anotacoes-regional__data"
                  dateTime={anotacao.data}
                >
                  {formatarData(anotacao.data)}
                </time>
                <span className="anotacoes-regional__autora">
                  {anotacao.autora}
                </span>
              </div>

              {/* Texto original, exibido como texto simples (sem HTML). */}
              <p className="anotacoes-regional__texto">{anotacao.texto}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
