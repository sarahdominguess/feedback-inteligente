"""Testes do roteiro da regional para o gerente, com cliente falso.

Nenhuma chamada de rede: o cliente fake imita a SDK openai e guarda os
parâmetros enviados. Os dados da loja são sintéticos, no mesmo formato do
dicionário devolvido por ConsolidadoRegional.obter_desempenho_gerente().
"""

import json
import os
import unittest
from datetime import date
from unittest.mock import patch

from domain.excecoes import LLMRespostaInvalidaError
from domain.feedback_roteiro import FeedbackRoteiro
from services.data_loader import DataLoader
from services.llm_service import LLMService
from services.prompt_feedback_regional import montar_mensagens_regional

# Reaproveita o cliente falso e o JSON aprovado do teste do vendedor, para não
# duplicar as classes de dublê nem o conteúdo do roteiro.
from tests.test_llm_service import (
    ROTEIRO_JSON,
    FakeClient,
    FakeCompletions,
    FakeResposta,
)


def criar_desempenho_sintetico() -> dict:
    """Monta um consolidado fictício com um mês e dois vendedores.

    Bianca tem roteiro preparado; Ana não tem. As anotações entram fora de
    ordem de propósito, para o teste provar que o prompt as ordena.
    """
    return {
        "gerente_id": "C0030",
        "gerente_nome": "Diego Furtado",
        "loja_id": "L004",
        "loja_nome": "Aurora Shopping Centro",
        "periodo_inicio": date(2026, 10, 1),
        "periodo_fim": date(2026, 10, 31),
        "resultado_loja": [
            {
                "mes": "2026-10",
                "mes_parcial": False,
                "dias_com_dados": 27,
                "meta_loja": 317200.0,
                "vendas_loja": 320000.0,
                "atingimento_loja": 1.0,
                "vendas_vendedores": 309084.37,
                "atingimento_vendedores": 0.9,
                "vendas_gerente": 10915.63,
                "participacao_gerente": 0.033,
            }
        ],
        "acompanhamento_feedback": {
            "total_vendedores": 2,
            "vendedores_com_roteiro": 1,
            "cobertura": 0.5,
            "total_roteiros_preparados": 1,
            "vendedores": [
                {
                    "vendedor_id": "C0031",
                    "nome": "Bianca Rocha",
                    "situacao": "com_roteiro",
                },
                {
                    "vendedor_id": "C0032",
                    "nome": "Ana Silva",
                    "situacao": "sem_roteiro",
                },
            ],
        },
        "anotacoes_regional": [
            {
                "data": date(2026, 9, 15),
                "autora": "Patrícia Lemos",
                "texto": "A reunião matinal não aconteceu nas visitas.",
            }
        ],
    }


def roteiro_json_com_vendedora() -> str:
    """Copia o JSON válido e acrescenta um item que cita a vendedora.

    Simula a IA quebrando a regra de não expor pessoas; o validador deve
    reprovar e o serviço deve pedir UMA correção.
    """
    dados = json.loads(ROTEIRO_JSON)
    dados["pontos_positivos"].append(
        "A Bianca Rocha ajudou o time no sábado."
    )
    return json.dumps(dados, ensure_ascii=False)


class TestLLMServiceRegional(unittest.TestCase):
    """Testa o caminho do roteiro do gerente com um cliente falso."""

    def setUp(self):
        """Limpa as variáveis de modelo/thinking para não depender da máquina."""
        ambiente = patch.dict(
            os.environ,
            {"DEEPSEEK_MODEL": "", "DEEPSEEK_THINKING": ""},
        )
        ambiente.start()
        self.addCleanup(ambiente.stop)

        self.loader = DataLoader()
        self.desempenho = criar_desempenho_sintetico()

    def criar_servico(self, resposta=None, respostas=None):
        """Cria o serviço com FakeClient e devolve (serviço, completions)."""
        completions = FakeCompletions(resposta=resposta, respostas=respostas)
        servico = LLMService(
            data_loader=self.loader,
            client=FakeClient(completions),
        )
        return servico, completions

    def test_resposta_valida_vira_feedback_roteiro(self):
        """JSON aprovado vira FeedbackRoteiro com as quatro listas."""
        servico, _ = self.criar_servico(resposta=FakeResposta(ROTEIRO_JSON))

        roteiro = servico.gerar_roteiro_feedback_gerente(self.desempenho)

        self.assertIsInstance(roteiro, FeedbackRoteiro)
        esperado = json.loads(ROTEIRO_JSON)
        self.assertEqual(
            roteiro.pontos_positivos, esperado["pontos_positivos"]
        )
        self.assertEqual(
            roteiro.roteiro_conversa, esperado["roteiro_conversa"]
        )

    def test_mensagens_enviadas_sao_as_do_prompt_regional(self):
        """A chamada leva exatamente as mensagens de montar_mensagens_regional."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON)
        )

        servico.gerar_roteiro_feedback_gerente(self.desempenho, "2026-10")

        chamada = completions.chamadas[0]
        self.assertEqual(
            chamada["messages"],
            montar_mensagens_regional(self.desempenho, "2026-10"),
        )
        self.assertEqual(
            [mensagem["role"] for mensagem in chamada["messages"]],
            ["system", "user"],
        )
        # O prompt da regional cita o gerente e o nome da loja.
        usuario = chamada["messages"][1]["content"]
        self.assertIn("Diego Furtado", usuario)
        self.assertIn("Aurora Shopping Centro", usuario)
        self.assertIn("R$ 317.200,00", usuario)

    def test_parametros_da_api_sao_os_mesmos_do_vendedor(self):
        """Modo JSON, limites e thinking continuam iguais aos do outro caminho."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON)
        )

        servico.gerar_roteiro_feedback_gerente(self.desempenho)

        chamada = completions.chamadas[0]
        self.assertEqual(chamada["response_format"], {"type": "json_object"})
        self.assertEqual(
            chamada["extra_body"], {"thinking": {"type": "disabled"}}
        )
        self.assertEqual(
            [mensagem["role"] for mensagem in chamada["messages"]],
            ["system", "user"],
        )

    def test_json_invalido_levanta_excecao_existente(self):
        """Texto que não é JSON vira LLMRespostaInvalidaError."""
        servico, _ = self.criar_servico(
            resposta=FakeResposta("isto não é json")
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback_gerente(self.desempenho)

        self.assertIn("JSON válido", str(contexto.exception))

    def test_resposta_com_vendedora_e_corrigida_na_segunda(self):
        """1ª cita a Bianca; a 2ª corrigida passa, com exatamente 2 chamadas."""
        servico, completions = self.criar_servico(
            respostas=[
                FakeResposta(roteiro_json_com_vendedora()),
                FakeResposta(ROTEIRO_JSON),
            ]
        )

        roteiro = servico.gerar_roteiro_feedback_gerente(self.desempenho)

        self.assertIsInstance(roteiro, FeedbackRoteiro)
        self.assertEqual(len(completions.chamadas), 2)

        # A segunda chamada reenvia as mensagens originais + a resposta
        # anterior + o pedido de correção com o problema apontado.
        mensagens = completions.chamadas[1]["messages"]
        self.assertEqual(
            [mensagem["role"] for mensagem in mensagens],
            ["system", "user", "assistant", "user"],
        )
        correcao = mensagens[-1]["content"]
        self.assertIn("Bianca", correcao)
        self.assertIn("reprovado", correcao)

    def test_duas_respostas_reprovadas_geram_erro(self):
        """Se as duas citam a vendedora, o erro lista o problema."""
        servico, completions = self.criar_servico(
            respostas=[
                FakeResposta(roteiro_json_com_vendedora()),
                FakeResposta(roteiro_json_com_vendedora()),
            ]
        )

        with self.assertRaises(LLMRespostaInvalidaError) as contexto:
            servico.gerar_roteiro_feedback_gerente(self.desempenho)

        self.assertEqual(len(completions.chamadas), 2)
        self.assertIn("Bianca", str(contexto.exception))
        self.assertIn("duas tentativas", str(contexto.exception))

    def test_mes_inexistente_falha_antes_de_chamar_a_api(self):
        """Mês fora dos dados levanta ValueError sem gastar chamada."""
        servico, completions = self.criar_servico(
            resposta=FakeResposta(ROTEIRO_JSON)
        )

        with self.assertRaises(ValueError):
            servico.gerar_roteiro_feedback_gerente(
                self.desempenho, "2025-01"
            )

        self.assertEqual(completions.chamadas, [])


if __name__ == "__main__":
    unittest.main()
