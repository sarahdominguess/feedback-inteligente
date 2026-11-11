"""Entidade que representa uma anotação da gerente regional.

Cada linha do arquivo anotacoes_regional.csv vira um objeto AnotacaoRegional.
São observações que a regional (Patrícia) registra sobre as lojas — atritos,
elogios, combinados — e que alimentam a visão executiva da Etapa 3.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AnotacaoRegional:
    """Uma anotação da gerente regional sobre uma loja ou sobre o time.

    frozen: depois de criada, a anotação não pode ser alterada. Ela é um
    registro histórico do que a regional escreveu, então deve permanecer
    exatamente como foi lida do CSV.

    Recebe:
        data: o dia em que a anotação foi feita.
        autora: quem escreveu (ex.: "Patrícia Lemos").
        texto: o que foi escrito, do jeito que foi digitado.

    Exemplo: AnotacaoRegional(
        data=date(2026, 10, 20),
        autora="Patrícia Lemos",
        texto="Conversar com o Diego sobre a escala de sábado.",
    )
    """

    data: date
    autora: str
    texto: str
