"""Dependências compartilhadas das rotas da API.

Dependência, no FastAPI: um objeto que a rota pede e o framework entrega
pronto ("injeção de dependência"). Na rota escrevemos
`data_loader: DataLoader = Depends(obter_data_loader)` e o FastAPI chama a
função por nós.

Singleton ("instância única"): uma só instância para todos os pedidos. O
DataLoader guarda cache dos CSVs e o serviço de registro guarda o cadeado
(lock) da gravação. Se cada pedido criasse um objeto novo, o cache seria
perdido e duas gravações poderiam usar cadeados diferentes, perdendo
registros. Por isso usamos functools.lru_cache: a primeira chamada cria, as
seguintes reaproveitam o mesmo objeto.

Nos testes, a rota pode ser testada com um falso sem tocar no código dela:
    app.dependency_overrides[obter_data_loader] = lambda: falso
E `obter_data_loader.cache_clear()` limpa o cache entre um teste e outro.
"""

from functools import lru_cache

from fastapi import Depends

from services.consolidado_regional import ConsolidadoRegional
from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.registro_anotacoes import RegistroAnotacoesService
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)
from services.registro_feedback import RegistroFeedbackService
from services.registro_feedback_regional import RegistroFeedbackRegionalService


@lru_cache(maxsize=1)
def obter_data_loader() -> DataLoader:
    """Devolve o DataLoader compartilhado por todas as rotas.

    lru_cache guarda o resultado da primeira chamada; com maxsize=1 e sem
    argumentos, funciona como singleton. A leitura dos CSVs continua
    preguiçosa: só acontece quando alguma rota pedir dados de verdade.

    O DataLoader recebe o serviço das anotações novas para que o histórico,
    o prompt da IA e a visão regional enxerguem o que o gerente escreveu na
    interface, sem alterar os CSVs de origem. O serviço da regional entra do
    mesmo jeito, para as anotações que a Patrícia escrever também aparecerem
    na visão dela.
    """
    return DataLoader(
        registro_anotacoes=obter_registro_anotacoes(),
        registro_anotacoes_regional=obter_registro_anotacoes_regional(),
    )


@lru_cache(maxsize=1)
def obter_registro_anotacoes() -> RegistroAnotacoesService:
    """Devolve o serviço das anotações novas, compartilhado por todas as rotas.

    Uma instância só garante o mesmo arquivo e o mesmo cadeado para todas as
    gravações — é o que evita dois pedidos simultâneos apagarem a anotação um
    do outro.
    """
    return RegistroAnotacoesService()


@lru_cache(maxsize=1)
def obter_registro_anotacoes_regional() -> RegistroAnotacoesRegionalService:
    """Devolve o serviço das anotações novas da regional, compartilhado.

    Mesma razão do serviço do gerente: uma instância só garante o mesmo
    arquivo e o mesmo cadeado (lock) para todas as gravações. Sem isso, dois
    pedidos simultâneos poderiam usar cadeados diferentes e um apagaria a
    anotação do outro.
    """
    return RegistroAnotacoesRegionalService()


@lru_cache(maxsize=1)
def obter_registro_feedbacks() -> RegistroFeedbackService:
    """Devolve o serviço de registro compartilhado.

    Uma instância só garante o mesmo arquivo e o mesmo cadeado para todas as
    gravações, que é o que evita dois pedidos apagarem o registro um do outro.
    """
    return RegistroFeedbackService()


@lru_cache(maxsize=1)
def obter_registro_feedbacks_regional() -> RegistroFeedbackRegionalService:
    """Devolve o serviço dos roteiros do gerente, compartilhado por todas.

    Mesma razão do serviço dos vendedores: uma instância só garante o mesmo
    arquivo e o mesmo cadeado, evitando que dois pedidos simultâneos apaguem
    o registro um do outro. É um serviço separado porque o arquivo também é
    separado (roteiros para o gerente não entram na cobertura do time).
    """
    return RegistroFeedbackRegionalService()


@lru_cache(maxsize=1)
def obter_llm_service() -> LLMService:
    """Devolve o LLMService compartilhado, usando o MESMO DataLoader.

    Reaproveitar o DataLoader evita ler os CSVs de novo para cada rota. A
    criação do serviço é barata e não abre conexão: a chave da API só é lida
    na primeira geração real de roteiro (leitura preguiçosa).
    """
    return LLMService(data_loader=obter_data_loader())


@lru_cache(maxsize=1)
def obter_consolidado_regional(
    data_loader: DataLoader = Depends(obter_data_loader),
    registro: RegistroFeedbackService = Depends(obter_registro_feedbacks),
) -> ConsolidadoRegional:
    """Devolve o consolidado da regional montado com as MESMAS dependências.

    Os parâmetros usam Depends de propósito: assim o FastAPI resolve o
    DataLoader e o registro do jeito normal (inclusive respeitando
    app.dependency_overrides nos testes). Com isso, o consolidado enxerga
    exatamente o MESMO registro usado pela rota de geração de feedback — sem
    isso, a regional não veria os roteiros recém-gerados.

    O lru_cache guarda o resultado por par de dependências: como as duas já
    são singletons, o consolidado também é único em uso normal.
    """
    return ConsolidadoRegional(
        data_loader=data_loader,
        registro=registro,
    )
