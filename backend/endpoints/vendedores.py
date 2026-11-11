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
from contracts.mapeadores import comparativo_de, metricas_de
from contracts.vendedores import ListaVendedoresResposta, VendedorResumoDTO
from domain.excecoes import LojaNaoEncontradaError
from endpoints.dependencias import obter_data_loader
from services.data_loader import DataLoader

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
