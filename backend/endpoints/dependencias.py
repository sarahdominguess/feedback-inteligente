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

from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.registro_feedback import RegistroFeedbackService


@lru_cache(maxsize=1)
def obter_data_loader() -> DataLoader:
    """Devolve o DataLoader compartilhado por todas as rotas.

    lru_cache guarda o resultado da primeira chamada; com maxsize=1 e sem
    argumentos, funciona como singleton. A leitura dos CSVs continua
    preguiçosa: só acontece quando alguma rota pedir dados de verdade.
    """
    return DataLoader()


@lru_cache(maxsize=1)
def obter_registro_feedbacks() -> RegistroFeedbackService:
    """Devolve o serviço de registro compartilhado.

    Uma instância só garante o mesmo arquivo e o mesmo cadeado para todas as
    gravações, que é o que evita dois pedidos apagarem o registro um do outro.
    """
    return RegistroFeedbackService()


@lru_cache(maxsize=1)
def obter_llm_service() -> LLMService:
    """Devolve o LLMService compartilhado, usando o MESMO DataLoader.

    Reaproveitar o DataLoader evita ler os CSVs de novo para cada rota. A
    criação do serviço é barata e não abre conexão: a chave da API só é lida
    na primeira geração real de roteiro (leitura preguiçosa).
    """
    return LLMService(data_loader=obter_data_loader())
