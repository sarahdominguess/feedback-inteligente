"""Rota da visão executiva da regional.

A regional acompanha o desempenho da loja e a cobertura dos roteiros já
preparados. A rota é fina: só pede o consolidado pronto e devolve no formato
do contrato — nenhuma conta é feita aqui.
"""

from fastapi import APIRouter, Depends

from config import LOJA_ID
from contracts.erros import ErroResposta
from contracts.mapeadores import feedback_gerente_de
from contracts.regional import (
    DesempenhoGerenteResposta,
    HistoricoLojaResposta,
    ListaLojasResposta,
)
from domain.excecoes import LojaNaoEncontradaError
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_registro_feedbacks_regional,
)
from services.consolidado_regional import ConsolidadoRegional
from services.registro_feedback_regional import (
    RegistroFeedbackRegionalService,
)

# Router com prefixo /api e etiqueta própria no Swagger.
router = APIRouter(prefix="/api", tags=["Regional"])


@router.get(
    "/regional/desempenho-gerente",
    response_model=DesempenhoGerenteResposta,
    responses={
        500: {
            "model": ErroResposta,
            "description": "Dados indisponíveis no servidor.",
        },
    },
)
def obter_desempenho_gerente(
    consolidado: ConsolidadoRegional = Depends(obter_consolidado_regional),
) -> DesempenhoGerenteResposta:
    """Devolve o consolidado da loja para a visão da regional.

    Recebe: nada além da dependência do consolidado (o FastAPI entrega).
    Devolve identidade do gerente/loja, período com dados, resultado mês a
    mês, acompanhamento dos roteiros preparados e anotações da regional.

    O consolidado usa o MESMO registro de feedbacks da rota de geração, então
    um roteiro recém-gerado já aparece aqui como "com_roteiro" — lembrando
    que o sistema só sabe que o roteiro foi GERADO, não que a conversa
    aconteceu.

    Exemplo: GET /api/regional/desempenho-gerente
    """
    # Montamos o contrato a partir do dicionário do serviço; o Pydantic
    # valida os campos e faz a resposta sair exatamente no formato combinado.
    return DesempenhoGerenteResposta(
        **consolidado.obter_desempenho_gerente()
    )


@router.get(
    "/regional/lojas",
    response_model=ListaLojasResposta,
    responses={
        500: {
            "model": ErroResposta,
            "description": "Dados indisponíveis no servidor.",
        },
    },
)
def listar_lojas(
    consolidado: ConsolidadoRegional = Depends(obter_consolidado_regional),
) -> ListaLojasResposta:
    """Lista as lojas que a regional pode acompanhar.

    Recebe: nada além da dependência do consolidado.
    Devolve: {"lojas": [...]}; hoje só a L004, mas o formato já aceita N
    lojas (o seletor da barra lateral foi feito para crescer).

    Exemplo: GET /api/regional/lojas
    """
    # Nenhuma conta aqui: a lista vem pronta do consolidado.
    return ListaLojasResposta(lojas=consolidado.listar_lojas())


@router.get(
    "/regional/lojas/{loja_id}/historico",
    response_model=HistoricoLojaResposta,
    responses={
        404: {
            "model": ErroResposta,
            "description": "Loja não encontrada.",
        },
        500: {
            "model": ErroResposta,
            "description": "Dados indisponíveis no servidor.",
        },
    },
)
def obter_historico_loja(
    loja_id: str,
    consolidado: ConsolidadoRegional = Depends(obter_consolidado_regional),
    registro_feedbacks: RegistroFeedbackRegionalService = Depends(
        obter_registro_feedbacks_regional
    ),
) -> HistoricoLojaResposta:
    """Devolve o histórico de uma loja: consolidado + roteiros do gerente.

    Recebe o código da loja no caminho. A comparação ignora maiúsculas e
    espaços nas pontas ("l004" e " L004 " valem "L004"); qualquer outra loja
    levanta LojaNaoEncontradaError, que o tratador global transforma em 404
    com {"erro": ...}.

    Devolve o MESMO conteúdo de GET /api/regional/desempenho-gerente e mais
    feedbacks_preparados, do mais novo para o mais antigo. "Preparado"
    significa GERADO; não sabemos se a conversa aconteceu.

    Exemplo: GET /api/regional/lojas/L004/historico
    """
    # Normalização só para COMPARAR; a resposta usa o código oficial do config.
    loja_normalizada = loja_id.strip().upper()

    if loja_normalizada != LOJA_ID.upper():
        raise LojaNaoEncontradaError(
            f"Loja '{loja_id.strip()}' não encontrada."
        )

    # Blocos já calculados (nenhuma conta nova nesta rota).
    dados = consolidado.obter_desempenho_gerente()

    # Roteiros PREPARADOS para o gerente, já do mais novo para o mais antigo
    # (a ordenação é do serviço; aqui só mapeamos para o contrato).
    roteiros = registro_feedbacks.listar(LOJA_ID)

    return HistoricoLojaResposta(
        **dados,
        feedbacks_preparados=[
            feedback_gerente_de(item) for item in roteiros
        ],
    )
