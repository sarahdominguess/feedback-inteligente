"""Entidade que representa o gerente e as anotações que ele escreveu.

Gerente guarda a identidade e as anotações soltas (sobre pessoas ou sobre o
time). A busca por nome é tolerante a acentos, maiúsculas e espaços, mas evita
misturar duas pessoas diferentes que tenham o mesmo primeiro nome.
"""

from collections.abc import Iterable

from domain.anotacao import Anotacao
from domain.texto import nome_corresponde, normalizar_nome


class Gerente:
    """Pessoa que lidera a loja e registra anotações sobre o time.

    Recebe:
        gerente_id: código único da pessoa (ex.: "C0030").
        nome: nome completo (ex.: "Diego Furtado").
        loja_id: código da loja (ex.: "L004").
        loja_nome: nome da loja.
        anotacoes: coleção de Anotacao. Internamente vira uma tupla ordenada
            por data (registro histórico não pode ser alterado de fora).
    """

    def __init__(
        self,
        gerente_id: str,
        nome: str,
        loja_id: str,
        loja_nome: str,
        anotacoes: Iterable[Anotacao],
    ):
        """Guarda a identidade e copia as anotações para dentro do objeto."""
        # Identidade em atributos privados (o "_" é uma convenção de "uso
        # interno"); o mundo externo lê pelas propriedades somente leitura.
        self._gerente_id = gerente_id
        self._nome = nome
        self._loja_id = loja_id
        self._loja_nome = loja_nome

        # tuple(...) copia as anotações para uma tupla imutável e sorted(...)
        # coloca em ordem cronológica. Mexer na lista original depois não
        # altera o Gerente.
        self._anotacoes = tuple(
            sorted(anotacoes, key=lambda anotacao: anotacao.data)
        )

    @property
    def gerente_id(self) -> str:
        """Código único do gerente (ex.: "C0030"). Somente leitura."""
        return self._gerente_id

    @property
    def nome(self) -> str:
        """Nome completo do gerente. Somente leitura."""
        return self._nome

    @property
    def loja_id(self) -> str:
        """Código da loja do gerente (ex.: "L004"). Somente leitura."""
        return self._loja_id

    @property
    def loja_nome(self) -> str:
        """Nome da loja do gerente. Somente leitura."""
        return self._loja_nome

    def anotacoes(self) -> tuple[Anotacao, ...]:
        """Devolve todas as anotações em ordem cronológica.

        A tupla é imutável: não há como adicionar, remover ou trocar itens
        pela API pública.
        """
        return self._anotacoes

    def anotacoes_sobre(self, nome: str) -> tuple[Anotacao, ...]:
        """Busca as anotações que falam de uma pessoa.

        Aceita o nome completo ("Bianca Rocha") ou só o primeiro nome
        ("Bianca"), sem diferenciar acentos, maiúsculas ou espaços extras.
        Anotações sobre o time ("(time)") nunca entram no resultado.

        Regra de ambiguidade: se o termo casar com mais de uma pessoa
        diferente (ex.: "Ana" para "Ana Silva" e "Ana Souza"), só vale a
        correspondência exata do nome completo; se nenhuma pessoa tiver
        exatamente esse nome, devolve uma tupla vazia.

        Devolve as anotações em ordem cronológica.
        """
        # Normalizamos o termo buscado para comparar no mesmo padrão dos nomes.
        termo = normalizar_nome(nome)
        if not termo:
            return ()

        # Conjunto de pessoas distintas que têm anotação (fora as do time).
        # Usamos a versão normalizada do nome para juntar variações de escrita.
        pessoas = {
            normalizar_nome(anotacao.sobre)
            for anotacao in self._anotacoes
            if not anotacao.e_do_time
        }

        # nome_corresponde é compartilhada com o DataLoader: aceita nome
        # completo ou primeiro nome (termo de uma palavra só).
        encontradas = {
            pessoa for pessoa in pessoas if nome_corresponde(pessoa, termo)
        }

        # Mais de uma pessoa distinta: a busca é ambígua. Nesse caso, mantemos
        # apenas quem tem exatamente o nome completo informado.
        if len(encontradas) > 1:
            encontradas = {pessoa for pessoa in encontradas if pessoa == termo}

        # Sem ninguém (ou ambiguidade sem correspondência exata): vazio.
        if not encontradas:
            return ()

        # Filtramos as anotações dessas pessoas, mantendo a ordem cronológica
        # e deixando de fora as anotações do time.
        return tuple(
            anotacao
            for anotacao in self._anotacoes
            if not anotacao.e_do_time
            and normalizar_nome(anotacao.sobre) in encontradas
        )

    def anotacoes_do_time(self) -> tuple[Anotacao, ...]:
        """Devolve só as anotações sobre o time inteiro, em ordem cronológica.

        São as anotações cujo "sobre" é "(time)", identificadas pela
        propriedade e_do_time da entidade Anotacao.
        """
        return tuple(
            anotacao for anotacao in self._anotacoes if anotacao.e_do_time
        )

    def total_anotacoes(self) -> int:
        """Conta todas as anotações, incluindo as do time."""
        return len(self._anotacoes)
