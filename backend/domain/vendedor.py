"""Entidade que representa um vendedor e calcula as métricas do seu histórico.

Vendedor junta identidade, indicadores diários e metas mensais. As métricas são
sempre calculadas a partir das somas do período (nunca pela média das razões
diárias), e as coleções internas são protegidas contra alterações externas.
"""

from collections.abc import Iterable, Mapping
from datetime import date

from domain.indicador_diario import IndicadorDiario


def _mes_de(data: date) -> str:
    """Devolve o mês de uma data no formato "AAAA-MM" (ex.: "2026-08").

    Esse formato é usado como chave para filtrar indicadores e buscar metas.
    O mês recebe dois dígitos ("08" em vez de "8") para a ordem alfabética
    coincidir com a ordem cronológica.
    """
    return f"{data.year:04d}-{data.month:02d}"


class Vendedor:
    """Pessoa da loja com seu histórico de vendas e metas.

    Recebe:
        vendedor_id: código único da pessoa (ex.: "C0031").
        nome: nome completo (ex.: "Bianca Rocha").
        cargo: "vendedor" ou "gerente".
        loja_id: código da loja (ex.: "L004").
        loja_nome: nome da loja.
        indicadores: coleção de IndicadorDiario (um por dia trabalhado).
            Pode vir como lista; internamente vira uma tupla ordenada.
        metas: dicionário opcional "AAAA-MM" → meta em reais. Quando None
            (caso do gerente, que não tem meta individual), fica vazio.

    As coleções nunca são expostas de forma alterável: os indicadores são
    guardados numa tupla (imutável) e as metas são devolvidas como cópia.
    """

    def __init__(
        self,
        vendedor_id: str,
        nome: str,
        cargo: str,
        loja_id: str,
        loja_nome: str,
        indicadores: Iterable[IndicadorDiario],
        metas: Mapping[str, float] | None = None,
    ):
        """Guarda a identidade e copia os dados para dentro do objeto."""
        # A identidade fica em atributos privados (o "_" na frente é uma
        # convenção: "uso interno da classe"). O mundo externo lê pelas
        # propriedades somente leitura definidas mais abaixo.
        self._vendedor_id = vendedor_id
        self._nome = nome
        self._cargo = cargo
        self._loja_id = loja_id
        self._loja_nome = loja_nome

        # tuple(...) copia os indicadores para uma tupla imutável. sorted(...)
        # ordena por data, então o histórico fica em ordem cronológica mesmo
        # que a lista recebida esteja fora de ordem. Assim, alterar a lista
        # original depois de criar o Vendedor não muda o que está guardado.
        self._indicadores = tuple(
            sorted(indicadores, key=lambda indicador: indicador.data)
        )

        # dict(...) faz uma cópia das metas. Sem a cópia, alguém poderia mudar
        # o dicionário original e alterar o Vendedor sem querer.
        self._metas = dict(metas) if metas is not None else {}

    @property
    def vendedor_id(self) -> str:
        """Código único da pessoa (ex.: "C0031"). Somente leitura."""
        return self._vendedor_id

    @property
    def nome(self) -> str:
        """Nome completo da pessoa. Somente leitura."""
        return self._nome

    @property
    def cargo(self) -> str:
        """Cargo da pessoa: "vendedor" ou "gerente". Somente leitura."""
        return self._cargo

    @property
    def loja_id(self) -> str:
        """Código da loja da pessoa (ex.: "L004"). Somente leitura."""
        return self._loja_id

    @property
    def loja_nome(self) -> str:
        """Nome da loja da pessoa. Somente leitura."""
        return self._loja_nome

    @property
    def indicadores(self) -> tuple[IndicadorDiario, ...]:
        """Histórico de indicadores como tupla ordenada por data.

        Devolvemos a própria tupla porque tuplas são imutáveis: não existe
        método público para adicionar, remover ou trocar itens.
        """
        return self._indicadores

    @property
    def metas(self) -> dict[str, float]:
        """Cópia do dicionário de metas ("AAAA-MM" → valor em reais).

        Devolvemos uma cópia (dict(...)) para que alterar o dicionário
        recebido não altere as metas guardadas no Vendedor.
        """
        return dict(self._metas)

    def _indicadores_do_mes(
        self, mes: str | None
    ) -> tuple[IndicadorDiario, ...]:
        """Filtra os indicadores de um mês; com mes=None, devolve todos.

        Recebe o mês no formato "AAAA-MM". Se o mês não tiver registros,
        devolve uma tupla vazia (e não um erro).
        """
        if mes is None:
            return self._indicadores

        # Percorremos o histórico e mantemos só os dias cujo mês é o pedido.
        return tuple(
            indicador
            for indicador in self._indicadores
            if _mes_de(indicador.data) == mes
        )

    def valor_vendido(self, mes: str | None = None) -> float:
        """Soma o valor vendido em reais no período.

        Com mes=None, soma todo o histórico. Sem registros no período,
        devolve 0.0.
        """
        total = 0.0
        for indicador in self._indicadores_do_mes(mes):
            total += indicador.valor_vendido
        return total

    def vendas(self, mes: str | None = None) -> int:
        """Soma o número de vendas no período (0 se não houver registros)."""
        total = 0
        for indicador in self._indicadores_do_mes(mes):
            total += indicador.vendas
        return total

    def pecas(self, mes: str | None = None) -> int:
        """Soma o número de peças vendidas no período."""
        total = 0
        for indicador in self._indicadores_do_mes(mes):
            total += indicador.pecas
        return total

    def atendimentos(self, mes: str | None = None) -> int:
        """Soma o número de clientes atendidas no período."""
        total = 0
        for indicador in self._indicadores_do_mes(mes):
            total += indicador.atendimentos
        return total

    def ticket_medio(self, mes: str | None = None) -> float | None:
        """Ticket médio = valor vendido ÷ número de vendas.

        Devolve None quando não há vendas (divisão por zero seria um erro) ou
        quando não há registros no período.

        Exemplo: valor vendido de 400 e 3 vendas → 400 ÷ 3 ≈ 133,33.
        """
        total_vendas = self.vendas(mes)
        if total_vendas == 0:
            return None
        return self.valor_vendido(mes) / total_vendas

    def pecas_por_atendimento(self, mes: str | None = None) -> float | None:
        """P.A. (peças por atendimento) = peças ÷ número de vendas.

        Devolve None quando não há vendas no período.

        Exemplo: 6 peças e 5 vendas → 6 ÷ 5 = 1,2 peças por venda.
        """
        total_vendas = self.vendas(mes)
        if total_vendas == 0:
            return None
        return self.pecas(mes) / total_vendas

    def conversao(self, mes: str | None = None) -> float | None:
        """Conversão = vendas ÷ atendimentos, como fração de 0 a 1.

        Devolve None quando não há atendimentos no período. A conversão em
        porcentagem (0,375 → 37,5%) é responsabilidade das camadas de cima.

        Exemplo: 3 vendas em 8 atendimentos → 3 ÷ 8 = 0,375.
        """
        total_atendimentos = self.atendimentos(mes)
        if total_atendimentos == 0:
            return None
        return self.vendas(mes) / total_atendimentos

    def meta_do_mes(self, mes: str) -> float | None:
        """Devolve a meta do mês em reais, ou None se não houver meta.

        O gerente não tem meta individual, então para ele este método
        devolve None em todos os meses.
        """
        return self._metas.get(mes)

    def atingimento_meta(self, mes: str) -> float | None:
        """Atingimento da meta = valor vendido no mês ÷ meta do mês.

        Devolve None quando não há meta cadastrada ou quando a meta é zero.
        O resultado é uma fração: 1.12 significa 112% da meta.
        """
        meta = self.meta_do_mes(mes)
        if meta is None or meta == 0:
            return None
        return self.valor_vendido(mes) / meta

    def meses_com_dados(self) -> tuple[str, ...]:
        """Lista os meses ("AAAA-MM") que têm pelo menos um registro.

        Devolve uma tupla ordenada, sem meses repetidos.
        """
        # set() remove os meses repetidos; sorted() coloca em ordem crescente.
        meses = {_mes_de(indicador.data) for indicador in self._indicadores}
        return tuple(sorted(meses))

    def dias_com_dados(self, mes: str) -> int:
        """Conta quantos registros existem no mês informado.

        Serve para sinalizar mês parcial: por exemplo, novembro de 2026 tem
        apenas 1 dia nos dados, então não deve ser comparado com um mês cheio.
        """
        return len(self._indicadores_do_mes(mes))

    def resumo_mensal(self) -> list[dict]:
        """Monta um resumo com as métricas de cada mês que tem registros.

        Devolve uma lista de dicionários, um por mês em ordem crescente, com:
        mes, dias_com_dados, valor_vendido, vendas, pecas, atendimentos,
        ticket_medio, pecas_por_atendimento, conversao, meta e
        atingimento_meta.
        """
        resumo = []

        for mes in self.meses_com_dados():
            # Cada dicionário é novo; os valores vêm dos métodos acima, que
            # sempre recalculam a partir das somas do mês.
            resumo.append(
                {
                    "mes": mes,
                    "dias_com_dados": self.dias_com_dados(mes),
                    "valor_vendido": self.valor_vendido(mes),
                    "vendas": self.vendas(mes),
                    "pecas": self.pecas(mes),
                    "atendimentos": self.atendimentos(mes),
                    "ticket_medio": self.ticket_medio(mes),
                    "pecas_por_atendimento": self.pecas_por_atendimento(mes),
                    "conversao": self.conversao(mes),
                    "meta": self.meta_do_mes(mes),
                    "atingimento_meta": self.atingimento_meta(mes),
                }
            )

        return resumo
