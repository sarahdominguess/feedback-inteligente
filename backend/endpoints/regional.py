"""Rota da visão executiva da regional.

A regional acompanha o desempenho da loja e a cobertura dos roteiros já
preparados. A rota é fina: só pede o consolidado pronto e devolve no formato
do contrato — nenhuma conta é feita aqui.
"""

from fastapi import APIRouter, Depends

from contracts.erros import ErroResposta
from contracts.regional import (
    AnotacaoRegionalDTO,
    AnotacaoRegionalNovaRequisicao,
    DesempenhoGerenteResposta,
)
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_registro_anotacoes_regional,
)
from services.consolidado_regional import ConsolidadoRegional
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
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


@router.post(
    "/regional/anotacoes",
    response_model=AnotacaoRegionalDTO,
    # 201 = "criado": o padrão HTTP para quando um POST cria um recurso novo.
    status_code=201,
    responses={
        400: {
            "model": ErroResposta,
            "description": (
                "Texto da anotação inválido (vazio, só com espaços ou acima "
                "do limite) ou corpo da requisição malformado."
            ),
        },
        500: {
            "model": ErroResposta,
            "description": "Falha ao gravar o registro de anotações.",
        },
    },
)
def registrar_anotacao_regional(
    requisicao: AnotacaoRegionalNovaRequisicao,
    registro: RegistroAnotacoesRegionalService = Depends(
        obter_registro_anotacoes_regional
    ),
) -> AnotacaoRegionalDTO:
    """Grava uma anotação nova da regional e devolve o que foi salvo.

    A rota é fina de propósito: validação e gravação ficam no serviço; aqui só
    orquestramos e convertemos para o DTO (o formato da resposta).

    Recebe:
        requisicao: no corpo, no formato AnotacaoRegionalNovaRequisicao — só
            o texto.
        registro: injetado pelo FastAPI (o serviço é o mesmo de toda a
            aplicação, com um cadeado só).

    O cliente NÃO manda a data nem a autora: a data é o dia de hoje no
    servidor e a autora é a padrão do config (Patrícia Lemos). Texto inválido
    vira 400 pelo tratador global de AnotacaoInvalidaError.

    Exemplo: POST /api/regional/anotacoes {"texto": "visitar a loja"}
    responde 201 {"data": "2026-11-12", "autora": "Patrícia Lemos",
    "texto": "visitar a loja"}.
    """
    # Função `def` (e não `async def`): a gravação mexe em arquivo e pega um
    # cadeado. O FastAPI executa funções normais numa thread separada, então o
    # servidor continua atendendo outros pedidos.
    anotacao = registro.registrar(requisicao.texto)

    # Mesmo formato do item da lista em anotacoes_regional: um só para a tela.
    return AnotacaoRegionalDTO(
        data=anotacao.data,
        autora=anotacao.autora,
        texto=anotacao.texto,
    )
