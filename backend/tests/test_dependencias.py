"""Testes das dependências compartilhadas (singleton) da API.

Verificam que cada função devolve o tipo certo, que chamadas repetidas
devolvem o MESMO objeto e que o LLMService reaproveita o DataLoader.
Nenhum teste lê CSVs, chama a rede ou exige a chave da API.
"""

import unittest

from endpoints.dependencias import (
    obter_data_loader,
    obter_llm_service,
    obter_registro_feedbacks,
)
from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.registro_feedback import RegistroFeedbackService


class TestDependencias(unittest.TestCase):
    """Testes das funções usadas com Depends nas rotas."""

    def setUp(self):
        """Limpa o cache antes de cada teste, para isolar um teste do outro.

        cache_clear() é o "botão de reset" do lru_cache: a próxima chamada
        cria um objeto novo. Sem isso, um teste poderia reaproveitar o objeto
        criado por outro.
        """
        obter_data_loader.cache_clear()
        obter_registro_feedbacks.cache_clear()
        obter_llm_service.cache_clear()

        # Garantimos a limpeza também no fim, mesmo se o teste falhar.
        self.addCleanup(obter_data_loader.cache_clear)
        self.addCleanup(obter_registro_feedbacks.cache_clear)
        self.addCleanup(obter_llm_service.cache_clear)

    def test_cada_funcao_devolve_o_tipo_certo(self):
        """DataLoader, RegistroFeedbackService e LLMService, respectivamente."""
        self.assertIsInstance(obter_data_loader(), DataLoader)
        self.assertIsInstance(
            obter_registro_feedbacks(), RegistroFeedbackService
        )
        self.assertIsInstance(obter_llm_service(), LLMService)

    def test_duas_chamadas_devolvem_o_mesmo_objeto(self):
        """Singleton: a segunda chamada reaproveita a primeira instância.

        É isso que mantém o cache dos CSVs e o cadeado das gravações iguais
        para todas as rotas.
        """
        self.assertIs(obter_data_loader(), obter_data_loader())
        self.assertIs(
            obter_registro_feedbacks(), obter_registro_feedbacks()
        )
        self.assertIs(obter_llm_service(), obter_llm_service())

    def test_llm_service_usa_o_mesmo_data_loader(self):
        """O LLMService precisa receber a instância compartilhada do loader.

        Conferimos pelo atributo interno (_data_loader): ele é privado, mas é
        a única forma de provar a identidade sem criar uma API pública só
        para o teste.
        """
        servico = obter_llm_service()

        self.assertIs(servico._data_loader, obter_data_loader())

    def test_criar_llm_service_sem_chave_nao_levanta_erro(self):
        """Criar o serviço não exige chave nem abre conexão.

        A chave (DEEPSEEK_API_KEY) só é lida quando um roteiro é gerado de
        verdade; aqui o teste só confirma que a dependência pode ser montada.
        """
        servico = obter_llm_service()

        self.assertIsInstance(servico, LLMService)
