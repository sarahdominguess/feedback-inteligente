"""Entidade que registra um roteiro de feedback já preparado.

Cada vez que a IA gera um roteiro, guardamos um RegistroFeedback com quem foi,
quando e o conteúdo das quatro listas. Assim a visão da regional consegue
saber para quais vendedores já existe um preparo.

Vocabulário: o sistema registra apenas que o roteiro foi GERADO. Ele não sabe
se a conversa aconteceu, então nada aqui deve ser chamado de "realizado".
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class RegistroFeedback:
    """Um roteiro gerado, com identificador, pessoa, data e conteúdo.

    Recebe:
        vendedor_id: código da pessoa (ex.: "C0031").
        vendedor_nome: nome completo (ex.: "Bianca Rocha").
        gerado_em: data e hora em que o roteiro foi preparado, COM fuso
            horário. Guardamos tudo em UTC.
        roteiro: dicionário com as quatro listas do roteiro
            (pontos_positivos, pontos_melhoria, possiveis_motivos,
            roteiro_conversa), normalmente vindo de FeedbackRoteiro.para_dict().
        mes_referencia: mês analisado ("AAAA-MM") ou None para todo o histórico.
        feedback_id: identificador único do registro. Por padrão é criado
            sozinho com uuid4().

    Termos:
        UUID: "identificador único universal", um texto aleatório no formato
            "550e8400-e29b-41d4-a716-446655440000". Como é praticamente
            impossível repetir, serve para identificar um registro sem
            depender de contador.
        UTC: o horário universal (referência mundial). Usar UTC evita confusão
            entre máquinas em fusos diferentes; na tela podemos converter para
            o horário de Brasília depois.

    frozen: depois de criado, o registro não pode ser alterado — ele é um
    histórico do que a IA preparou naquele momento.
    """

    vendedor_id: str
    vendedor_nome: str
    gerado_em: datetime
    roteiro: dict[str, list[str]]
    mes_referencia: str | None = None

    # field(default_factory=...) chama a função a cada criação, gerando um ID
    # novo. Fica por último porque, em Python, campos com valor padrão precisam
    # vir depois dos campos obrigatórios.
    feedback_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Valida o roteiro e guarda uma cópia das listas.

        frozen impede trocar o atributo, mas não impede alterar as listas
        dentro do dicionário. Copiar aqui evita que quem criou o objeto mude
        o registro depois, sem querer.
        """
        if not isinstance(self.roteiro, dict):
            raise ValueError(
                "O campo 'roteiro' deve ser um dicionário com as quatro listas."
            )

        copia: dict[str, list[str]] = {}
        for chave, itens in self.roteiro.items():
            if not isinstance(itens, list):
                raise ValueError(
                    f"O campo 'roteiro.{chave}' deve ser uma lista de textos."
                )
            copia[chave] = list(itens)

        # object.__setattr__ escreve no atributo mesmo com frozen=True. É o
        # jeito recomendado de ajustar o valor na criação do objeto.
        object.__setattr__(self, "roteiro", copia)

    def para_dict(self) -> dict:
        """Transforma o registro em um dicionário pronto para virar JSON.

        JSON: formato de texto organizado em pares nome/valor, usado para
        gravar dados em arquivo. Datas não existem em JSON, então gerado_em
        vira texto no padrão ISO 8601 ("2026-11-11T14:00:00+00:00").

        Devolve cópias das listas do roteiro, para alterar o dicionário sem
        alterar o registro original.
        """
        return {
            "feedback_id": self.feedback_id,
            "vendedor_id": self.vendedor_id,
            "vendedor_nome": self.vendedor_nome,
            "mes_referencia": self.mes_referencia,
            "gerado_em": self.gerado_em.isoformat(),
            "roteiro": {
                chave: list(itens) for chave, itens in self.roteiro.items()
            },
        }

    @classmethod
    def de_dict(cls, dados: dict) -> "RegistroFeedback":
        """Recria um RegistroFeedback a partir do dicionário gravado.

        @classmethod: método chamado na classe, não em um objeto já criado:
        RegistroFeedback.de_dict({...}).

        Levanta ValueError quando:
        - falta um campo obrigatório (feedback_id, vendedor_id, vendedor_nome,
          gerado_em ou roteiro); mes_referencia pode faltar porque None é um
          valor válido;
        - um campo tem o tipo errado;
        - gerado_em não é uma data válida ou não tem fuso horário.

        Exemplo: RegistroFeedback.de_dict(registro.para_dict()) recria o
        mesmo registro.
        """
        if not isinstance(dados, dict):
            raise ValueError("O registro deve ser um dicionário.")

        # 1) Campos obrigatórios: conferimos um por um para a mensagem dizer
        # exatamente qual faltou.
        for campo in (
            "feedback_id",
            "vendedor_id",
            "vendedor_nome",
            "gerado_em",
            "roteiro",
        ):
            if campo not in dados:
                raise ValueError(f"O campo '{campo}' está faltando no registro.")

        # 2) Textos: precisam ser str e não podem ser vazios.
        for campo in ("feedback_id", "vendedor_id", "vendedor_nome"):
            valor = dados[campo]
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(
                    f"O campo '{campo}' deve ser um texto não vazio."
                )

        # 3) Mês de referência: None (todo o histórico) ou texto "AAAA-MM".
        mes_referencia = dados.get("mes_referencia")
        if mes_referencia is not None and not isinstance(mes_referencia, str):
            raise ValueError(
                "O campo 'mes_referencia' deve ser texto ou None."
            )

        # 4) Data: o JSON guarda texto; convertemos de volta para datetime.
        texto_data = dados["gerado_em"]
        if not isinstance(texto_data, str):
            raise ValueError(
                "O campo 'gerado_em' deve ser uma data em texto ISO 8601."
            )
        try:
            gerado_em = datetime.fromisoformat(texto_data)
        except ValueError as erro:
            raise ValueError(
                f"O campo 'gerado_em' não é uma data válida: {texto_data!r}."
            ) from erro

        # Sem fuso não sabemos a que horas o roteiro foi gerado de verdade.
        if gerado_em.tzinfo is None:
            raise ValueError(
                "O campo 'gerado_em' precisa ter fuso horário (ex.: +00:00)."
            )

        # Convertemos para UTC para guardar sempre no mesmo padrão, mesmo que
        # o texto venha com outro fuso (ex.: -03:00).
        gerado_em = gerado_em.astimezone(timezone.utc)

        # 5) Roteiro: precisa ser dicionário. As listas internas são validadas
        # no __post_init__, para não repetir a regra em dois lugares.
        roteiro = dados["roteiro"]
        if not isinstance(roteiro, dict):
            raise ValueError(
                "O campo 'roteiro' deve ser um dicionário com as quatro listas."
            )

        return cls(
            feedback_id=dados["feedback_id"],
            vendedor_id=dados["vendedor_id"],
            vendedor_nome=dados["vendedor_nome"],
            mes_referencia=mes_referencia,
            gerado_em=gerado_em,
            roteiro=roteiro,
        )
