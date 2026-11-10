"""Teste opcional da chamada real à DeepSeek (consome créditos).

Só roda quando as variáveis de ambiente RODAR_TESTES_LLM=1 e DEEPSEEK_API_KEY
estão definidas; sem isso aparece como "skipped" na suíte. Não roda por padrão
porque gasta créditos e depende de rede.
"""

import os
import unittest

from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.validador_feedback import validar_roteiro

# Estas duas checagens acontecem no carregamento do módulo. Se faltar uma
# delas, o unittest marca a classe inteira como pulada.
RODAR = os.environ.get("RODAR_TESTES_LLM") == "1"
TEM_CHAVE = bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())


@unittest.skipUnless(
    RODAR and TEM_CHAVE,
    "Defina RODAR_TESTES_LLM=1 e DEEPSEEK_API_KEY para chamar a IA real.",
)
class TestLLMReal(unittest.TestCase):
    """Chama a API de verdade uma vez e confere o roteiro da Bianca."""

    def test_gerar_roteiro_da_bianca(self):
        """O roteiro real deve ter as quatro listas e passar no validador."""
        loader = DataLoader()
        servico = LLMService(data_loader=loader)

        roteiro = servico.gerar_roteiro_feedback("C0031")

        self.assertTrue(roteiro.pontos_positivos)
        self.assertTrue(roteiro.pontos_melhoria)
        self.assertTrue(roteiro.possiveis_motivos)
        self.assertTrue(roteiro.roteiro_conversa)

        colegas = [
            vendedor.nome
            for vendedor in loader.listar_vendedores()
            if vendedor.vendedor_id != "C0031"
        ]

        self.assertEqual(
            validar_roteiro(roteiro, "Bianca Rocha", colegas), []
        )


if __name__ == "__main__":
    unittest.main()
