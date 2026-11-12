"""Construtor das mensagens da IA para o feedback da regional ao gerente.

Este módulo é PURO: não acessa a internet, não usa a SDK openai e não lê
arquivos. Recebe o dicionário já calculado por
ConsolidadoRegional.obter_desempenho_gerente() e devolve duas mensagens de
texto: a de sistema (papel, regras e formato) e a de usuário (dados da loja).

Por que um construtor separado do prompt do vendedor: aqui a conversa é da
gerente regional com o GERENTE da loja, e não do gerente com uma vendedora.
Os fatos são os resultados da loja, a cobertura de feedbacks do time e as
anotações das visitas — não os indicadores individuais de uma pessoa. Misturar
os dois prompts faria a IA cobrar do gerente números de vendedor, o que seria
injusto e confuso.

Reaproveitamento do validador: `validar_roteiro` (em validador_feedback.py)
pode ser usada com `vendedor_nome=consolidado["gerente_nome"]` e
`nomes_colegas=()`. Ela confere quantidade, tamanho, perguntas abertas e
clichês; com a lista de colegas vazia, NENHUM nome é bloqueado. Ou seja, a
função não impede citar outro gerente ou outra loja — esse limite fica a cargo
do prompt de sistema, que é explícito sobre isso. Para o roteiro do gerente
não há "colegas" a proteger: a conversa é individual e o único nome em jogo é
o do próprio avaliado (que é permitido).
"""

# Reaproveitamos os formatadores do prompt do vendedor para dinheiro, data,
# mês e percentual saírem sempre no mesmo padrão brasileiro. Importar daqui
# NÃO viola a regra de "módulo puro": aquele arquivo também não faz I/O.
from services.prompt_feedback import (
    formatar_data,
    formatar_mes,
    formatar_moeda,
    formatar_percentual,
)

# Mensagem de sistema: define o papel da IA, o método e os limites. É montada
# em pedaços para que cada regra tenha, ao lado, um comentário explicando POR
# QUE ela existe; os comentários ficam só no código e não vão para a IA.
SISTEMA_PROMPT_REGIONAL = (
    # Papel: a IA prepara a gerente regional, não conversa com o gerente. Sem
    # isso, ela pode escrever como se estivesse falando diretamente com ele.
    "Você é o Co-piloto Executivo da Gerente Regional no Varejo.\n"
    "Você apoia a gerente regional a preparar uma conversa de feedback\n"
    "individual e privada com o gerente da loja. Ela é a dona da conversa:\n"
    "vai revisar, adaptar e conduzir o seu rascunho. Você prepara a gerente\n"
    "regional; não fala diretamente com o gerente.\n"
    "\n"
    # SBI: feedback sem método vira opinião. Ligar situação, comportamento e
    # impacto aos números e às visitas torna o retorno verificável e justo.
    "MÉTODO SBI (Situação, Comportamento, Impacto)\n"
    "- Situação: quando e onde aconteceu, citando o número da loja ou a\n"
    "  observação de visita que mostra o fato.\n"
    "- Comportamento: o que o gerente fez de observável na liderança da loja\n"
    "  (rotina, escala, presença no caixa, condução do time), sem rótulo de\n"
    "  personalidade.\n"
    "- Impacto: o efeito no resultado da loja, no cliente ou no time.\n"
    "Todo ponto de melhoria deve seguir S-B-I e terminar em uma ação pequena\n"
    "e concreta, possível de começar já amanhã.\n"
    "\n"
    # Limites: o bloco de dados fala de UMA loja e de UM gerente. Citar outros
    # nomes ou inventar números quebra a confiança e pode prejudicar terceiros.
    "LIMITES\n"
    "- Fale APENAS do gerente avaliado e da loja dele.\n"
    "- É PROIBIDO mencionar nomes de outros gerentes ou de outras lojas.\n"
    "- É PROIBIDO citar vendedores pelo nome; se precisar, diga \"o time\".\n"
    "- É PROIBIDO inventar números, datas, clientes, metas ou motivos. Use\n"
    "  SOMENTE os valores e as anotações do bloco de dados.\n"
    "- Não faça contas novas: use os números já calculados.\n"
    "- Em \"possiveis_motivos\", escreva HIPÓTESES a confirmar ouvindo o\n"
    "  gerente, no formato \"pode ser que...\".\n"
    "\n"
    # Tom: linguagem de loja aproxima; texto de robô soa falso. Cada item
    # precisa de um dado ou de uma anotação para não virar conselho genérico.
    "TOM\n"
    "- Direto, construtivo e em português do Brasil, com linguagem de loja.\n"
    "- Proibido texto genérico de robô como \"Prezado colaborador\",\n"
    "  \"oportunidades de melhoria em múltiplas dimensões\" ou \"buscar a\n"
    "  excelência\".\n"
    "- Comece reconhecendo o que é bom, com base em fatos.\n"
    "- Respeite o contexto dos dados: mês parcial, meta e dias com dados.\n"
    "- Não faça diagnóstico psicológico nem use ironia ou ameaça.\n"
    "\n"
    # Saída: JSON é o formato que o backend transforma em FeedbackRoteiro sem
    # adivinhar texto solto. As perguntas são para o GERENTE falar primeiro.
    "SAÍDA\n"
    "Responda SOMENTE com um objeto JSON válido, sem markdown e sem texto\n"
    "antes ou depois, com exatamente estas 4 chaves, cada uma uma lista de\n"
    "textos em português:\n"
    "- \"pontos_positivos\": 2 a 4 reconhecimentos da liderança, baseados nos\n"
    "  números da loja ou nas anotações da regional;\n"
    "- \"pontos_melhoria\": 2 a 3 alavancas de desenvolvimento no formato SBI,\n"
    "  cada uma terminando em uma ação para amanhã;\n"
    "- \"possiveis_motivos\": 2 a 3 hipóteses de comportamento ou de contexto;\n"
    "- \"roteiro_conversa\": 6 a 9 itens em ordem de conversa: abertura\n"
    "  acolhedora, reconhecimento, Situação-Comportamento-Impacto, pelo menos\n"
    "  3 perguntas abertas para o gerente (que não possam ser respondidas com\n"
    "  sim/não e o convidem a falar primeiro), combinado de uma ação para\n"
    "  amanhã e fechamento com data de acompanhamento.\n"
    "\n"
    "Exemplo do formato JSON (textos fictícios, sem nomes reais):\n"
    '{"pontos_positivos": ["Exemplo de reconhecimento com dado real"], '
    '"pontos_melhoria": ["Exemplo de melhoria em SBI com ação para amanhã"], '
    '"possiveis_motivos": ["Pode ser que exemplo de hipótese"], '
    '"roteiro_conversa": ["Exemplo de abertura", "Exemplo de pergunta aberta", '
    '"Exemplo de combinado e data de acompanhamento"]}\n'
)


def _linha_resultado_mes(item: dict) -> str:
    """Monta uma linha de texto com todos os números de UM mês da loja.

    Recebe um item de consolidado["resultado_loja"] (exatamente os campos de
    ResultadoLojaMesDTO) e devolve uma frase única, com os rótulos em
    português. Valores ausentes (meta não cadastrada, por exemplo) viram
    "sem dados" pelos formatadores — nunca um zero inventado.

    Quando o mês é parcial, acrescenta um aviso: comparar um mês com poucos
    dias com um mês cheio seria injusto com o gerente.
    """
    linha = (
        f"- {formatar_mes(item['mes'])}: "
        f"meta da loja {formatar_moeda(item['meta_loja'])}; "
        f"vendas da loja {formatar_moeda(item['vendas_loja'])}; "
        f"atingimento da loja {formatar_percentual(item['atingimento_loja'])}; "
        f"vendas dos vendedores {formatar_moeda(item['vendas_vendedores'])}; "
        f"atingimento dos vendedores "
        f"{formatar_percentual(item['atingimento_vendedores'])}; "
        f"vendas do gerente no caixa {formatar_moeda(item['vendas_gerente'])}; "
        f"participação do gerente "
        f"{formatar_percentual(item['participacao_gerente'])}"
    )

    # Aviso explícito de mês parcial, com quantos dias têm dados.
    if item["mes_parcial"]:
        quantidade = item["dias_com_dados"]
        unidade = "dia" if quantidade == 1 else "dias"
        linha += (
            f"; ATENÇÃO: mês parcial (apenas {quantidade} {unidade} "
            "com dados)"
        )

    return linha


def _linhas_de_anotacoes(anotacoes: list[dict]) -> list[str]:
    """Monta as linhas das anotações da regional, uma por visita.

    Recebe a lista de anotações (já em ordem cronológica pelo consolidado) e
    devolve as linhas com a data formatada na frente. Se não houver nenhuma,
    devolve uma linha dizendo isso — melhor do que um bloco vazio, que deixaria
    a IA sem saber se o dado faltou.
    """
    if not anotacoes:
        return ["- Nenhuma anotação da regional sobre a loja."]

    linhas = []
    for anotacao in anotacoes:
        # A data vem como objeto date; formatar_data deixa "18/08/2026".
        data_formatada = formatar_data(anotacao["data"])
        linhas.append(f"- {data_formatada}: {anotacao['texto']}")
    return linhas


def montar_prompt_feedback_regional(
    consolidado: dict,
    mes_referencia: str | None = None,
) -> tuple[str, str]:
    """Monta (mensagem de sistema, mensagem de usuário) para a IA.

    Recebe:
        consolidado: o dicionário devolvido por
            ConsolidadoRegional.obter_desempenho_gerente() — nada é recalculado
            aqui.
        mes_referencia: "AAAA-MM" para destacar um mês ou None para analisar
            todo o histórico.

    Devolve uma tupla (sistema, usuário), pronta para virar as duas mensagens
    de chat da API.

    Levanta ValueError quando o mês pedido não existe em resultado_loja: é
    melhor falhar com uma mensagem clara do que gerar um roteiro sem o mês
    escolhido.

    Exemplo: montar_prompt_feedback_regional(dados, "2026-10") devolve o
    prompt com outubro em destaque e os outros meses como contexto.
    """
    resultado_loja = consolidado["resultado_loja"]
    meses_disponiveis = [item["mes"] for item in resultado_loja]

    # Validação cedo: se o mês não existe, nada mais adianta montar.
    if mes_referencia is not None and mes_referencia not in meses_disponiveis:
        disponiveis = ", ".join(meses_disponiveis) or "nenhum"
        raise ValueError(
            f"O mês {mes_referencia} não existe no resultado da loja. "
            f"Meses disponíveis: {disponiveis}."
        )

    linhas: list[str] = []

    # 1) Quem: situa a IA sobre a loja, o gerente avaliado e o período.
    linhas.append("QUEM")
    linhas.append(
        f"- Loja: {consolidado['loja_nome']} ({consolidado['loja_id']})"
    )
    linhas.append(f"- Gerente avaliado: {consolidado['gerente_nome']}")
    linhas.append(f"- Período analisado: {formatar_mes(mes_referencia)}")
    linhas.append("")

    # 2) Resultado da loja. Com um mês escolhido, ele vem em destaque e os
    # demais ficam como contexto; sem escolha, todos os meses são listados.
    if mes_referencia is None:
        linhas.append(
            "RESULTADO DA LOJA (todo o histórico, em ordem cronológica)"
        )
        for item in resultado_loja:
            linhas.append(_linha_resultado_mes(item))
        linhas.append("")
    else:
        linhas.append(
            "RESULTADO DA LOJA NO MÊS DE REFERÊNCIA "
            f"({formatar_mes(mes_referencia)})"
        )
        for item in resultado_loja:
            if item["mes"] == mes_referencia:
                linhas.append(_linha_resultado_mes(item))
                break
        linhas.append("")

        # Contexto só faz sentido se houver outros meses além do escolhido.
        outros = [
            item for item in resultado_loja if item["mes"] != mes_referencia
        ]
        if outros:
            linhas.append(
                "CONTEXTO DOS DEMAIS MESES "
                "(use para comparar, sem cobrar do gerente meses parciais)"
            )
            for item in outros:
                linhas.append(_linha_resultado_mes(item))
            linhas.append("")

    # 3) Liderança e acompanhamento: a conversa é sobre o time, então a
    # cobertura de feedbacks entra como fato de liderança, nunca como meta.
    acompanhamento = consolidado["acompanhamento_feedback"]
    linhas.append("LIDERANÇA E ACOMPANHAMENTO DE FEEDBACKS DO TIME")
    linhas.append(
        f"- Vendedores na loja: {acompanhamento['total_vendedores']}"
    )
    linhas.append(
        "- Vendedores com pelo menos um roteiro preparado: "
        f"{acompanhamento['vendedores_com_roteiro']}"
    )
    linhas.append(
        "- Cobertura de feedbacks preparados no time: "
        f"{formatar_percentual(acompanhamento['cobertura'])}"
    )
    linhas.append(
        "- Total de roteiros preparados para o time: "
        f"{acompanhamento['total_roteiros_preparados']}"
    )
    linhas.append(
        "Lembrete: \"roteiro preparado\" significa que o roteiro foi GERADO "
        "pela IA; não significa que a conversa de feedback já aconteceu."
    )
    linhas.append("")

    # 4) Anotações da regional: são as observações das visitas, já em ordem
    # cronológica no consolidado.
    linhas.append(
        "ANOTAÇÕES DA REGIONAL SOBRE A LOJA (ordem cronológica)"
    )
    linhas.extend(_linhas_de_anotacoes(consolidado["anotacoes_regional"]))
    linhas.append("")

    # 5) Instrução final: repete o formato para a resposta não vir solta.
    linhas.append("Gere o roteiro em JSON conforme as regras.")

    return SISTEMA_PROMPT_REGIONAL, "\n".join(linhas)
