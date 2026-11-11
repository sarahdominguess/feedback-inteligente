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
from contracts.feedback import FeedbackRoteiroDTO
from contracts.metricas import (
    MetricaComparadaDTO,
    MetricasDTO,
    ResumoMensalDTO,
)
from contracts.vendedores import AnotacaoDTO, FeedbackPreparadoDTO
from domain.anotacao import Anotacao
from domain.comparativo_time import ComparativoTime
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


def feedback_preparado_de(
    registro: RegistroFeedback,
) -> FeedbackPreparadoDTO:
    """Resume um registro de roteiro para a lista do histórico.

    Recebe o RegistroFeedback gravado pelo serviço e devolve só o
    identificador, o mês de referência e o horário. O CONTEÚDO do roteiro
    (as quatro listas) NÃO entra aqui: o histórico só precisa mostrar que
    existe um preparo, não repetir o texto.

    "Preparado" significa que o roteiro foi GERADO; não sabemos se a
    conversa aconteceu.
    """
    return FeedbackPreparadoDTO(
        feedback_id=registro.feedback_id,
        mes_referencia=registro.mes_referencia,
        gerado_em=registro.gerado_em,
    )
