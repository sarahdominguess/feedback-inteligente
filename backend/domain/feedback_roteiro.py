"""Estrutura do roteiro de feedback preparado para o gerente.

O roteiro tem quatro listas de textos: pontos positivos, pontos de melhoria,
possíveis motivos e o roteiro da conversa. Por enquanto é só uma estrutura de
dados; a integração com a LLM (DeepSeek) vai preenchê-la numa etapa futura.
"""

from dataclasses import dataclass, field


@dataclass
class FeedbackRoteiro:
    """Roteiro de feedback em quatro partes, cada uma com uma lista de textos.

    Recebe (todas opcionais; sem valor, começam como listas vazias):
        pontos_positivos: o que a pessoa faz bem.
        pontos_melhoria: o que pode melhorar.
        possiveis_motivos: hipóteses que explicam os números.
        roteiro_conversa: perguntas e falas sugeridas para a conversa.

    field(default_factory=list) cria uma lista nova para cada objeto. Se
    usássemos apenas "= []", todos os roteiros compartilhariam a mesma lista,
    e mudar um mudaria os outros também.
    """

    pontos_positivos: list[str] = field(default_factory=list)
    pontos_melhoria: list[str] = field(default_factory=list)
    possiveis_motivos: list[str] = field(default_factory=list)
    roteiro_conversa: list[str] = field(default_factory=list)

    def para_dict(self) -> dict[str, list[str]]:
        """Transforma o roteiro em um dicionário simples.

        Dicionário: estrutura que guarda pares "nome → valor"; aqui, o nome de
        cada parte do roteiro aponta para a lista de textos correspondente.

        Devolve cópias das listas (list(...)): assim, alterar o dicionário
        resultante não altera o objeto FeedbackRoteiro original.

        Exemplo de retorno:
        {
            "pontos_positivos": ["Ótima relação com as clientes"],
            "pontos_melhoria": ["Vender mais de uma peça por atendimento"],
            "possiveis_motivos": [],
            "roteiro_conversa": [],
        }
        """
        return {
            "pontos_positivos": list(self.pontos_positivos),
            "pontos_melhoria": list(self.pontos_melhoria),
            "possiveis_motivos": list(self.possiveis_motivos),
            "roteiro_conversa": list(self.roteiro_conversa),
        }

    @classmethod
    def de_dict(cls, dados: dict) -> "FeedbackRoteiro":
        """Cria um FeedbackRoteiro a partir de um dicionário.

        @classmethod: um método que pertence à classe (não a um objeto já
        criado) e é chamado como FeedbackRoteiro.de_dict(...).

        Recebe um dicionário que pode ter as quatro chaves do roteiro. Chaves
        extras são ignoradas; chaves ausentes viram lista vazia. Se algum valor
        não for uma lista de textos (str), levanta ValueError.

        Exemplo: FeedbackRoteiro.de_dict({"pontos_positivos": ["Bom atendimento"]})
        cria um roteiro em que só os pontos positivos estão preenchidos.
        """
        # Nomes das quatro partes que o roteiro conhece. Qualquer outra chave
        # recebida é simplesmente ignorada.
        nomes = (
            "pontos_positivos",
            "pontos_melhoria",
            "possiveis_motivos",
            "roteiro_conversa",
        )

        valores = {}
        for nome in nomes:
            # get(nome, []) devolve lista vazia quando a chave não existe,
            # o que atende à regra de aceitar chaves ausentes.
            valor = dados.get(nome, [])

            # isinstance(valor, list) confere se é uma lista; all(...) confere
            # se todos os itens são textos (str). Se qualquer item for número
            # ou outra coisa, o valor é inválido.
            if not isinstance(valor, list) or not all(
                isinstance(item, str) for item in valor
            ):
                raise ValueError(
                    f"O campo '{nome}' deve ser uma lista de textos."
                )

            # Guardamos uma cópia da lista para o roteiro não compartilhar a
            # mesma lista do dicionário recebido.
            valores[nome] = list(valor)

        # cls(**valores) chama o construtor da própria classe usando os quatro
        # valores já validados como argumentos nomeados.
        return cls(**valores)
