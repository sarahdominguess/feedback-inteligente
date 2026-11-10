"""Construtor das mensagens enviadas à IA para preparar o feedback.

Este módulo é puro: não acessa a internet, não usa a SDK openai e não lê
arquivos. Recebe objetos de domínio já calculados (Vendedor, ComparativoTime e
anotações) e devolve duas mensagens de texto: a de sistema (regras e papel) e a
de usuário (dados da vendedora). É daqui que sai a qualidade do roteiro.
"""

from collections.abc import Sequence
from datetime import date

from domain.anotacao import Anotacao
from domain.comparativo_time import ComparativoTime
from domain.vendedor import Vendedor

# Nomes dos meses em português. Usamos uma lista fixa em vez de locale do
# sistema porque locale (configuração de idioma da máquina) muda de computador
# para computador e poderia gerar "October" em uma máquina e "outubro" em outra.
_MESES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)

# Rótulos em português para os nomes técnicos das métricas do comparativo.
_ROTULOS_METRICAS = {
    "ticket_medio": "Ticket médio",
    "pecas_por_atendimento": "P.A. (peças por venda)",
    "conversao": "Conversão",
}

# Tradução das situações do comparativo para um texto mais natural.
_SITUACOES = {
    "acima": "acima",
    "abaixo": "abaixo",
    "na_media": "na média",
    "indisponivel": "indisponível",
}


def formatar_moeda(valor: float | None) -> str:
    """Formata um valor em reais no padrão brasileiro, ou "sem dados".

    Recebe um número (ou None) e devolve, por exemplo, "R$ 206,31".
    None significa "sem valor" e vira o texto "sem dados".

    Exemplo: 206.311... vira "R$ 206,31".
    """
    if valor is None:
        return "sem dados"

    # O Python formata números no padrão dos EUA ("1,234.56"). Primeiro
    # trocamos a vírgula por um marcador "X", depois o ponto por vírgula e,
    # por fim, o "X" por ponto. Assim chegamos a "1.234,56", como usamos aqui.
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_percentual(valor: float | None, com_sinal: bool = False) -> str:
    """Formata uma fração como porcentagem com uma casa decimal.

    Recebe uma fração de 0 a 1 (0,5048) e devolve "50,5%". None vira
    "sem dados". Com com_sinal=True, valores positivos ganham "+" na frente,
    o que ajuda a ler diferenças (ex.: "+12,0%").

    Exemplo: formatar_percentual(0.5048) devolve "50,5%".
    """
    if valor is None:
        return "sem dados"

    # Multiplicamos por 100 para virar porcentagem e trocamos o ponto decimal
    # pela vírgula, sem depender da configuração de idioma da máquina.
    texto = f"{valor * 100:.1f}%".replace(".", ",")

    # O sinal de menos já aparece sozinho; só o positivo precisa do "+".
    if com_sinal and valor > 0:
        return f"+{texto}"
    return texto


def formatar_numero(valor: float | None) -> str:
    """Formata um número com duas casas decimais e vírgula decimal.

    Recebe um número (ou None) e devolve "1,22". None vira "sem dados".

    Exemplo: o P.A. 1.224 vira "1,22".
    """
    if valor is None:
        return "sem dados"
    return f"{valor:.2f}".replace(".", ",")


def formatar_mes(mes: str | None) -> str:
    """Traduz "AAAA-MM" para "mês/ano" em português.

    Recebe "2026-10" e devolve "outubro/2026". None significa todo o
    histórico e devolve "todo o histórico".
    """
    if mes is None:
        return "todo o histórico"

    # split("-") separa o texto em duas partes: o ano e o número do mês.
    ano, numero = mes.split("-")
    return f"{_MESES[int(numero) - 1]}/{ano}"


def formatar_data(data: date) -> str:
    """Formata uma data como "dia/mês/ano" (ex.: "06/08/2026")."""
    return f"{data.day:02d}/{data.month:02d}/{data.year:04d}"


def _formatar_metrica(nome: str, valor: float | None) -> str:
    """Formata o valor de uma métrica conforme o tipo dela.

    Ticket médio é dinheiro, conversão é porcentagem e P.A. é número puro.
    Métricas desconhecidas caem no formato de número.
    """
    if nome == "ticket_medio":
        return formatar_moeda(valor)
    if nome == "conversao":
        return formatar_percentual(valor)
    return formatar_numero(valor)


def _linhas_de_anotacoes(
    titulo: str, anotacoes: Sequence[Anotacao]
) -> list[str]:
    """Monta as linhas de um bloco de anotações em ordem cronológica.

    Recebe o título do bloco e as anotações; devolve uma lista de linhas de
    texto, uma por anotação, com a data na frente.
    """
    linhas = [titulo]

    # sorted copia e ordena por data, para a conversa seguir a linha do tempo.
    ordenadas = sorted(anotacoes, key=lambda anotacao: anotacao.data)

    if not ordenadas:
        linhas.append("- Nenhuma anotação.")
        return linhas

    for anotacao in ordenadas:
        linhas.append(f"- {formatar_data(anotacao.data)}: {anotacao.texto}")
    return linhas


# Mensagem de sistema: define papel, método, limites e formato da resposta.
# Ela é montada em pedaços para que cada regra tenha, ao lado, um comentário
# explicando POR QUE a regra existe. Esses comentários ficam só no código e
# não são enviados à IA.
SISTEMA_PROMPT = (
    # Papel: deixa claro quem fala e quem decide. Sem isso, a IA pode tratar
    # o rascunho como ordem final ou escrever como se falasse à vendedora.
    "Você é o Co-piloto de Liderança e Feedback no Varejo.\n"
    "Você apoia o gerente de loja a preparar uma conversa de feedback\n"
    "individual e privada. O gerente é o dono da conversa: vai revisar,\n"
    "adaptar e conduzir o seu rascunho. Você prepara o gerente; não fala\n"
    "diretamente com a vendedora.\n"
    "\n"
    # SBI: dá um método concreto de observação e ação. Feedback sem método
    # vira opinião; com SBI, vira fato observável ligado a consequência.
    "MÉTODO SBI (Situação, Comportamento, Impacto)\n"
    "- Situação: quando e onde aconteceu, citando o dado que mostra o fato.\n"
    "- Comportamento: o que a pessoa fez de observável, sem rótulo de\n"
    "  personalidade.\n"
    "- Impacto: o efeito no resultado, no cliente ou no time.\n"
    "Todo ponto de melhoria deve seguir S-B-I e terminar em uma ação concreta\n"
    "e pequena, para fazer já amanhã. Feedback vago não muda nada.\n"
    "\n"
    # Honestidade: números e anotações são a única fonte de verdade. Inventar
    # fato ou motivo destrói a confiança do gerente e pode prejudicar a pessoa.
    "HONESTIDADE\n"
    "- Use APENAS os números e as anotações fornecidos.\n"
    "- Não invente fatos, datas, clientes, valores nem motivos como se fossem\n"
    "  certos.\n"
    "- Se faltar um dado, diga que falta em vez de supor.\n"
    "- Não faça contas novas: use os números já calculados.\n"
    "- Em \"possiveis_motivos\", escreva HIPÓTESES a confirmar ouvindo a\n"
    "  pessoa, no formato \"pode ser que...\".\n"
    "\n"
    # Justiça e cuidado: comparação por nome humilha e gera conflito; rótulo
    # e ironia fecham a pessoa; "mas" anula o elogio; contexto evita injustiça
    # (mês parcial, férias); diagnóstico psicológico não é papel do gerente.
    "JUSTIÇA E CUIDADO\n"
    "- Nunca compare a pessoa com colegas pelo nome; a única comparação\n"
    "  permitida é com \"a média do time\".\n"
    "- Não cite assuntos pessoais de ninguém.\n"
    "- Não use rótulos (\"você é desorganizada\"), ameaça, ironia nem um \"mas\"\n"
    "  que anule o elogio.\n"
    "- Comece reconhecendo o que é bom, com base em fatos.\n"
    "- Respeite o contexto dos dados: mês parcial, férias, meta.\n"
    "- Não faça diagnóstico psicológico.\n"
    "\n"
    # Tom: linguagem de loja aproxima; texto de robô afasta e soa falso.
    # Cada item precisa de dado ou anotação para não virar conselho genérico.
    "TOM\n"
    "- Caloroso, direto, linguagem de loja (não de RH).\n"
    "- Proibido texto genérico de robô como \"Prezado colaborador\",\n"
    "  \"oportunidades de melhoria em múltiplas dimensões\" ou \"buscar a\n"
    "  excelência\".\n"
    "- Cada item deve ser específico para ESTA pessoa e ligado a um dado ou\n"
    "  anotação.\n"
    "\n"
    # Saída: JSON é o formato que o backend consegue transformar em
    # FeedbackRoteiro sem adivinhar texto solto. A palavra "JSON" e o exemplo
    # são exigidos pelo modo JSON da API.
    "SAÍDA\n"
    "Responda SOMENTE com um objeto JSON válido, sem markdown e sem texto\n"
    "antes ou depois, com exatamente estas 4 chaves, cada uma uma lista de\n"
    "textos em português:\n"
    "- \"pontos_positivos\": 2 a 4 reconhecimentos baseados em dados reais ou\n"
    "  anotações;\n"
    "- \"pontos_melhoria\": 2 a 3 alavancas de desenvolvimento, cada uma no\n"
    "  formato SBI em uma ou duas frases;\n"
    "- \"possiveis_motivos\": 2 a 3 hipóteses comportamentais ou de contexto;\n"
    "- \"roteiro_conversa\": 6 a 9 itens em ordem de conversa: abertura\n"
    "  acolhedora, reconhecimento, Situação-Comportamento-Impacto, pelo menos\n"
    "  3 perguntas abertas empáticas (que não possam ser respondidas com\n"
    "  sim/não e convidem a pessoa a falar primeiro), combinado de uma ação\n"
    "  para amanhã e fechamento com data de acompanhamento.\n"
    "\n"
    "Exemplo do formato JSON (textos fictícios, sem nomes reais):\n"
    '{"pontos_positivos": ["Exemplo de reconhecimento com dado real"], '
    '"pontos_melhoria": ["Exemplo de melhoria em SBI com ação para amanhã"], '
    '"possiveis_motivos": ["Pode ser que exemplo de hipótese"], '
    '"roteiro_conversa": ["Exemplo de abertura", "Exemplo de pergunta aberta", '
    '"Exemplo de combinado e data de acompanhamento"]}\n'
)


def _montar_mensagem_usuario(
    vendedor: Vendedor,
    comparativo: ComparativoTime,
    anotacoes_do_vendedor: Sequence[Anotacao],
    anotacoes_do_time: Sequence[Anotacao],
    gerente_nome: str,
    loja_nome: str,
    mes_referencia: str | None,
) -> str:
    """Monta a mensagem de usuário com todos os dados já calculados.

    Recebe o Vendedor, o ComparativoTime, as anotações (da pessoa e do time),
    os nomes do gerente e da loja e o mês de referência (None = histórico
    completo). Devolve um texto dividido em seções, pronto para ser enviado
    junto com a mensagem de sistema.
    """
    linhas: list[str] = []

    # 1) Quem: situa a IA sobre o gerente, a loja, a vendedora e o período.
    linhas.append("QUEM")
    linhas.append(f"- Gerente: {gerente_nome}")
    linhas.append(f"- Loja: {loja_nome}")
    linhas.append(f"- Vendedora: {vendedor.nome} (cargo: {vendedor.cargo})")
    linhas.append(f"- Período analisado: {formatar_mes(mes_referencia)}")
    linhas.append("")

    # 2) Indicadores do período: números consolidados, sem contar de novo.
    linhas.append("INDICADORES DO PERÍODO")
    linhas.append(
        f"- Valor vendido: {formatar_moeda(vendedor.valor_vendido(mes_referencia))}"
    )
    linhas.append(f"- Vendas: {vendedor.vendas(mes_referencia)}")
    linhas.append(f"- Peças: {vendedor.pecas(mes_referencia)}")
    linhas.append(f"- Atendimentos: {vendedor.atendimentos(mes_referencia)}")
    linhas.append(
        f"- Ticket médio: {formatar_moeda(vendedor.ticket_medio(mes_referencia))}"
    )
    linhas.append(
        "- P.A. (peças por venda): "
        f"{formatar_numero(vendedor.pecas_por_atendimento(mes_referencia))}"
    )
    linhas.append(
        f"- Conversão: {formatar_percentual(vendedor.conversao(mes_referencia))}"
    )

    # Meta só faz sentido quando existe um mês específico com meta cadastrada.
    # O gerente não tem meta individual; para ele este bloco não aparece.
    meta_do_mes = (
        vendedor.meta_do_mes(mes_referencia) if mes_referencia else None
    )
    if meta_do_mes is not None:
        linhas.append(f"- Meta do mês: {formatar_moeda(meta_do_mes)}")
        linhas.append(
            "- Atingimento da meta: "
            f"{formatar_percentual(vendedor.atingimento_meta(mes_referencia))}"
        )
    linhas.append("")

    # 3) Resumo mensal: um bloco por mês, com aviso de mês parcial. Mês com
    # poucos dias não pode ser comparado com mês cheio; o aviso evita injustiça.
    linhas.append("RESUMO MENSAL")
    for resumo in vendedor.resumo_mensal():
        linha = (
            f"- {formatar_mes(resumo['mes'])}: "
            f"valor vendido {formatar_moeda(resumo['valor_vendido'])}; "
            f"vendas {resumo['vendas']}; peças {resumo['pecas']}; "
            f"atendimentos {resumo['atendimentos']}; "
            f"ticket médio {formatar_moeda(resumo['ticket_medio'])}; "
            f"P.A. {formatar_numero(resumo['pecas_por_atendimento'])}; "
            f"conversão {formatar_percentual(resumo['conversao'])}"
        )
        if resumo["meta"] is not None:
            linha += (
                f"; meta {formatar_moeda(resumo['meta'])}; "
                f"atingimento {formatar_percentual(resumo['atingimento_meta'])}"
            )
        linhas.append(linha)

        # Abaixo de 10 dias com dados, o mês é sinalizado como parcial.
        if resumo["dias_com_dados"] < 10:
            quantidade = resumo["dias_com_dados"]
            unidade = "dia" if quantidade == 1 else "dias"
            linhas.append(
                f"  - mês parcial (apenas {quantidade} {unidade} com dados)"
            )
    linhas.append("")

    # 4) Comparativo com o time: deixa explícito que não existe meta de P.A.
    # nem de conversão; a referência é a média calculada a partir das somas.
    linhas.append("COMPARATIVO COM A MÉDIA DO TIME")
    linhas.append(
        "Não há meta de P.A. nem de conversão; a referência é a média do time."
    )
    for metrica in comparativo.metricas:
        rotulo = _ROTULOS_METRICAS.get(metrica.nome, metrica.nome)
        if metrica.posicao is None:
            posicao = "sem posição"
        else:
            posicao = f"{metrica.posicao}º de {metrica.total_vendedores}"
        situacao = _SITUACOES.get(metrica.situacao, metrica.situacao)
        linhas.append(
            f"- {rotulo}: {_formatar_metrica(metrica.nome, metrica.valor)}"
            f" | média do time: {_formatar_metrica(metrica.nome, metrica.media_time)}"
            f" | diferença: {formatar_percentual(metrica.diferenca_percentual, com_sinal=True)}"
            f" | posição: {posicao}"
            f" | situação: {situacao}"
        )
    linhas.append("")

    # 5) Anotações: só as da vendedora e as do time. Anotações sobre outras
    # pessoas ficam de fora para preservar a privacidade e evitar comparação.
    linhas.extend(
        _linhas_de_anotacoes(
            "ANOTAÇÕES DO GERENTE SOBRE A VENDEDORA (ordem cronológica)",
            anotacoes_do_vendedor,
        )
    )
    linhas.append("")
    linhas.extend(
        _linhas_de_anotacoes(
            "ANOTAÇÕES DO GERENTE SOBRE O TIME (ordem cronológica)",
            anotacoes_do_time,
        )
    )
    linhas.append("")

    # 6) Instrução final: repete o formato para a resposta não vir solta.
    linhas.append("Gere o roteiro em JSON conforme as regras.")

    return "\n".join(linhas)


def montar_mensagens(
    vendedor: Vendedor,
    comparativo: ComparativoTime,
    anotacoes_do_vendedor: Sequence[Anotacao],
    anotacoes_do_time: Sequence[Anotacao],
    gerente_nome: str,
    loja_nome: str,
    mes_referencia: str | None = None,
) -> list[dict]:
    """Monta as duas mensagens de chat (sistema e usuário) para a LLM.

    Recebe os dados já calculados (nada é lido de CSV nem recalculado aqui),
    o nome do gerente, o nome da loja e, opcionalmente, o mês de referência
    ("AAAA-MM"; None = todo o histórico).

    Devolve uma lista no formato aceito pela API de chat:
    [{"role": "system", "content": ...}, {"role": "user", "content": ...}].
    """
    return [
        {"role": "system", "content": SISTEMA_PROMPT},
        {
            "role": "user",
            "content": _montar_mensagem_usuario(
                vendedor=vendedor,
                comparativo=comparativo,
                anotacoes_do_vendedor=anotacoes_do_vendedor,
                anotacoes_do_time=anotacoes_do_time,
                gerente_nome=gerente_nome,
                loja_nome=loja_nome,
                mes_referencia=mes_referencia,
            ),
        },
    ]
