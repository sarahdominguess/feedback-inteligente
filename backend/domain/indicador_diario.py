"""Entidade que representa os indicadores de um vendedor em um dia.

Cada linha do arquivo indicadores_diarios_vendedor.csv vira um objeto
IndicadorDiario. Ele só guarda os números do dia; os cálculos de métricas
(ticket médio, P.A., conversão) ficam em outra camada.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class IndicadorDiario:
    """Um dia de trabalho de um vendedor, com os números das vendas.

    dataclass: um molde de objeto que guarda dados, evitando escrever à mão
    o construtor e outras funções básicas.

    frozen: depois de criado, o objeto não pode ser alterado (imutável).
    Isso protege os dados históricos: ninguém muda um dia já registrado.

    Recebe:
        data: o dia a que os números se referem.
        vendedor_id: o código do vendedor (ex.: "C0031").
        valor_vendido: quanto ele vendeu em reais naquele dia.
        vendas: quantas vendas (compras) ele fez no dia.
        pecas: quantas peças de roupa ele vendeu no dia.
        atendimentos: quantas clientes ele atendeu no dia.
    """

    data: date
    vendedor_id: str
    valor_vendido: float
    vendas: int
    pecas: int
    atendimentos: int

    def __post_init__(self):
        """Valida os números logo depois que o objeto é criado.

        __post_init__ é um método especial que a dataclass chama sozinha ao
        final do construtor. Se algum valor for inválido, levantamos
        ValueError (erro de valor) com uma mensagem em português.

        Regra verificada: valor vendido, vendas, peças e atendimentos não
        podem ser negativos. Outras combinações (como peças por venda) serão
        avaliadas quando os dados reais forem lidos, em etapas futuras.
        """
        # Um valor vendido negativo não faz sentido no varejo.
        if self.valor_vendido < 0:
            raise ValueError("O valor vendido não pode ser negativo.")

        # Contagens negativas também não existem: não dá para vender
        # -1 vez nem atender -2 clientes.
        if self.vendas < 0:
            raise ValueError("O número de vendas não pode ser negativo.")
        if self.pecas < 0:
            raise ValueError("O número de peças não pode ser negativo.")
        if self.atendimentos < 0:
            raise ValueError("O número de atendimentos não pode ser negativo.")
