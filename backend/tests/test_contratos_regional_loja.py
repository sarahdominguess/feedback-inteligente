"""Testes dos contratos da regional POR LOJA (Etapa 8).

Verificam os campos obrigatórios, os limites do texto da anotação, o formato do
mês, a herança do histórico, os mapeadores a partir de um registro sintético e
a serialização em JSON sem NaN.
"""

import json
import unittest
from datetime import date, datetime, timezone

from pydantic import ValidationError

from contracts.mapeadores import feedback_gerente_de, resposta_regional_de
from contracts.regional import (
    AnotacaoRegionalNovaRequisicao,
    DesempenhoGerenteResposta,
    FeedbackGerenteGeradoDTO,
    FeedbackRegionalGerarRequisicao,
    HistoricoLojaResposta,
    ListaLojasResposta,
    LojaResumoDTO,
)
from domain.feedback_roteiro import FeedbackRoteiro
from domain.registro_feedback_gerente import RegistroFeedbackGerente

# Reaproveita os blocos válidos do teste dos contratos da regional, para não
# duplicar os números fictícios.
from tests.test_contratos_regional import (
    acompanhamento_valido,
    resultado_valido,
)


def roteiro_valido() -> FeedbackRoteiro:
    """Devolve um roteiro simples para os testes (conteúdo não importa aqui)."""
    return FeedbackRoteiro(
        pontos_positivos=["Loja organizada e time engajado"],
        pontos_melhoria=["Delegar o caixa no horário de pico"],
        possiveis_motivos=["Movimento concentrado no almoço"],
        roteiro_conversa=["Como foi a semana com o time?"],
    )


def registro_sintetico(
    mes_referencia: str | None = "2026-10",
) -> RegistroFeedbackGerente:
    """Cria um RegistroFeedbackGerente válido para os testes dos mapeadores."""
    return RegistroFeedbackGerente(
        loja_id="L004",
        loja_nome="Aurora Shopping Centro",
        gerente_id="C0030",
        gerente_nome="Diego Furtado",
        gerado_em=datetime(2026, 11, 12, 14, 0, tzinfo=timezone.utc),
        mes_referencia=mes_referencia,
        roteiro=roteiro_valido().para_dict(),
    )


def historico_valido(**alteracoes) -> HistoricoLojaResposta:
    """Monta o histórico completo de uma loja, com um roteiro preparado."""
    dados = {
        "gerente_id": "C0030",
        "gerente_nome": "Diego Furtado",
        "loja_id": "L004",
        "loja_nome": "Aurora Shopping Centro",
        "periodo_inicio": date(2026, 8, 1),
        "periodo_fim": date(2026, 10, 31),
        "resultado_loja": [resultado_valido()],
        "acompanhamento_feedback": acompanhamento_valido(),
        "anotacoes_regional": [],
        "feedbacks_preparados": [
            FeedbackGerenteGeradoDTO(
                feedback_id="id-1",
                mes_referencia="2026-10",
                gerado_em=datetime(2026, 11, 12, 14, 0, tzinfo=timezone.utc),
                roteiro=roteiro_valido().para_dict(),
            )
        ],
    }
    dados.update(alteracoes)
    return HistoricoLojaResposta(**dados)


class TestContratosDeLoja(unittest.TestCase):
    """Testes dos contratos de lista de lojas e do histórico por loja."""

    def test_loja_resumo_valida_e_campos_obrigatorios(self):
        """A loja exige os quatro campos; faltando um, levanta ValidationError."""
        loja = LojaResumoDTO(
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            gerente_id="C0030",
            gerente_nome="Diego Furtado",
        )
        self.assertEqual(loja.loja_id, "L004")

        for campo in ("loja_id", "loja_nome", "gerente_id", "gerente_nome"):
            with self.subTest(campo=campo):
                incompleto = {
                    "loja_id": "L004",
                    "loja_nome": "Aurora Shopping Centro",
                    "gerente_id": "C0030",
                    "gerente_nome": "Diego Furtado",
                }
                del incompleto[campo]
                with self.assertRaises(ValidationError):
                    LojaResumoDTO(**incompleto)

    def test_lista_de_lojas(self):
        """A lista devolve as lojas na ordem recebida."""
        resposta = ListaLojasResposta(
            lojas=[
                LojaResumoDTO(
                    loja_id="L004",
                    loja_nome="Aurora Shopping Centro",
                    gerente_id="C0030",
                    gerente_nome="Diego Furtado",
                )
            ]
        )

        self.assertEqual(len(resposta.lojas), 1)
        self.assertEqual(resposta.lojas[0].loja_id, "L004")

    def test_historico_herda_o_consolidado_e_acrescenta_roteiros(self):
        """O histórico é um DesempenhoGerenteResposta com os roteiros do gerente."""
        historico = historico_valido()

        self.assertIsInstance(historico, DesempenhoGerenteResposta)
        self.assertEqual(historico.resultado_loja[0].mes, "2026-10")
        self.assertEqual(len(historico.feedbacks_preparados), 1)
        self.assertEqual(historico.feedbacks_preparados[0].feedback_id, "id-1")
        self.assertEqual(
            historico.feedbacks_preparados[0].roteiro.pontos_positivos,
            ["Loja organizada e time engajado"],
        )

    def test_historico_exige_a_lista_de_roteiros(self):
        """Sem feedbacks_preparados o contrato recusa: o campo é obrigatório."""
        with self.assertRaises(ValidationError):
            HistoricoLojaResposta(
                gerente_id="C0030",
                gerente_nome="Diego Furtado",
                loja_id="L004",
                loja_nome="Aurora Shopping Centro",
                resultado_loja=[],
                acompanhamento_feedback=acompanhamento_valido(),
                anotacoes_regional=[],
            )


class TestRequisicoesDaRegional(unittest.TestCase):
    """Testes das entradas: texto da anotação e pedido de geração."""

    def test_texto_da_anotacao_apara_as_pontas(self):
        """Espaços das pontas saem antes da contagem."""
        requisicao = AnotacaoRegionalNovaRequisicao(texto="  visitar a loja  ")

        self.assertEqual(requisicao.texto, "visitar a loja")

    def test_texto_vazio_ou_so_espacos_e_recusado(self):
        """Texto vazio e texto só com espaços falham na validação."""
        for texto in ("", "   \n\t "):
            with self.subTest(texto=repr(texto)):
                with self.assertRaises(ValidationError):
                    AnotacaoRegionalNovaRequisicao(texto=texto)

    def test_limite_do_texto(self):
        """1000 caracteres passam; 1001 são recusados."""
        no_limite = AnotacaoRegionalNovaRequisicao(texto="a" * 1000)
        self.assertEqual(len(no_limite.texto), 1000)

        with self.assertRaises(ValidationError):
            AnotacaoRegionalNovaRequisicao(texto="a" * 1001)

    def test_pedido_de_geracao_valida_e_apara_a_loja(self):
        """A loja é obrigatória e perde os espaços das pontas."""
        requisicao = FeedbackRegionalGerarRequisicao(
            loja_id="  L004  ", mes_referencia="2026-10"
        )

        self.assertEqual(requisicao.loja_id, "L004")
        self.assertEqual(requisicao.mes_referencia, "2026-10")

        # Sem mês, vale todo o histórico.
        sem_mes = FeedbackRegionalGerarRequisicao(loja_id="L004")
        self.assertIsNone(sem_mes.mes_referencia)

    def test_loja_vazia_e_recusada(self):
        """Sem loja, o pedido de geração não é aceito."""
        for loja_id in ("", "   "):
            with self.subTest(loja_id=repr(loja_id)):
                with self.assertRaises(ValidationError):
                    FeedbackRegionalGerarRequisicao(loja_id=loja_id)

    def test_mes_invalido_e_recusado(self):
        """Mês fora de "AAAA-MM" (ex.: 2026-13) levanta ValidationError."""
        for mes in ("2026-13", "2026/10", "outubro", "26-10"):
            with self.subTest(mes=mes):
                with self.assertRaises(ValidationError):
                    FeedbackRegionalGerarRequisicao(
                        loja_id="L004", mes_referencia=mes
                    )


class TestMapeadoresDaRegional(unittest.TestCase):
    """Testes dos mapeadores do registro do gerente para os DTOs."""

    def test_feedback_gerente_de(self):
        """O roteiro preparado leva id, mês, horário e as quatro listas."""
        registro = registro_sintetico()

        dto = feedback_gerente_de(registro)

        self.assertIsInstance(dto, FeedbackGerenteGeradoDTO)
        self.assertEqual(dto.feedback_id, registro.feedback_id)
        self.assertEqual(dto.mes_referencia, "2026-10")
        self.assertEqual(dto.gerado_em, registro.gerado_em)
        self.assertEqual(
            dto.roteiro.roteiro_conversa, ["Como foi a semana com o time?"]
        )

    def test_feedback_gerente_de_sem_mes(self):
        """Roteiro de todo o histórico mantém mes_referencia nulo."""
        dto = feedback_gerente_de(registro_sintetico(mes_referencia=None))

        self.assertIsNone(dto.mes_referencia)

    def test_resposta_regional_de(self):
        """A resposta da geração traz identidade da loja e do gerente."""
        registro = registro_sintetico()

        resposta = resposta_regional_de(registro)

        self.assertEqual(resposta.feedback_id, registro.feedback_id)
        self.assertEqual(resposta.loja_id, "L004")
        self.assertEqual(resposta.loja_nome, "Aurora Shopping Centro")
        self.assertEqual(resposta.gerente_id, "C0030")
        self.assertEqual(resposta.gerente_nome, "Diego Furtado")
        self.assertEqual(resposta.mes_referencia, "2026-10")
        self.assertEqual(
            resposta.roteiro.pontos_melhoria,
            ["Delegar o caixa no horário de pico"],
        )

    def test_roteiro_do_registro_do_gerente_reaproveita_a_conversao(self):
        """O mapeador usa a mesma conversão do registro dos vendedores.

        O teste confirma o contrato observável: o roteiro do DTO é igual ao
        dicionário gravado, com as quatro listas.
        """
        registro = registro_sintetico()

        dto = feedback_gerente_de(registro)

        self.assertEqual(
            dto.roteiro.model_dump(), registro.roteiro
        )


class TestSerializacaoJson(unittest.TestCase):
    """Testes da saída JSON: datas em texto ISO e nenhum NaN."""

    def test_json_do_historico_nao_tem_nan(self):
        """O histórico serializa com null onde falta dado, nunca NaN."""
        historico = historico_valido(
            periodo_inicio=None,
            periodo_fim=None,
            resultado_loja=[
                resultado_valido(
                    meta_loja=None,
                    atingimento_loja=None,
                    participacao_gerente=None,
                )
            ],
        )

        texto = historico.model_dump_json()
        dados = json.loads(texto)

        self.assertNotIn("NaN", texto)
        self.assertIsNone(dados["resultado_loja"][0]["meta_loja"])
        self.assertIsNone(dados["periodo_inicio"])
        self.assertEqual(
            dados["feedbacks_preparados"][0]["mes_referencia"], "2026-10"
        )
        # Data com hora sai em texto ISO com fuso.
        self.assertTrue(
            dados["feedbacks_preparados"][0]["gerado_em"].startswith(
                "2026-11-12T14:00:00"
            )
        )


if __name__ == "__main__":
    unittest.main()
