"""Construtor das mensagens da IA para o feedback da regional ao gerente.

Este módulo é puro: não acessa a internet, não usa a SDK openai e não lê
arquivos. Recebe o dicionário já calculado por
ConsolidadoRegional.obter_desempenho_gerente() e devolve as duas mensagens de
chat (sistema e usuário).

A única "conta" feita aqui é a contagem de vendedores sem roteiro preparado, que
é uma contagem simples sobre a lista recebida — nenhum indicador é recalculado.
"""

from datetime import date

from services.prompt_feedback import (
    formatar_data,
    formatar_mes,
    formatar_moeda,
    formatar_percentual,
)


def _formatar_data_anotacao(valor) -> str:
    """Formata a data de uma anotação, aceitando date ou texto ISO.

    O consolidado devolve objetos date, mas o dicionário pode ter vindo de um
    JSON (onde data é texto "AAAA-MM-DD"). Aceitamos os dois para o prompt
    nunca mostrar algo técnico como "2026-10-20" ou "None".

    Exemplo: date(2026, 10, 20) e "2026-10-20" viram "20/10/2026".
    """
    if isinstance(valor, date):
        return formatar_data(valor)

    if isinstance(valor, str) and len(valor) >= 10:
        try:
            return formatar_data(date.fromisoformat(valor[:10]))
        except ValueError:
            return valor

    return "sem dado"


def _meses_disponiveis(desempenho: dict) -> list[str]:
    """Devolve os meses que existem em resultado_loja, em ordem cronológica."""
    meses = [
        item.get("mes")
        for item in desempenho.get("resultado_loja", [])
        if item.get("mes")
    ]
    return sorted(meses)


def _linha_resultado(item: dict) -> str:
    """Monta a linha de um mês do resultado da loja.

    Recebe um item de resultado_loja (já calculado pelo consolidado) e devolve
    uma linha de texto com meta, vendas, atingimentos e a participação do
    gerente. Nenhum número é recalculado: só formatado.
    """
    linha = (
        f"- {formatar_mes(item.get('mes'))}: "
        f"meta da loja {formatar_moeda(item.get('meta_loja'))}; "
        f"vendas da loja {formatar_moeda(item.get('vendas_loja'))}; "
        f"atingimento da loja {formatar_percentual(item.get('atingimento_loja'))}; "
        f"vendas dos vendedores {formatar_moeda(item.get('vendas_vendedores'))}; "
        "atingimento dos vendedores "
        f"{formatar_percentual(item.get('atingimento_vendedores'))}; "
        f"vendas do gerente no caixa {formatar_moeda(item.get('vendas_gerente'))}; "
        "participação do gerente "
        f"{formatar_percentual(item.get('participacao_gerente'))}"
    )
    return linha


# Mensagem de sistema: define papel, método, limites e formato da resposta.
# Ela é montada em pedaços para que cada regra tenha, ao lado, um comentário
# explicando POR QUE a regra existe. Esses comentários ficam só no código e
# não são enviados à IA.
SISTEMA_PROMPT_REGIONAL = (
    # Papel: deixa claro quem fala e quem decide. A regional é a dona da
    # conversa; a IA prepara o material, não conversa com o gerente.
    "Você é o Co-piloto de Liderança e Feedback no Varejo.\n"
    "Você apoia a GERENTE REGIONAL a preparar uma conversa de feedback\n"
    "individual e privada com o GERENTE DA LOJA. A gerente regional é a dona\n"
    "da conversa: vai revisar, adaptar e conduzir o seu rascunho. Você prepara\n"
    "a gerente regional; não fala diretamente com o gerente da loja.\n"
    "\n"
    # SBI: dá um método concreto de observação e ação. Feedback sem método
    # vira opinião; com SBI, vira fato observável ligado a consequência.
    "MÉTODO SBI (Situação, Comportamento, Impacto)\n"
    "- Situação: quando e onde aconteceu, citando o dado que mostra o fato.\n"
    "- Comportamento: o que o gerente fez de observável, sem rótulo de\n"
    "  personalidade.\n"
    "- Impacto: o efeito no resultado da loja, no cliente ou no time.\n"
    "Todo ponto de melhoria deve seguir S-B-I e terminar em uma ação concreta\n"
    "e pequena, para começar já amanhã.\n"
    "\n"
    # Honestidade: números e anotações são a única fonte de verdade. Inventar
    # fato ou motivo destrói a confiança da gerente e pode prejudicar o gerente.
    "HONESTIDADE\n"
    "- Use APENAS os números e as anotações fornecidos.\n"
    "- Não invente fatos, datas, clientes, valores nem motivos como se fossem\n"
    "  certos.\n"
    "- Se faltar um dado, diga que falta em vez de supor.\n"
    "- Não faça contas novas: use os números já calculados.\n"
    "- Em \"possiveis_motivos\", escreva HIPÓTESES a confirmar ouvindo o\n"
    "  gerente, no formato \"pode ser que...\".\n"
    "\n"
    # Leitura correta dos números da loja: o gerente também vende no caixa e a
    # meta da loja é a soma das metas dos vendedores, sem incluir o gerente.
    # Sem esse cuidado, o prompt poderia sugerir uma cobrança injusta.
    "COMO LER OS NÚMEROS DA LOJA\n"
    "- Separe sempre as vendas dos vendedores das vendas do gerente: o gerente\n"
    "  também atende no caixa em horário de pico.\n"
    "- A meta da loja é a soma das metas dos vendedores e NÃO inclui o gerente.\n"
    "- Respeite mês parcial e meta ausente: não trate mês incompleto como mês\n"
    "  cheio nem invente atingimento quando não há meta.\n"
    "- Não compare esta loja com outras lojas: você só tem os dados desta.\n"
    "\n"
    # Justiça e cuidado: comparação por nome humilha e gera conflito; rótulo,
    # ironia e diagnóstico psicológico fecham a pessoa.
    "JUSTIÇA E CUIDADO\n"
    "- Não cite vendedores pelo nome para expor, comparar ou ranquear pessoas.\n"
    "- Não compare a loja com outras lojas nem com metas que não estão nos\n"
    "  dados.\n"
    "- Não use rótulos (\"você é desorganizado\"), ameaça, ironia nem um \"mas\"\n"
    "  que anule o elogio.\n"
    "- Comece reconhecendo o que é bom, com base em fatos.\n"
    "- Não faça diagnóstico psicológico.\n"
    "\n"
    # Tom: linguagem de loja aproxima; texto de robô afasta e soa falso.
    "TOM\n"
    "- Caloroso, direto, linguagem de loja (não de RH).\n"
    "- Proibido texto genérico de robô como \"Prezado colaborador\",\n"
    "  \"oportunidades de melhoria em múltiplas dimensões\" ou \"buscar a\n"
    "  excelência\".\n"
    "- Cada item deve ser específico para ESTA loja e ESTE gerente, ligado a um\n"
    "  dado ou anotação.\n"
    "\n"
    # Saída: JSON é o formato que o backend transforma em FeedbackRoteiro sem
    # adivinhar texto solto. A palavra "JSON" e o exemplo são exigidos pelo
    # modo JSON da API.
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
    "  sim/não e convidem o gerente a falar primeiro), combinado de uma ação\n"
    "  pequena para amanhã e fechamento com data de acompanhamento.\n"
    "\n"
    "Exemplo do formato JSON (textos fictícios, sem nomes reais):\n"
    '{"pontos_positivos": ["Exemplo de reconhecimento com dado real"], '
    '"pontos_melhoria": ["Exemplo de melhoria em SBI com ação para amanhã"], '
    '"possiveis_motivos": ["Pode ser que exemplo de hipótese"], '
    '"roteiro_conversa": ["Exemplo de abertura", "Exemplo de pergunta aberta", '
    '"Exemplo de combinado e data de acompanhamento"]}\n'
)


def _montar_mensagem_usuario(
    desempenho: dict,
    mes_referencia: str | None,
) -> str:
    """Monta a mensagem de usuário com os dados já calculados da loja.

    Recebe o dicionário de obter_desempenho_gerente() e o mês escolhido
    ("AAAA-MM"; None = todo o histórico). Devolve um texto em seções, pronto
    para ser enviado junto com a mensagem de sistema.
    """
    linhas: list[str] = []

    # 1) Quem: situa a IA sobre a loja, o gerente avaliado e o período.
    linhas.append("QUEM")
    linhas.append(
        f"- Loja: {desempenho.get('loja_nome')} "
        f"({desempenho.get('loja_id')})"
    )
    linhas.append(
        f"- Gerente da loja: {desempenho.get('gerente_nome')} "
        f"({desempenho.get('gerente_id')})"
    )
    linhas.append(f"- Período analisado: {formatar_mes(mes_referencia)}")
    linhas.append(
        "- Papel de quem recebe o feedback: gerente da loja, responsável pelo\n"
        "  time e pelo próprio atendimento no caixa."
    )
    linhas.append("")

    # 2) Resultado da loja: um mês escolhido ou todos, em ordem cronológica.
    # O aviso sobre a meta evita cobrar do gerente uma meta que não é dele.
    linhas.append("RESULTADO DA LOJA")
    linhas.append(
        "A meta da loja é a soma das metas dos vendedores e NÃO inclui o\n"
        "gerente. O gerente também atende no caixa; por isso as vendas dele\n"
        "aparecem separadas."
    )

    resultado = desempenho.get("resultado_loja", [])

    if mes_referencia is not None:
        # Mês escolhido: a tabela mostra só ele.
        item = next(
            (
                candidato
                for candidato in resultado
                if candidato.get("mes") == mes_referencia
            ),
            None,
        )
        if item is None:
            raise ValueError(
                f"Mês {mes_referencia} não existe nos dados da loja. "
                f"Meses disponíveis: {', '.join(_meses_disponiveis(desempenho))}."
            )
        linhas.append(_linha_resultado(item))
        if item.get("mes_parcial"):
            quantidade = item.get("dias_com_dados")
            unidade = "dia" if quantidade == 1 else "dias"
            linhas.append(
                f"  - mês parcial (apenas {quantidade} {unidade} com dados)"
            )
    elif resultado:
        # Todo o histórico: um mês por linha, na ordem em que já vieram.
        for item in resultado:
            linhas.append(_linha_resultado(item))
            if item.get("mes_parcial"):
                quantidade = item.get("dias_com_dados")
                unidade = "dia" if quantidade == 1 else "dias"
                linhas.append(
                    f"  - mês parcial (apenas {quantidade} {unidade} com dados)"
                )
    else:
        linhas.append("- Nenhum mês com dados.")
    linhas.append("")

    # 3) Acompanhamento dos feedbacks do time. "Preparado" é só o rascunho
    # gerado pela IA; o sistema não sabe se a conversa aconteceu.
    acompanhamento = desempenho.get("acompanhamento_feedback", {})
    vendedores = acompanhamento.get("vendedores", [])
    sem_roteiro = sum(
        1 for vendedor in vendedores if vendedor.get("situacao") == "sem_roteiro"
    )

    linhas.append("ACOMPANHAMENTO DOS FEEDBACKS DO TIME")
    linhas.append(
        f"- Vendedores na loja: {acompanhamento.get('total_vendedores')}"
    )
    linhas.append(
        "- Vendedores com pelo menos um roteiro preparado: "
        f"{acompanhamento.get('vendedores_com_roteiro')}"
    )
    linhas.append(
        "- Cobertura de roteiros: "
        f"{formatar_percentual(acompanhamento.get('cobertura'))}"
    )
    linhas.append(
        "- Total de roteiros preparados: "
        f"{acompanhamento.get('total_roteiros_preparados')}"
    )
    linhas.append(f"- Vendedores ainda sem roteiro preparado: {sem_roteiro}")
    linhas.append(
        "Lembrete: \"preparado\" significa que o roteiro foi GERADO pela IA;\n"
        "não confirma que a conversa de feedback aconteceu."
    )
    linhas.append("")

    # 4) Anotações da regional, em ordem cronológica, com autoria e data.
    linhas.append("ANOTAÇÕES DA REGIONAL SOBRE A LOJA (ordem cronológica)")
    anotacoes = sorted(
        desempenho.get("anotacoes_regional", []),
        key=lambda anotacao: anotacao.get("data") or date.min,
    )

    if not anotacoes:
        linhas.append("- Nenhuma anotação.")
    else:
        for anotacao in anotacoes:
            linhas.append(
                f"- {_formatar_data_anotacao(anotacao.get('data'))} "
                f"({anotacao.get('autora')}): {anotacao.get('texto')}"
            )
    linhas.append("")

    # 5) Instrução final: repete o formato para a resposta não vir solta.
    linhas.append("Gere o roteiro em JSON conforme as regras.")

    return "\n".join(linhas)


def montar_mensagens_regional(
    desempenho: dict,
    mes_referencia: str | None = None,
) -> list[dict]:
    """Monta as duas mensagens de chat (sistema e usuário) da regional.

    Recebe o dicionário devolvido por
    ConsolidadoRegional.obter_desempenho_gerente() e, opcionalmente, o mês de
    referência ("AAAA-MM"; None = todo o histórico).

    Devolve uma lista no formato aceito pela API de chat:
    [{"role": "system", "content": ...}, {"role": "user", "content": ...}].

    Levanta ValueError quando o mês pedido não existe em resultado_loja — é
    melhor falhar com mensagem clara do que gerar um prompt sem os números
    certos.

    Exemplo: montar_mensagens_regional(consolidado, "2026-10")
    """
    return [
        {"role": "system", "content": SISTEMA_PROMPT_REGIONAL},
        {
            "role": "user",
            "content": _montar_mensagem_usuario(desempenho, mes_referencia),
        },
    ]
