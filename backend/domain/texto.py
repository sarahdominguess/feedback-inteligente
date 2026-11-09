"""Utilidades de texto compartilhadas pelo domínio.

Por enquanto há só a normalização de nomes, usada para comparar nomes de
pessoas mesmo quando vêm com acento, letras maiúsculas ou espaços extras
(ex.: "  Patrícia   Lemos " e "patricia lemos" devem ser tratados como iguais).
"""

import unicodedata


def normalizar_nome(texto: str) -> str:
    """Deixa um nome num formato simples para comparação.

    O que faz, passo a passo:
    1. Remove espaços das pontas e troca espaços repetidos por um só.
    2. Remove acentos (á → a, ç → c, ã → a...).
    3. Converte tudo para minúsculas com casefold (versão mais completa do
       que o lower() para comparar textos).

    Recebe: o texto original (ex.: "  Patrícia   Lemos ").
    Devolve: o texto normalizado (ex.: "patricia lemos").

    Exemplo: normalizar_nome("JOÃO  da Silva") devolve "joao da silva".
    """
    # 1) split() sem argumento separa o texto em palavras por qualquer
    # sequência de espaços; " ".join(...) remonta com um espaço só entre elas.
    sem_espacos_extras = " ".join(texto.split())

    # 2) unicodedata.normalize("NFD", ...) separa cada letra do seu acento.
    # O acento vira um caractere da categoria "Mn" (marca não espaçante), que
    # descartamos com o if. Assim "á" vira "a" + acento e sobra só o "a".
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", sem_espacos_extras)
        if unicodedata.category(caractere) != "Mn"
    )

    # 3) casefold() deixa todas as letras minúsculas para a comparação.
    return sem_acentos.casefold()


def nome_corresponde(nome_completo: str, termo: str) -> bool:
    """Diz se um nome corresponde ao termo buscado.

    Recebe o nome completo de uma pessoa e o termo digitado (ambos como texto
    normal; a função normaliza os dois). Aceita duas formas:
    - nome completo igual ao termo (ex.: "Bianca Rocha" com "bianca rocha");
    - primeiro nome igual ao termo, quando o termo tem uma palavra só
      (ex.: "Bianca Rocha" com "Bianca").

    Exemplo: nome_corresponde("Bianca Rocha", "BIANCA") devolve True;
    nome_corresponde("Bianca Rocha", "Rocha") devolve False.
    """
    nome_normalizado = normalizar_nome(nome_completo)
    termo_normalizado = normalizar_nome(termo)

    if nome_normalizado == termo_normalizado:
        return True

    # Só comparamos o primeiro nome quando o termo tem uma palavra; assim
    # "Bianca Rocha" não casa por prefixo com outro nome composto.
    if " " not in termo_normalizado:
        primeiro_nome = nome_normalizado.split(" ", 1)[0]
        return primeiro_nome == termo_normalizado

    return False
