"""Rota da visão executiva da regional.

A regional acompanha o desempenho da loja e a cobertura dos roteiros já
preparados. A rota é fina: só pede o consolidado pronto e devolve no formato
do contrato — nenhuma conta é feita aqui.
"""

from fastapi import APIRouter, Depends

from contracts.erros import ErroResposta
from contracts.regional import DesempenhoGerenteResposta
from endpoints.dependencias import obter_consolidado_regional
from services.consolidado_regional import ConsolidadoRegional

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
