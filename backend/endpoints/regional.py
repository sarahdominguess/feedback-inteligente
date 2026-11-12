"""Rota da visão executiva da regional.

A regional acompanha o desempenho da loja e a cobertura dos roteiros já
preparados. A rota é fina: só pede o consolidado pronto e devolve no formato
do contrato — nenhuma conta é feita aqui.
"""

from fastapi import APIRouter, Depends, Path

from config import LOJA_ID, REGIONAL_NOME
from contracts.erros import ErroResposta
from contracts.mapeadores import feedback_gerente_de, resposta_regional_de
from contracts.regional import (
    AnotacaoRegionalDTO,
    AnotacaoRegionalNovaRequisicao,
    DesempenhoGerenteResposta,
    FeedbackRegionalGerarRequisicao,
    FeedbackRegionalGerarResposta,
    HistoricoLojaResposta,
    ListaLojasResposta,
)
from domain.excecoes import LojaNaoEncontradaError
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_llm_service,
    obter_registro_anotacoes_regional,
    obter_registro_feedbacks_regional,
)
from services.consolidado_regional import ConsolidadoRegional
from services.llm_service import LLMService
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)
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


@router.post(
    "/regional/lojas/{loja_id}/anotacoes",
    response_model=AnotacaoRegionalDTO,
    # 201 = "criado": o padrão HTTP para um POST que cria um recurso novo.
    status_code=201,
    responses={
        400: {
            "model": ErroResposta,
            "description": (
                "Texto da anotação inválido (vazio, só com espaços ou acima "
                "do limite) ou corpo da requisição malformado."
            ),
        },
        404: {
            "model": ErroResposta,
            "description": "Loja não encontrada.",
        },
    },
)
def registrar_anotacao_da_loja(
    requisicao: AnotacaoRegionalNovaRequisicao,
    loja_id: str = Path(
        description='Código da loja (ex.: "L004").',
    ),
    registro_anotacoes: RegistroAnotacoesRegionalService = Depends(
        obter_registro_anotacoes_regional
    ),
) -> AnotacaoRegionalDTO:
    """Grava uma anotação nova da regional sobre a loja.

    Recebe o código da loja no caminho e, no corpo, APENAS o texto.
    O cliente NÃO manda a autora nem a data:
    - a autora é REGIONAL_NOME (config), porque não há login — quem usa a
      visão regional é sempre a Patrícia;
    - a data é o dia de hoje no SERVIDOR, para ninguém inventar a data.

    Fluxo:
    1) loja diferente da configurada => LojaNaoEncontradaError (404);
    2) o serviço apara os espaços, valida o limite e grava;
    3) devolve a anotação no DTO que já existe.

    Texto inválido => 400 pelo tratador global (AnotacaoInvalidaError).
    A rota é fina: validação e gravação ficam no serviço; aqui só orquestra.

    Exemplo: POST /api/regional/lojas/L004/anotacoes
    {"texto": "visitar a loja na sexta"} responde 201 com data, autora e texto.
    """
    # Normalização só para comparar; a resposta usa a autora do config.
    if loja_id.strip().upper() != LOJA_ID.upper():
        raise LojaNaoEncontradaError(
            f"Loja '{loja_id.strip()}' não encontrada."
        )

    anotacao = registro_anotacoes.registrar(
        texto=requisicao.texto,
        autora=REGIONAL_NOME,
    )

    return AnotacaoRegionalDTO(
        data=anotacao.data,
        autora=anotacao.autora,
        texto=anotacao.texto,
    )


@router.post(
    "/regional/feedback/gerar",
    response_model=FeedbackRegionalGerarResposta,
    responses={
        400: {
            "model": ErroResposta,
            "description": "Dados da requisição inválidos (ex.: mês errado).",
        },
        404: {
            "model": ErroResposta,
            "description": "Loja não encontrada.",
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
def gerar_feedback_do_gerente(
    requisicao: FeedbackRegionalGerarRequisicao,
    consolidado: ConsolidadoRegional = Depends(obter_consolidado_regional),
    llm: LLMService = Depends(obter_llm_service),
    registro: RegistroFeedbackRegionalService = Depends(
        obter_registro_feedbacks_regional
    ),
) -> FeedbackRegionalGerarResposta:
    """Gera o roteiro da regional para o gerente e grava o registro.

    Função `def` (e não `async def`) de propósito: a chamada à IA pode levar
    segundos. O FastAPI executa funções normais numa thread separada (o
    "pool de threads"), então o servidor continua atendendo outros pedidos
    enquanto esta espera. Se fosse `async def` com chamada bloqueante, o
    servidor inteiro ficaria parado durante a espera.

    Fluxo:
    1) valida a loja (desconhecida => 404, sem chamar a IA);
    2) obtém o consolidado já calculado (nenhuma conta na rota);
    3) pede o roteiro à IA;
    4) SÓ se o roteiro veio válido, grava no registro da regional;
    5) devolve a resposta no formato da API.

    Se a IA falhar, nada é gravado e o erro sobe para o tratador global
    (500/502/503 com mensagem em português).

    Exemplo: POST /api/regional/feedback/gerar
    {"loja_id": "L004", "mes_referencia": "2026-10"}
    """
    # 1) Valida a loja antes de gastar uma chamada de IA.
    if requisicao.loja_id.strip().upper() != LOJA_ID.upper():
        raise LojaNaoEncontradaError(
            f"Loja '{requisicao.loja_id}' não encontrada."
        )

    # 2) Dados já calculados pelo consolidado (o prompt regional usa esse
    #    mesmo dicionário; a rota não monta prompt nem métrica).
    desempenho = consolidado.obter_desempenho_gerente()

    # 3) Pede o roteiro. Erros da IA sobem daqui SEM nada ser gravado.
    roteiro = llm.gerar_roteiro_feedback_gerente(
        desempenho, requisicao.mes_referencia
    )

    # 4) Grava só depois de o roteiro estar validado pelo LLMService. Se a
    #    gravação falhar, o erro também sobe (melhor avisar do que esconder).
    registro_gravado = registro.registrar(
        loja_id=desempenho["loja_id"],
        loja_nome=desempenho["loja_nome"],
        gerente_id=desempenho["gerente_id"],
        gerente_nome=desempenho["gerente_nome"],
        mes_referencia=requisicao.mes_referencia,
        roteiro=roteiro,
    )

    # 5) Mesma conversão usada pelos roteiros antigos do histórico.
    return resposta_regional_de(registro_gravado)
