"""Testes dos contratos da visão regional.

Verificam a montagem completa da resposta, os campos que podem ser null, a
recusa de situações fora da lista, a recusa de NaN e a serialização de datas
no padrão ISO (o formato de texto que o frontend entende).
"""

import json
import unittest
from datetime import date, datetime, timezone

from pydantic import ValidationError

from contracts.regional import (
    AcompanhamentoFeedbackDTO,
    AcompanhamentoVendedorDTO,
    AnotacaoRegionalDTO,
    DesempenhoGerenteResposta,
    ResultadoLojaMesDTO,
)


def resultado_valido(**alteracoes) -> ResultadoLojaMesDTO:
    """Monta um resultado de loja válido, permitindo trocar campos nos testes."""
    dados = {
        "mes": "2026-10",
        "mes_parcial": False,
        "dias_com_dados": 27,
        "meta_loja": 317200.0,
        "vendas_loja": 108608.64,
        "atingimento_loja": 0.3424,
        "vendas_vendedores": 97693.01,
        "atingimento_vendedores": 0.308,
        "vendas_gerente": 10915.63,
        "participacao_gerente": 0.1005,
    }
    dados.update(alteracoes)
    return ResultadoLojaMesDTO(**dados)


def vendedor_valido(**alteracoes) -> AcompanhamentoVendedorDTO:
    """Monta um acompanhamento de vendedor válido para os testes."""
    dados = {
        "vendedor_id": "C0031",
        "nome": "Bianca Rocha",
        "anotacoes_do_gerente": 3,
        "ultima_anotacao_em": date(2026, 10, 8),
        "roteiros_preparados": 2,
        "ultimo_roteiro_em": datetime(
            2026, 11, 11, 14, 0, tzinfo=timezone.utc
        ),
        "situacao": "com_roteiro",
    }
    dados.update(alteracoes)
    return AcompanhamentoVendedorDTO(**dados)


def acompanhamento_valido() -> AcompanhamentoFeedbackDTO:
    """Monta o bloco de acompanhamento com um vendedor fictício."""
    return AcompanhamentoFeedbackDTO(
        total_vendedores=1,
        vendedores_com_roteiro=1,
        cobertura=1.0,
        total_roteiros_preparados=2,
        vendedores=[vendedor_valido()],
    )


class TestDesempenhoGerenteResposta(unittest.TestCase):
    """Testes do contrato completo da visão da regional."""

    def _criar_valida(self, **alteracoes) -> DesempenhoGerenteResposta:
        """Monta a resposta completa com dados fictícios."""
        dados = {
            "gerente_id": "C0030",
            "gerente_nome": "Diego Furtado",
            "loja_id": "L004",
            "loja_nome": "Aurora Shopping Centro",
            "periodo_inicio": date(2026, 8, 1),
            "periodo_fim": date(2026, 10, 31),
            "resultado_loja": [resultado_valido()],
            "acompanhamento_feedback": acompanhamento_valido(),
            "anotacoes_regional": [
                AnotacaoRegionalDTO(
                    data=date(2026, 8, 18),
                    autora="Patrícia Lemos",
                    texto="Loja organizada, vitrine no padrão.",
                )
            ],
        }
        dados.update(alteracoes)
        return DesempenhoGerenteResposta(**dados)

    def test_criacao_valida(self):
        """Todos os blocos são aceitos e os números chegam intactos."""
        resposta = self._criar_valida()

        self.assertEqual(resposta.gerente_id, "C0030")
        self.assertEqual(resposta.loja_id, "L004")
        self.assertEqual(len(resposta.resultado_loja), 1)
        self.assertEqual(resposta.resultado_loja[0].vendas_gerente, 10915.63)
        self.assertEqual(
            resposta.acompanhamento_feedback.vendedores[0].situacao,
            "com_roteiro",
        )

    def test_campos_opcionais_viram_null(self):
        """Onde falta dado, o JSON traz null (nunca NaN ou texto inventado).

        Testamos os pontos que podem faltar: meta do mês, participação do
        gerente, datas da última anotação e do último roteiro, e o período.
        """
        resultado = resultado_valido(
            meta_loja=None,
            atingimento_loja=None,
            participacao_gerente=None,
        )
        vendedor = vendedor_valido(
            ultima_anotacao_em=None,
            roteiros_preparados=0,
            ultimo_roteiro_em=None,
            situacao="sem_roteiro",
        )
        acompanhamento = AcompanhamentoFeedbackDTO(
            total_vendedores=1,
            vendedores_com_roteiro=0,
            cobertura=0.0,
            total_roteiros_preparados=0,
            vendedores=[vendedor],
        )
        resposta = self._criar_valida(
            periodo_inicio=None,
            periodo_fim=None,
            resultado_loja=[resultado],
            acompanhamento_feedback=acompanhamento,
        )

        dados = json.loads(resposta.model_dump_json())
        mes = dados["resultado_loja"][0]
        pessoa = dados["acompanhamento_feedback"]["vendedores"][0]

        self.assertIsNone(mes["meta_loja"])
        self.assertIsNone(mes["atingimento_loja"])
        self.assertIsNone(mes["participacao_gerente"])
        self.assertIsNone(pessoa["ultima_anotacao_em"])
        self.assertIsNone(pessoa["ultimo_roteiro_em"])
        self.assertIsNone(dados["periodo_inicio"])
        self.assertIsNone(dados["periodo_fim"])

    def test_datas_serializadas_em_texto_iso(self):
        """Datas viram "AAAA-MM-DD" e data com hora vira texto ISO com fuso."""
        resposta = self._criar_valida()

        dados = json.loads(resposta.model_dump_json())

        self.assertEqual(dados["periodo_inicio"], "2026-08-01")
        self.assertEqual(dados["anotacoes_regional"][0]["data"], "2026-08-18")
        self.assertEqual(
            dados["acompanhamento_feedback"]["vendedores"][0][
                "ultima_anotacao_em"
            ],
            "2026-10-08",
        )
        self.assertTrue(
            dados["acompanhamento_feedback"]["vendedores"][0][
                "ultimo_roteiro_em"
            ].startswith("2026-11-11T14:00:00")
        )


class TestValidacoesDosContratosRegionais(unittest.TestCase):
    """Testes das recusas: situação inválida e valores NaN."""

    def test_situacao_invalida_e_recusada(self):
        """Situação fora de com_roteiro/sem_roteiro levanta ValidationError."""
        with self.assertRaises(ValidationError):
            vendedor_valido(situacao="em_dia")

    def test_nan_e_recusado(self):
        """Valores NaN são recusados nos campos de fração e de dinheiro.

        NaN não existe em JSON; aceitá-lo quebraria a tela da regional.
        """
        with self.subTest(campo="cobertura"):
            with self.assertRaises(ValidationError):
                AcompanhamentoFeedbackDTO(
                    total_vendedores=8,
                    vendedores_com_roteiro=0,
                    cobertura=float("nan"),
                    total_roteiros_preparados=0,
                    vendedores=[],
                )

        with self.subTest(campo="vendas_loja"):
            with self.assertRaises(ValidationError):
                resultado_valido(vendas_loja=float("nan"))

        with self.subTest(campo="participacao_gerente"):
            with self.assertRaises(ValidationError):
                resultado_valido(participacao_gerente=float("nan"))
