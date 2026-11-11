"""Rotas de geração de feedback.

A rota recebe o vendedor (e, se quiser, um mês), pede o roteiro à IA e grava
o resultado no registro local. Ela é fina de propósito: não monta prompt,
não valida qualidade e não calcula métrica — isso tudo já vive nos serviços.
"""

from fastapi import APIRouter, Depends

from contracts.erros import ErroResposta
from contracts.feedback import FeedbackGerarRequisicao, FeedbackGerarResposta
from contracts.mapeadores import resposta_de_feedback
from endpoints.dependencias import (
    obter_data_loader,
    obter_llm_service,
    obter_registro_feedbacks,
)
from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.registro_feedback import RegistroFeedbackService

# Router com prefixo /api e etiqueta própria na documentação.
router = APIRouter(prefix="/api", tags=["Feedback"])


@router.post(
    "/feedback/gerar",
    response_model=FeedbackGerarResposta,
    responses={
        400: {
            "model": ErroResposta,
            "description": "Dados da requisição inválidos (ex.: mês errado).",
        },
        404: {
            "model": ErroResposta,
            "description": "Vendedor não encontrado.",
        },
        500: {
            "model": ErroResposta,
            "description": "IA não configurada ou falha ao gravar o registro.",
        },
        502: {
            "model": ErroResposta,
            "description": "A IA respondeu algo que não serve (JSON inválido).",
        },
        503: {
            "model": ErroResposta,
            "description": "Serviço de IA indisponível (tente mais tarde).",
        },
    },
)
def gerar_feedback(
    requisicao: FeedbackGerarRequisicao,
    data_loader: DataLoader = Depends(obter_data_loader),
    llm: LLMService = Depends(obter_llm_service),
    registro: RegistroFeedbackService = Depends(obter_registro_feedbacks),
) -> FeedbackGerarResposta:
    """Gera o roteiro de feedback de um vendedor e grava o registro.

    Função `def` (e não `async def`) de propósito: a chamada à IA pode levar
    segundos. O FastAPI executa funções normais numa thread separada (o
    "pool de threads"), então o servidor continua atendendo outros pedidos
    enquanto esta espera a resposta. Se fosse `async def` com uma chamada
    bloqueante, o servidor inteiro ficaria parado durante a espera.

    Fluxo:
    1) procura o vendedor (ID inexistente ou do gerente => 404, sem chamar a
       IA — economiza tempo e dinheiro);
    2) pede o roteiro à IA;
    3) SÓ se a IA devolveu um roteiro válido, grava no registro local;
    4) devolve a resposta no formato da API.

    Se a IA falhar, nada é gravado e o erro sobe para o tratador global
    (500/502/503 com mensagem em português).

    Exemplo: POST /api/feedback/gerar {"vendedor_id": "C0031", "mes_referencia": "2026-10"}
    """
    # 1) Valida a pessoa antes de gastar uma chamada de IA.
    vendedor = data_loader.obter_vendedor(requisicao.vendedor_id)

    # 2) Pede o roteiro. Erros da IA (sem chave, sem conexão, resposta ruim)
    # sobem daqui sem nada ser gravado.
    roteiro = llm.gerar_roteiro_feedback(
        vendedor.vendedor_id, requisicao.mes_referencia
    )

    # 3) Grava o registro. Se a gravação falhar (DadosIndisponiveisError),
    # deixamos o erro subir: é melhor avisar que o registro não foi salvo do
    # que esconder, porque sem ele a regional não consegue acompanhar os
    # feedbacks preparados.
    registro_gravado = registro.registrar(
        vendedor_id=vendedor.vendedor_id,
        vendedor_nome=vendedor.nome,
        mes_referencia=requisicao.mes_referencia,
        roteiro=roteiro,
    )

    # 4) Converte o registro gravado no contrato de resposta.
    return resposta_de_feedback(registro_gravado)
