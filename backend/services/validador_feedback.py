"""Validação de qualidade do roteiro de feedback gerado pela IA.

Módulo puro: não acessa rede nem arquivos. Recebe um FeedbackRoteiro já
convertido e devolve uma lista de problemas em português (lista vazia =
aprovado). Validamos porque a IA pode errar ou escorregar em uma regra mesmo
recebendo instruções claras; melhor barrar aqui do que entregar ao gerente um
texto injusto, genérico ou com nome de colega.
"""

import re
from collections.abc import Iterable

from domain.feedback_roteiro import FeedbackRoteiro
from domain.texto import normalizar_nome

# Quantidade mínima e máxima de itens em cada lista do roteiro.
# O roteiro_conversa precisa de mais itens porque é a sequência da conversa.
LIMITES_POR_LISTA = {
    "pontos_positivos": (1, 6),
    "pontos_melhoria": (1, 5),
    "possiveis_motivos": (1, 5),
    "roteiro_conversa": (4, 12),
}

# Cada item precisa ter texto suficiente para ser útil e não pode virar um
# bloco gigante que o gerente não consegue ler na hora da conversa.
TAMANHO_MINIMO_ITEM = 10
TAMANHO_MAXIMO_ITEM = 700

# Pelo menos três perguntas abertas no roteiro (itens que contêm "?").
MINIMO_PERGUNTAS = 3

# Clichês de "texto de robô" vistos nos exemplos ruins do desafio. São
# comparados sem acento e sem diferenciar maiúsculas (normalizar_nome).
# Para ajustar a regra, basta editar esta lista.
FRASES_GENERICAS_PROIBIDAS = (
    "prezado colaborador",
    "multiplas dimensoes",
    "buscar a excelencia",
    "oportunidades de melhoria em",
)


def _trecho(texto: str, limite: int = 60) -> str:
    """Devolve um pedaço curto do texto, em uma linha, para a mensagem.

    Recebe o texto e o tamanho máximo. Junta espaços/quebras em um só espaço
    e corta com "..." quando passa do limite. Serve para identificar o item
    problemático sem repetir o texto inteiro.
    """
    limpo = " ".join(texto.split())
    if len(limpo) <= limite:
        return limpo
    return limpo[:limite].rstrip() + "..."


def _problemas_de_tamanho(nome_lista: str, itens: list[str]) -> list[str]:
    """Confere quantidade e tamanho dos itens de uma lista do roteiro.

    Recebe o nome da lista e os itens. Devolve os problemas encontrados:
    quantidade fora do limite, item curto demais ou longo demais.
    """
    problemas = []
    minimo, maximo = LIMITES_POR_LISTA[nome_lista]
    quantidade = len(itens)

    if quantidade < minimo:
        problemas.append(
            f"{nome_lista}: tem {quantidade} item(ns); o mínimo é {minimo}."
        )
        # Sem itens suficientes, não vale a pena checar o tamanho de cada um.
        return problemas

    if quantidade > maximo:
        problemas.append(
            f"{nome_lista}: tem {quantidade} itens; o máximo é {maximo}."
        )

    for indice, item in enumerate(itens, start=1):
        texto = item.strip()

        if len(texto) < TAMANHO_MINIMO_ITEM:
            problemas.append(
                f"{nome_lista}[{indice}]: item curto "
                f"({len(texto)} caracteres; mínimo {TAMANHO_MINIMO_ITEM}) - "
                f"\"{_trecho(texto)}\"."
            )
        elif len(texto) > TAMANHO_MAXIMO_ITEM:
            problemas.append(
                f"{nome_lista}[{indice}]: item longo "
                f"({len(texto)} caracteres; máximo {TAMANHO_MAXIMO_ITEM}) - "
                f"\"{_trecho(texto)}\"."
            )

    return problemas


def _nomes_bloqueados(
    vendedor_nome: str, nomes_colegas: Iterable[str]
) -> list[tuple[str, str]]:
    """Monta a lista de nomes que não podem aparecer no roteiro.

    Recebe o nome da vendedora e os nomes dos colegas. Devolve pares
    (nome para exibir, nome normalizado para buscar), incluindo o nome
    completo e o primeiro nome de cada colega.

    O nome da própria vendedora não entra. Quando o primeiro nome de um
    colega é igual ao da vendedora, esse primeiro nome é ignorado (não dá
    para saber de quem a IA estava falando), mas o nome completo continua
    bloqueado.
    """
    vendedora = normalizar_nome(vendedor_nome)
    primeiro_da_vendedora = vendedora.split(" ")[0] if vendedora else ""

    bloqueados: list[tuple[str, str]] = []
    vistos: set[str] = set()

    for nome in nomes_colegas:
        completo = normalizar_nome(nome)

        # Ignora vazio, o nome da própria vendedora e repetidos.
        if not completo or completo == vendedora or completo in vistos:
            continue

        vistos.add(completo)
        bloqueados.append((nome, completo))

        primeiro = completo.split(" ")[0]
        if primeiro and primeiro != primeiro_da_vendedora:
            if primeiro not in vistos:
                vistos.add(primeiro)
                # Mostra o primeiro nome com a grafia original do CSV
                # ("Sabrina"), mas busca pelo normalizado ("sabrina").
                primeiro_exibicao = nome.split()[0]
                bloqueados.append((primeiro_exibicao, primeiro))

    return bloqueados


def _problemas_de_nomes(
    roteiro: FeedbackRoteiro,
    vendedor_nome: str,
    nomes_colegas: Iterable[str],
) -> list[str]:
    """Aponta itens que citam colegas pelo nome.

    A busca é feita com expressão regular e \\b (fronteira de palavra) sobre o
    texto normalizado: assim "Ana" não casa dentro de "plano". Reportamos no
    máximo uma ocorrência por colega em cada lista, para não repetir demais.
    """
    problemas = []

    for nome_exibicao, nome_normalizado in _nomes_bloqueados(
        vendedor_nome, nomes_colegas
    ):
        padrao = re.compile(rf"\b{re.escape(nome_normalizado)}\b")

        for nome_lista in LIMITES_POR_LISTA:
            itens = getattr(roteiro, nome_lista)

            for indice, item in enumerate(itens, start=1):
                if padrao.search(normalizar_nome(item)):
                    problemas.append(
                        f"{nome_lista}[{indice}]: cita o colega "
                        f"'{nome_exibicao}' - \"{_trecho(item)}\"."
                    )
                    break

    return problemas


def _problemas_de_perguntas(roteiro: FeedbackRoteiro) -> list[str]:
    """Exige pelo menos três itens com "?" no roteiro da conversa."""
    perguntas = [item for item in roteiro.roteiro_conversa if "?" in item]

    if len(perguntas) >= MINIMO_PERGUNTAS:
        return []

    return [
        "roteiro_conversa: tem "
        f"{len(perguntas)} pergunta(s) com '?'; são necessárias pelo menos "
        f"{MINIMO_PERGUNTAS} perguntas abertas."
    ]


def _problemas_de_frases_genericas(roteiro: FeedbackRoteiro) -> list[str]:
    """Aponta clichês de texto de robô em qualquer lista do roteiro.

    A comparação usa normalizar_nome (sem acento, minúsculas e espaços
    simples), então "Múltiplas Dimensões" também é encontrado.
    """
    problemas = []

    for frase in FRASES_GENERICAS_PROIBIDAS:
        for nome_lista in LIMITES_POR_LISTA:
            itens = getattr(roteiro, nome_lista)

            for indice, item in enumerate(itens, start=1):
                if frase in normalizar_nome(item):
                    problemas.append(
                        f"{nome_lista}[{indice}]: usa a frase genérica "
                        f"\"{frase}\" - \"{_trecho(item)}\"."
                    )
                    break

    return problemas


def validar_roteiro(
    roteiro: FeedbackRoteiro,
    vendedor_nome: str,
    nomes_colegas: Iterable[str],
) -> list[str]:
    """Valida a qualidade do roteiro e devolve os problemas encontrados.

    Recebe o roteiro já convertido, o nome da vendedora (permitido no texto) e
    os nomes dos colegas (proibidos). Devolve uma lista de problemas em
    português; lista vazia significa aprovado.

    Regras: quantidade e tamanho dos itens, nomes de colegas, perguntas
    abertas no roteiro e clichês de texto de robô.

    Exemplo: validar_roteiro(roteiro, "Bianca Rocha", ["Sabrina Alves"])
    devolve [] quando está tudo certo e uma lista com "cita o colega
    'Sabrina'" quando o texto usa esse nome.
    """
    problemas: list[str] = []

    # 1) Quantidade e tamanho dos itens de cada lista.
    for nome_lista in LIMITES_POR_LISTA:
        problemas.extend(
            _problemas_de_tamanho(
                nome_lista, getattr(roteiro, nome_lista)
            )
        )

    # 2) Nomes de colegas (a própria vendedora é permitida).
    problemas.extend(
        _problemas_de_nomes(roteiro, vendedor_nome, nomes_colegas)
    )

    # 3) Perguntas abertas no roteiro da conversa.
    problemas.extend(_problemas_de_perguntas(roteiro))

    # 4) Clichês de texto de robô.
    problemas.extend(_problemas_de_frases_genericas(roteiro))

    return problemas
