/**
 * Componente que mostra uma mensagem de erro amigável.
 *
 * Recebe só texto já tratado (nunca o objeto de erro) e, se quiser, uma ação
 * para tentar de novo. Não usa contexto, rede nem regra de negócio.
 */

// Ícone de alerta da biblioteca lucide-react (já instalada no projeto).
import { CircleAlert } from 'lucide-react';

// Importa o CSS deste componente.
import './EstadoErro.css';

/**
 * Componente de erro.
 *
 * Um componente é uma função do React que devolve um pedaço da tela.
 * As props (dados recebidos de quem usa) são:
 *   mensagem: texto pronto para o usuário.
 *   aoTentarDeNovo: função opcional chamada quando a pessoa clica no botão.
 *   rotuloBotao: texto do botão (padrão "Tentar de novo").
 *
 * Devolve um bloco com role="alert" (papel que faz o leitor de tela anunciar
 * o conteúdo assim que ele aparece) e o botão apenas quando há ação.
 *
 * Exemplo: <EstadoErro mensagem="Não foi possível conectar." aoTentarDeNovo={carregar} />
 */
export function EstadoErro({
  mensagem,
  aoTentarDeNovo,
  rotuloBotao = 'Tentar de novo',
}) {
  // Só aceitamos texto: se um objeto de erro chegar por engano, ele não é
  // desenhado na tela (o React nem consegue exibir objetos). Assim nenhum
  // detalhe interno, URL ou dado técnico vaza para o usuário.
  const texto =
    typeof mensagem === 'string' && mensagem.trim() !== ''
      ? mensagem
      : 'Não foi possível concluir a operação.';

  // O botão só existe quando quem usa passou uma função de verdade.
  const temAcao = typeof aoTentarDeNovo === 'function';

  return (
    <div className="estado-erro" role="alert">
      {/*
       * Ícone decorativo: aria-hidden="true" evita que o leitor de tela o
       * anuncie, porque o texto ao lado já explica o problema.
       */}
      <span className="estado-erro__icone" aria-hidden="true">
        <CircleAlert />
      </span>

      <div className="estado-erro__conteudo">
        {/*
         * Título fixo, igual para qualquer falha, para a mensagem soar humana
         * e não técnica. Usamos <p> em vez de <h3> para não interferir na
         * ordem de títulos da página.
         */}
        <p className="estado-erro__titulo">Algo não saiu como esperado</p>

        {/* Apenas o texto recebido: nada de stack trace ou dados internos. */}
        <p className="estado-erro__mensagem">{texto}</p>

        {/* Botão opcional: sem ação, nada é desenhado. */}
        {temAcao && (
          <button
            type="button"
            className="ui-botao-primario estado-erro__botao"
            onClick={aoTentarDeNovo}
          >
            {rotuloBotao}
          </button>
        )}
      </div>
    </div>
  );
}
