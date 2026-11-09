"""Entidades do comparativo entre um vendedor e a média do time.

Cada métrica mostra o valor do vendedor, a média do time (calculada com as
somas de todos, nunca pela média das razões diárias), a diferença percentual,
a posição no ranking e a situação: acima, abaixo ou na média (tolerância de
5% em torno da média).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricaComparada:
    """Uma métrica do vendedor comparada com a média dos vendedores.

    frozen: depois de criada, não pode ser alterada; é um retrato do momento.

    Recebe:
        nome: qual métrica é: "ticket_medio", "pecas_por_atendimento" ou
            "conversao".
        valor: o valor do vendedor (None quando ele não tem dados no período).
        media_time: a média do time no mesmo período (None quando não é
            possível calcular, por exemplo sem vendas).
        diferenca_percentual: (valor - média) ÷ média. Exemplo: -0,20
            significa 20% abaixo da média. None quando não dá para comparar.
        posicao: posição no ranking dos vendedores (1 = melhor). None quando
            o vendedor não entra no ranking por falta de dados.
        total_vendedores: quantos vendedores existem no time considerado.
        situacao: "acima", "abaixo", "na_media" (dentro de ±5% da média) ou
            "indisponivel" quando falta algum valor para comparar.
    """

    nome: str
    valor: float | None
    media_time: float | None
    diferenca_percentual: float | None
    posicao: int | None
    total_vendedores: int
    situacao: str


@dataclass(frozen=True)
class ComparativoTime:
    """As três métricas de um vendedor comparadas com o time.

    Recebe:
        vendedor_id: código do vendedor comparado.
        nome: nome do vendedor.
        metricas: tupla de MetricaComparada (ticket médio, P.A. e conversão).
        mes: mês comparado no formato "AAAA-MM"; None significa todo o
            histórico.
    """

    vendedor_id: str
    nome: str
    metricas: tuple[MetricaComparada, ...]
    mes: str | None

    def para_dict(self) -> dict:
        """Transforma o comparativo em um dicionário simples (para JSON etc.).

        Devolve um dicionário com vendedor_id, nome, mes e uma lista
        "metricas", em que cada item também é um dicionário com os campos da
        MetricaComparada. É útil para uma camada de cima devolver isso como
        resposta de API sem conhecer as dataclasses.

        Exemplo de retorno:
        {
            "vendedor_id": "C0031",
            "nome": "Bianca Rocha",
            "mes": None,
            "metricas": [
                {"nome": "conversao", "valor": 0.505, ...},
                ...
            ],
        }
        """
        return {
            "vendedor_id": self.vendedor_id,
            "nome": self.nome,
            "mes": self.mes,
            "metricas": [
                {
                    "nome": metrica.nome,
                    "valor": metrica.valor,
                    "media_time": metrica.media_time,
                    "diferenca_percentual": metrica.diferenca_percentual,
                    "posicao": metrica.posicao,
                    "total_vendedores": metrica.total_vendedores,
                    "situacao": metrica.situacao,
                }
                for metrica in self.metricas
            ],
        }
