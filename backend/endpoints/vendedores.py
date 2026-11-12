"""Rotas dos vendedores da loja.

APIRouter: um "agrupador de rotas" do FastAPI. Criamos o router com um
prefixo comum (/api) e uma etiqueta (tag) que aparece no Swagger, e depois o
main.py inclui esse router no app. Assim as rotas de vendedores ficam num
arquivo só, sem inchar o main.py.

A rota aqui é fina de propósito: ela só orquestra. Nenhum cálculo de métrica
e nenhum Pandas — os números vêm do DataLoader e do Vendedor, e a conversão
para o formato da API fica nos mapeadores.
"""

from fastapi import APIRouter, Depends, Path, Query

from config import LOJA_ID, LOJA_NOME
from contracts.erros import ErroResposta
from contracts.mapeadores import (
    anotacao_de,
    comparativo_de,
    feedback_preparado_de,
    metricas_de,
    resumo_mensal_de,
)
from contracts.vendedores import (
    AnotacaoDTO,
    AnotacaoNovaRequisicao,
    HistoricoVendedorResposta,
    ListaVendedoresResposta,
    VendedorResumoDTO,
)
from domain.excecoes import LojaNaoEncontradaError
from endpoints.dependencias import (
    obter_data_loader,
    obter_registro_anotacoes,
    obter_registro_feedbacks,
)
from services.data_loader import DataLoader
from services.registro_anotacoes import RegistroAnotacoesService
from services.registro_feedback import RegistroFeedbackService

# Router com prefixo /api: as rotas declaradas aqui começam com /api.
# tags=["Vendedores"] agrupa a rota na documentação automática.
router = APIRouter(prefix="/api", tags=["Vendedores"])

# Molde do mês aceito na query: quatro dígitos, hífen e mês de 01 a 12.
# Quem valida é a própria Query; se não casar, o FastAPI gera
# RequestValidationError, que o tratador global transforma em 400.
_PATTERN_MES = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get(
    "/vendedores/{loja_id}",
    response_model=ListaVendedoresResposta,
    responses={
        400: {
            "model": ErroResposta,
            "description": "Mês em formato inválido (use AAAA-MM).",
        },
        404: {
            "model": ErroResposta,
            "description": "Loja não encontrada.",
        },
    },
)
def listar_vendedores_da_loja(
    loja_id: str = Path(
        description='Código da loja (ex.: "L004").',
    ),
    mes: str | None = Query(
        default=None,
        pattern=_PATTERN_MES,
        description=(
            'Mês no formato "AAAA-MM" (ex.: "2026-10"). Sem valor, usa todo '
            "o histórico."
        ),
    ),
    data_loader: DataLoader = Depends(obter_data_loader),
) -> ListaVendedoresResposta:
    """Lista os vendedores da loja com métricas e comparativo com o time.

    Parâmetro de caminho: o trecho da URL entre chaves ({loja_id}); o FastAPI
    o entrega como argumento.
    Query: os pares "?nome=valor" no fim da URL; aqui, ?mes=AAAA-MM.

    Recebe o código da loja e, opcionalmente, o mês. Devolve a loja, o mês
    usado e a lista de vendedores (ordem do CSV, sem o gerente), cada um com
    as métricas do período e as três métricas comparadas com a média do time.

    Regras:
    - loja diferente da configurada (sem diferenciar maiúsculas) => 404;
    - mês fora de AAAA-MM => 400 pelo tratador global;
    - valores indisponíveis são null (nunca NaN).

    Exemplo: GET /api/vendedores/L004?mes=2026-10
    """
    # Comparação sem diferenciar maiúsculas/minúsculas: "l004" vale como
    # "L004". Qualquer outra loja não existe na nossa base.
    if loja_id.strip().upper() != LOJA_ID.upper():
        raise LojaNaoEncontradaError(f"Loja '{loja_id}' não encontrada.")

    # A rota só junta o que já existe: nenhuma fórmula é calculada aqui.
    vendedores = []
    for vendedor in data_loader.listar_vendedores():
        comparativo = data_loader.obter_comparativo_time(
            vendedor.vendedor_id, mes
        )
        vendedores.append(
            VendedorResumoDTO(
                vendedor_id=vendedor.vendedor_id,
                nome=vendedor.nome,
                cargo=vendedor.cargo,
                metricas=metricas_de(vendedor, mes),
                comparativo=comparativo_de(comparativo),
            )
        )

    # Devolvemos o código da loja na forma canônica (L004), mesmo que a URL
    # tenha vindo em minúsculas.
    return ListaVendedoresResposta(
        loja_id=LOJA_ID,
        loja_nome=LOJA_NOME,
        mes=mes,
        vendedores=vendedores,
    )


@router.get(
    "/vendedores/{vendedor_id}/historico",
    response_model=HistoricoVendedorResposta,
    responses={
        404: {
            "model": ErroResposta,
            "description": "Vendedor não encontrado.",
        },
    },
)
def obter_historico_do_vendedor(
    vendedor_id: str = Path(
        description='Código do vendedor (ex.: "C0031").',
    ),
    data_loader: DataLoader = Depends(obter_data_loader),
    registro: RegistroFeedbackService = Depends(obter_registro_feedbacks),
) -> HistoricoVendedorResposta:
    """Devolve o histórico completo de um vendedor.

    Esta rota tem DOIS segmentos depois de /vendedores ({vendedor_id} e
    "historico"), enquanto a lista usa UM ({loja_id}). São formatos
    diferentes, então o FastAPI não confunde uma com a outra.

    Recebe só o ID do vendedor (nome não vale aqui). Devolve:
    - identidade e loja;
    - métricas de todo o histórico e o resumo mês a mês;
    - comparativo com a média do time;
    - anotações do gerente SOBRE a pessoa e, separadamente, as do time;
    - roteiros já preparados para a pessoa (do mais novo para o mais antigo).

    ID desconhecido ou do gerente (C0030) => 404 pelo tratador global.

    Exemplo: GET /api/vendedores/C0031/historico
    """
    # obter_vendedor devolve VendedorNaoEncontradoError para ID inexistente
    # ou que pertence ao gerente; não capturamos para o handler global
    # responder 404 com mensagem clara.
    vendedor = data_loader.obter_vendedor(vendedor_id)

    # Anotações SOBRE a pessoa (sem as do time) e anotações do time inteiro.
    anotacoes = [
        anotacao_de(anotacao)
        for anotacao in data_loader.obter_anotacoes_do_vendedor(vendedor_id)
    ]
    anotacoes_do_time = [
        anotacao_de(anotacao)
        for anotacao in data_loader.obter_gerente().anotacoes_do_time()
    ]

    # Roteiros já preparados: listar() já devolve do mais novo para o mais
    # antigo. O texto do roteiro não entra no histórico, só o resumo.
    feedbacks_preparados = [
        feedback_preparado_de(registro_gravado)
        for registro_gravado in registro.listar(vendedor_id)
    ]

    return HistoricoVendedorResposta(
        vendedor_id=vendedor.vendedor_id,
        nome=vendedor.nome,
        cargo=vendedor.cargo,
        loja_id=vendedor.loja_id,
        loja_nome=vendedor.loja_nome,
        metricas=metricas_de(vendedor),
        resumo_mensal=[
            resumo_mensal_de(item) for item in vendedor.resumo_mensal()
        ],
        comparativo=comparativo_de(
            data_loader.obter_comparativo_time(vendedor.vendedor_id)
        ),
        anotacoes=anotacoes,
        anotacoes_do_time=anotacoes_do_time,
        feedbacks_preparados=feedbacks_preparados,
    )


@router.post(
    "/vendedores/{vendedor_id}/anotacoes",
    response_model=AnotacaoDTO,
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
        404: {
            "model": ErroResposta,
            "description": "Vendedor não encontrado.",
        },
    },
)
def registrar_anotacao_do_vendedor(
    requisicao: AnotacaoNovaRequisicao,
    vendedor_id: str = Path(
        description='Código do vendedor (ex.: "C0031").',
    ),
    data_loader: DataLoader = Depends(obter_data_loader),
    registro_anotacoes: RegistroAnotacoesService = Depends(
        obter_registro_anotacoes
    ),
) -> AnotacaoDTO:
    """Grava uma anotação nova sobre um vendedor e devolve o que foi salvo.

    Endpoint: um endereço da API que faz uma tarefa. Dependência (Depends): um
    objeto que o FastAPI entrega pronto para a rota — aqui, o DataLoader e o
    serviço de anotações, sempre os mesmos (singletons) em toda a aplicação.

    Recebe:
        vendedor_id: no caminho da URL (o trecho entre chaves).
        requisicao: no corpo, no formato AnotacaoNovaRequisicao — só o texto.

    O cliente NÃO manda a data nem o "sobre": a data é o dia de hoje no
    servidor (ninguém inventa data) e o "sobre" é o nome do vendedor
    encontrado pelo ID. Assim a anotação nunca fica na pessoa errada.

    Fluxo:
    1) procura o vendedor (ID desconhecido ou do gerente => 404);
    2) pede ao serviço para gravar (texto inválido => 400 pelo tratador
       global de AnotacaoInvalidaError);
    3) devolve a anotação convertida pelo mapeador que já existe.

    A rota é fina de propósito: validação e gravação ficam no serviço; aqui só
    orquestramos e convertemos para o DTO (o formato da resposta).

    Exemplo: POST /api/vendedores/C0031/anotacoes {"texto": "elogiou o caixa"}
    responde 201 {"data": "2026-11-12", "sobre": "Bianca Rocha",
    "texto": "elogiou o caixa", "e_do_time": false}.
    """
    # 1) VendedorNaoEncontradoError (ID inexistente ou gerente) vira 404 no
    #    tratador global, com a mesma mensagem usada pelo histórico.
    vendedor = data_loader.obter_vendedor(vendedor_id)

    # 2) O serviço apara os espaços, valida o limite e usa a data de hoje.
    anotacao = registro_anotacoes.registrar(
        sobre=vendedor.nome,
        texto=requisicao.texto,
    )

    # 3) Mesma conversão usada no histórico: um formato só para a anotação.
    return anotacao_de(anotacao)
