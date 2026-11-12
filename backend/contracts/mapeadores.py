"""Mapeadores: convertem entidades do domínio em DTOs da API.

Mapeador é uma camada de tradução: pega um objeto interno (Vendedor,
ComparativoTime, Anotacao...) e monta o formato que sai na API. Assim o
domínio continua independente do Pydantic e as rotas ficam finas.

Função pura: não guarda estado, não lê arquivo, não acessa a internet e não
muda nada no objeto recebido — o mesmo dado de entrada sempre produz a mesma
saída. Aqui também NÃO há cálculo de métrica: todos os números vêm dos
métodos do próprio domínio.
"""

from config import DIAS_MINIMOS_MES_COMPLETO
from contracts.feedback import FeedbackGerarResposta, FeedbackRoteiroDTO
from contracts.metricas import (
    MetricaComparadaDTO,
    MetricasDTO,
    ResumoMensalDTO,
)
from contracts.vendedores import AnotacaoDTO, FeedbackPreparadoDTO
from domain.anotacao import Anotacao
from domain.comparativo_time import ComparativoTime
from domain.excecoes import DadosIndisponiveisError
from domain.feedback_roteiro import FeedbackRoteiro
from domain.registro_feedback import RegistroFeedback
from domain.vendedor import Vendedor


def metricas_de(vendedor: Vendedor, mes: str | None = None) -> MetricasDTO:
    """Monta as métricas consolidadas de um vendedor num período.

    Recebe o vendedor e, opcionalmente, o mês ("AAAA-MM"); sem mês, usa todo
    o histórico. Cada número é pedido ao próprio Vendedor, então a regra de
    cálculo continua num lugar só (nada é recalculado aqui).

    Exemplo: metricas_de(bianca) devolve valor vendido, vendas, peças,
    atendimentos, ticket médio, P.A. e conversão de todo o histórico.
    """
    return MetricasDTO(
        valor_vendido=vendedor.valor_vendido(mes),
        vendas=vendedor.vendas(mes),
        pecas=vendedor.pecas(mes),
        atendimentos=vendedor.atendimentos(mes),
        ticket_medio=vendedor.ticket_medio(mes),
        pecas_por_atendimento=vendedor.pecas_por_atendimento(mes),
        conversao=vendedor.conversao(mes),
    )


def resumo_mensal_de(item: dict) -> ResumoMensalDTO:
    """Converte um item de Vendedor.resumo_mensal() no DTO da API.

    Recebe um dicionário já montado pelo domínio (mes, dias_com_dados,
    valor_vendido, vendas, pecas, atendimentos, ticket_medio,
    pecas_por_atendimento, conversao, meta, atingimento_meta).

    O campo mes_parcial não vem do domínio: ele é derivado aqui pela regra
    compartilhada de config (mês com menos de DIAS_MINIMOS_MES_COMPLETO dias
    com dados é parcial), a mesma usada no prompt enviado à IA.
    """
    return ResumoMensalDTO(
        mes=item["mes"],
        dias_com_dados=item["dias_com_dados"],
        # Menos dias que o mínimo => mês ainda em andamento ou incompleto.
        mes_parcial=item["dias_com_dados"] < DIAS_MINIMOS_MES_COMPLETO,
        valor_vendido=item["valor_vendido"],
        vendas=item["vendas"],
        pecas=item["pecas"],
        atendimentos=item["atendimentos"],
        ticket_medio=item["ticket_medio"],
        pecas_por_atendimento=item["pecas_por_atendimento"],
        conversao=item["conversao"],
        meta=item["meta"],
        atingimento_meta=item["atingimento_meta"],
    )


def comparativo_de(comparativo: ComparativoTime) -> list[MetricaComparadaDTO]:
    """Converte as métricas do comparativo com o time em DTOs.

    Recebe o ComparativoTime devolvido pelo DataLoader e devolve uma lista
    com as três métricas (ticket médio, P.A. e conversão), mantendo valor,
    média do time, diferença percentual, posição no ranking e situação.
    """
    return [
        MetricaComparadaDTO(
            nome=metrica.nome,
            valor=metrica.valor,
            media_time=metrica.media_time,
            diferenca_percentual=metrica.diferenca_percentual,
            posicao=metrica.posicao,
            total_vendedores=metrica.total_vendedores,
            situacao=metrica.situacao,
        )
        for metrica in comparativo.metricas
    ]


def anotacao_de(anotacao: Anotacao) -> AnotacaoDTO:
    """Converte uma anotação do gerente no DTO da API.

    Recebe a Anotacao do domínio e devolve data, sobre, texto e e_do_time.
    O campo e_do_time é uma propriedade do domínio (True quando "sobre" é
    "(time)"), então não é recalculado aqui.
    """
    return AnotacaoDTO(
        data=anotacao.data,
        sobre=anotacao.sobre,
        texto=anotacao.texto,
        e_do_time=anotacao.e_do_time,
    )


def roteiro_de(roteiro: FeedbackRoteiro) -> FeedbackRoteiroDTO:
    """Converte o roteiro gerado pela IA no DTO de resposta.

    Usa FeedbackRoteiro.para_dict(), que já devolve cópias das quatro listas:
    assim o DTO não compartilha listas com o objeto de domínio.
    """
    return FeedbackRoteiroDTO(**roteiro.para_dict())


def roteiro_do_registro(registro: RegistroFeedback) -> FeedbackRoteiroDTO:
    """Reconstrói o DTO do roteiro a partir do dicionário gravado.

    Recebe o RegistroFeedback (o "registro" é a marca, no arquivo, de que um
    roteiro existiu) e devolve o FeedbackRoteiroDTO, que é o formato que a API
    entrega.

    Por que esta função existe: a resposta do POST /api/feedback/gerar e os
    roteiros antigos do histórico precisam do MESMO formato. Uma conversão só
    evita duas versões que podem divergir com o tempo.

    Se o dicionário gravado estiver num formato que o domínio não aceita
    (arquivo editado à mão, por exemplo), levantamos DadosIndisponiveisError:
    é o mesmo erro que o RegistroFeedbackService usa ao ler um arquivo
    inválido, e o tratador global o transforma numa mensagem amigável em vez
    de um erro técnico com detalhes internos.
    """
    try:
        # de_dict confere que as quatro chaves são listas de textos e levanta
        # ValueError quando não são. O ValidationError do Pydantic também é
        # um ValueError, então o mesmo except cobre os dois casos.
        return roteiro_de(FeedbackRoteiro.de_dict(registro.roteiro))
    except ValueError as erro:
        raise DadosIndisponiveisError(
            "O registro de feedbacks tem um roteiro em formato inválido."
        ) from erro


def feedback_preparado_de(
    registro: RegistroFeedback,
) -> FeedbackPreparadoDTO:
    """Monta um roteiro preparado (com o conteúdo) para a lista do histórico.

    Recebe o RegistroFeedback gravado pelo serviço e devolve o identificador,
    o mês de referência, o horário e o CONTEÚDO do roteiro (as quatro
    listas) — o mesmo conteúdo que o POST da geração devolve, para o frontend
    mostrar os roteiros antigos sem um segundo formato.

    "Preparado" significa que o roteiro foi GERADO; não sabemos se a
    conversa aconteceu.

    Exemplo: feedback_preparado_de(registro).roteiro.pontos_positivos
    """
    return FeedbackPreparadoDTO(
        feedback_id=registro.feedback_id,
        mes_referencia=registro.mes_referencia,
        gerado_em=registro.gerado_em,
        roteiro=roteiro_do_registro(registro),
    )


def resposta_de_feedback(registro: RegistroFeedback) -> FeedbackGerarResposta:
    """Monta a resposta da geração de feedback a partir do registro gravado.

    Recebe o RegistroFeedback que acabou de ser salvo e devolve identidade,
    id, mês, horário e o roteiro em quatro listas. O roteiro é reconstruído
    com roteiro_do_registro, a MESMA conversão usada pelos roteiros antigos
    do histórico.

    Exemplo: resposta_de_feedback(registro).roteiro.roteiro_conversa
    """
    return FeedbackGerarResposta(
        feedback_id=registro.feedback_id,
        vendedor_id=registro.vendedor_id,
        vendedor_nome=registro.vendedor_nome,
        mes_referencia=registro.mes_referencia,
        gerado_em=registro.gerado_em,
        roteiro=roteiro_do_registro(registro),
    )
