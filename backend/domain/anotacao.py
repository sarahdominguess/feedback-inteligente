"""Entidade que representa uma anotação solta do gerente.

Cada linha do arquivo anotacoes_gerente.csv vira um objeto Anotacao. Essas
anotações trazem o contexto que os números sozinhos não mostram (férias, chuva,
reforma da loja) e serão usadas para preparar o feedback.
"""

from dataclasses import dataclass
from datetime import date

from config import ANOTACAO_SOBRE_TIME


@dataclass(frozen=True)
class Anotacao:
    """Uma anotação do gerente sobre uma pessoa ou sobre o time.

    frozen: depois de criada, a anotação não pode ser alterada; é um registro
    histórico do que o gerente escreveu.

    Recebe:
        data: o dia em que a anotação foi feita.
        sobre: o nome da pessoa (ex.: "Bianca Rocha") ou o texto "(time)"
            quando a anotação vale para a equipe inteira.
        texto: o que foi escrito, do jeito que o gerente digitou.
    """

    data: date
    sobre: str
    texto: str

    @property
    def e_do_time(self) -> bool:
        """Diz se a anotação é sobre o time inteiro, e não sobre uma pessoa.

        Devolve True quando "sobre" é igual à constante ANOTACAO_SOBRE_TIME
        (o texto "(time)"), e False nos demais casos.

        Exemplo: uma anotação com sobre="(time)" devolve True; com
        sobre="Bianca Rocha" devolve False.
        """
        return self.sobre == ANOTACAO_SOBRE_TIME
