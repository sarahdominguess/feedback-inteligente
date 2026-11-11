/**
 * Lista lateral de colaboradores da loja.
 *
 * Lê a lista do contexto, deixa a pessoa escolher um colaborador e cuida dos
 * estados de carregamento, erro e vazio. Não navega entre abas nem calcula.
 */

// Ícone de "selecionado" ao lado do nome escolhido.
import { Check } from 'lucide-react';
import { useEffect, useRef } from 'react';

// STATUS: situação da lista; VENDEDOR_FOCO_ID: quem já vem selecionado na demo.
import { STATUS, VENDEDOR_FOCO_ID } from '../constantes.js';
// Hook que entrega o estado global e as ações do AppProvider.
import { useApp } from '../context/useApp.js';
import { EstadoCarregando } from './EstadoCarregando.jsx';
import { EstadoErro } from './EstadoErro.jsx';
import { EstadoVazio } from './EstadoVazio.jsx';

// Importa o CSS deste componente.
import './ListaColaboradores.css';

/**
 * Componente ListaColaboradores.
 *
 * Não recebe props obrigatórias: pega tudo do contexto com o useApp().
 *
 * "Hook" é uma função do React cujo nome começa com "use"; ela dá poderes
 * extras ao componente. O useApp() devolve:
 *   estado.vendedores: { status, dados, erro } da lista da loja;
 *   estado.vendedorSelecionadoId: quem está escolhido agora;
 *   carregarVendedores(): busca a lista na API;
 *   selecionarVendedor(id): escolhe uma pessoa e busca o histórico dela.
 *
 * Devolve a lista de botões (ou o aviso de carregando, erro ou vazio).
 *
 * Exemplo de uso: <ListaColaboradores />
 */
export function ListaColaboradores() {
  const { estado, carregarVendedores, selecionarVendedor } = useApp();

  // Atalho para os três pedaços da lista que interessam aqui.
  const { status, dados, erro } = estado.vendedores;

  // useRef: uma "caixa" que guarda um valor entre renderizações sem fazer a
  // tela se atualizar. Usamos para lembrar se o pedido da lista já saiu.
  const jaPediuLista = useRef(false);

  // useEffect: roda um código depois que a tela aparece.
  //
  // A condição de status evita pedir de novo a cada renderização: assim que
  // o pedido começa, o status deixa de ser "ocioso" e o efeito não repete.
  //
  // Só isso, porém, não segura o StrictMode (modo de desenvolvimento que
  // monta o componente duas vezes de propósito, para revelar efeitos mal
  // feitos): as duas execuções acontecem antes de o novo status chegar à
  // tela. Por isso a caixa jaPediuLista impede a segunda chamada. Resultado:
  // a lista é pedida uma única vez.
  useEffect(() => {
    if (jaPediuLista.current) {
      return;
    }

    // Se outra parte do app já carregou a lista, não pedimos de novo: o
    // estado é compartilhado por toda a aplicação.
    if (status !== STATUS.OCIOSO) {
      return;
    }

    jaPediuLista.current = true;
    carregarVendedores();
  }, [status, carregarVendedores]);

  // Segundo efeito: quando a lista chega e ninguém está selecionado, escolhe
  // a Bianca (VENDEDOR_FOCO_ID) se ela estiver na lista. É uma conveniência
  // do cenário da demo; se ela não estiver lá, ninguém é selecionado.
  useEffect(() => {
    if (status !== STATUS.SUCESSO) {
      return;
    }

    if (estado.vendedorSelecionadoId) {
      return;
    }

    const temFoco = dados.some(
      (vendedor) => vendedor.vendedor_id === VENDEDOR_FOCO_ID,
    );

    if (!temFoco) {
      return;
    }

    selecionarVendedor(VENDEDOR_FOCO_ID);
  }, [status, dados, estado.vendedorSelecionadoId, selecionarVendedor]);

  return (
    <div className="lista-colaboradores">
      {/* Erro: mostra o texto vindo do estado e permite tentar de novo. */}
      {status === STATUS.ERRO && (
        <EstadoErro
          mensagem={erro}
          aoTentarDeNovo={() => carregarVendedores()}
        />
      )}

      {/* Ainda não pedimos (ocioso) ou o pedido está em andamento. */}
      {(status === STATUS.OCIOSO || status === STATUS.CARREGANDO) && (
        <EstadoCarregando
          titulo="Carregando colaboradores…"
          linhas={4}
          variante="texto"
        />
      )}

      {/* Deu certo, mas a loja não devolveu ninguém. */}
      {status === STATUS.SUCESSO && dados.length === 0 && (
        <EstadoVazio
          titulo="Nenhum colaborador encontrado"
          descricao="Não há colaboradores para mostrar nesta loja agora."
        />
      )}

      {/* Deu certo: um botão por colaborador, na ordem recebida da API. */}
      {status === STATUS.SUCESSO && dados.length > 0 && (
        <ul
          className="lista-colaboradores__itens"
          aria-label="Colaboradores da loja"
        >
          {dados.map((vendedor) => {
            const selecionado =
              vendedor.vendedor_id === estado.vendedorSelecionadoId;

            return (
              <li key={vendedor.vendedor_id}>
                {/*
                 * <button> nativo já é navegável por Tab e aciona com Enter
                 * ou Espaço: não precisamos de código extra para teclado.
                 */}
                <button
                  type="button"
                  className={
                    selecionado
                      ? 'lista-colaboradores__item lista-colaboradores__item--selecionado'
                      : 'lista-colaboradores__item'
                  }
                  /*
                   * aria-current avisa o leitor de tela qual item é o atual
                   * da lista. Só entra no item selecionado.
                   */
                  aria-current={selecionado ? 'true' : undefined}
                  onClick={() => selecionarVendedor(vendedor.vendedor_id)}
                >
                  <span className="lista-colaboradores__texto">
                    <span className="lista-colaboradores__nome">
                      {vendedor.nome}
                    </span>
                    <span className="lista-colaboradores__cargo">
                      {vendedor.cargo}
                    </span>
                  </span>

                  {/*
                   * Marca de seleção: além da cor, o ícone e a borda mostram
                   * qual é o item atual. aria-hidden porque o aria-current
                   * acima já informa isso ao leitor de tela.
                   */}
                  {selecionado && (
                    <span
                      className="lista-colaboradores__marca"
                      aria-hidden="true"
                    >
                      <Check />
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
