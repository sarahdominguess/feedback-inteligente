"""Script de teste manual da integração real com a DeepSeek.

Rode a partir de backend/ (com o venv ativo):

    python -m scripts.testar_deepseek --mostrar-prompt
    python -m scripts.testar_deepseek --listar-modelos
    python -m scripts.testar_deepseek --vendedor Bianca

O script nunca imprime a chave da API nem o conteúdo do arquivo .env. A opção
--mostrar-prompt não usa rede e nem exige chave; as outras usam a API real e
consomem créditos.
"""

import argparse
import json
import sys

from domain.excecoes import DominioError, VendedorNaoEncontradoError
from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.prompt_feedback import montar_mensagens


def _mes_valido(valor: str) -> str:
    """Valida o argumento --mes no formato "AAAA-MM".

    Recebe o texto digitado e devolve o mesmo texto quando está correto.
    Se estiver errado, levanta ArgumentTypeError para o argparse mostrar uma
    mensagem clara, em vez de deixar o erro estourar mais adiante.
    """
    try:
        ano, mes = valor.split("-")
        if len(ano) == 4 and ano.isdigit() and 1 <= int(mes) <= 12:
            return valor
    except (ValueError, AttributeError):
        pass

    raise argparse.ArgumentTypeError(
        "Use o formato AAAA-MM, por exemplo 2026-10."
    )


def _buscar_vendedor(loader: DataLoader, termo: str):
    """Busca o vendedor por ID ("C0031") ou por nome/primeiro nome ("Bianca").

    Recebe o DataLoader e o texto digitado. Primeiro tenta como ID (em
    maiúsculas, porque os IDs do CSV são assim); se não achar, tenta pelo
    nome. Devolve o Vendedor encontrado ou deixa subir
    VendedorNaoEncontradoError com a mensagem em português.
    """
    try:
        return loader.obter_vendedor(termo.strip().upper())
    except VendedorNaoEncontradoError:
        # Não era um ID válido; agora buscamos pelo nome, aceitando o
        # primeiro nome (ex.: "Bianca" encontra "Bianca Rocha").
        return loader.buscar_vendedor_por_nome(termo)


def _imprimir_prompt(loader: DataLoader, vendedor, mes_referencia):
    """Imprime as mensagens de sistema e de usuário, sem chamar a API.

    Monta o mesmo prompt que o LLMService usaria, para você conferir o texto
    e os dados enviados antes de gastar créditos.
    """
    comparativo = loader.obter_comparativo_time(
        vendedor.vendedor_id, mes_referencia
    )
    gerente = loader.obter_gerente()

    mensagens = montar_mensagens(
        vendedor=vendedor,
        comparativo=comparativo,
        anotacoes_do_vendedor=loader.obter_anotacoes_do_vendedor(
            vendedor.vendedor_id
        ),
        anotacoes_do_time=gerente.anotacoes_do_time(),
        gerente_nome=gerente.nome,
        loja_nome=gerente.loja_nome,
        mes_referencia=mes_referencia,
    )

    for mensagem in mensagens:
        print(f"===== {mensagem['role'].upper()} =====")
        print(mensagem["content"])
        print()


def _listar_modelos(loader: DataLoader):
    """Lista os ids de modelo disponíveis na conta da DeepSeek.

    Usa o mesmo caminho de configuração do LLMService (ler o .env e criar o
    cliente preguiçosamente). Chamamos o método interno de propósito: assim a
    leitura da chave fica em um lugar só e o script não duplica essa lógica.
    """
    servico = LLMService(data_loader=loader)
    cliente = servico._obter_cliente()

    modelos = cliente.models.list()

    # Imprimimos só o id: é o valor que vai em DEEPSEEK_MODEL.
    for modelo in modelos.data:
        print(modelo.id)


def _imprimir_resumo(roteiro):
    """Imprime as quatro seções do roteiro de forma legível.

    Recebe o FeedbackRoteiro devolvido pela IA (já validado) e mostra cada
    lista numerada, para facilitar a leitura no terminal.
    """
    secoes = (
        ("Pontos positivos", "pontos_positivos"),
        ("Pontos de melhoria", "pontos_melhoria"),
        ("Possíveis motivos", "possiveis_motivos"),
        ("Roteiro da conversa", "roteiro_conversa"),
    )

    print("RESUMO DO ROTEIRO")
    for titulo, atributo in secoes:
        itens = getattr(roteiro, atributo)
        print(f"\n{titulo} ({len(itens)}):")
        for indice, item in enumerate(itens, start=1):
            print(f"  {indice}. {item}")


def main(argv=None) -> int:
    """Executa o script e devolve o código de saída (0 = sucesso, 1 = erro).

    Recebe a lista de argumentos (None usa a linha de comando). Erros de
    domínio viram mensagem amigável em português, sem traceback.
    """
    parser = argparse.ArgumentParser(
        description="Testa a integração real com a DeepSeek."
    )
    parser.add_argument(
        "--vendedor",
        default="Bianca",
        help="nome, primeiro nome ou ID do vendedor (padrão: Bianca)",
    )
    parser.add_argument(
        "--mes",
        type=_mes_valido,
        default=None,
        help="mês de referência no formato AAAA-MM (padrão: todo o histórico)",
    )
    parser.add_argument(
        "--mostrar-prompt",
        action="store_true",
        help="imprime o prompt montado e sai, sem chamar a API",
    )
    parser.add_argument(
        "--listar-modelos",
        action="store_true",
        help="lista os ids de modelo disponíveis na conta (exige chave)",
    )

    args = parser.parse_args(argv)
    loader = DataLoader()

    try:
        # 1) Mostrar o prompt não toca em rede nem exige chave da API.
        if args.mostrar_prompt:
            vendedor = _buscar_vendedor(loader, args.vendedor)
            _imprimir_prompt(loader, vendedor, args.mes)
            return 0

        # 2) Listar modelos exige chave, mas não precisa de vendedor.
        if args.listar_modelos:
            _listar_modelos(loader)
            return 0

        # 3) Caminho padrão: gera o roteiro de verdade (consome créditos).
        vendedor = _buscar_vendedor(loader, args.vendedor)
        servico = LLMService(data_loader=loader)
        roteiro = servico.gerar_roteiro_feedback(
            vendedor.vendedor_id, args.mes
        )

        # JSON bonito para copiar/inspecionar e um resumo para leitura rápida.
        print(json.dumps(roteiro.para_dict(), ensure_ascii=False, indent=2))
        print()
        _imprimir_resumo(roteiro)
        return 0

    except DominioError as erro:
        # Erros previstos (chave ausente, vendedor não encontrado, resposta
        # inválida etc.) mostram só a mensagem em português, sem traceback.
        print(f"Erro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
