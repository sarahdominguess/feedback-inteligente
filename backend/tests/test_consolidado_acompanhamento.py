"""Testes do acompanhamento de feedbacks no consolidado regional.

Primeiro com stubs sintéticos (controlam cobertura, anotações e datas) e
depois com os CSVs reais + registro temporário (nenhum teste toca o registro
real do projeto).
"""

import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from contracts.regional import DesempenhoGerenteResposta
from domain.anotacao import Anotacao
from domain.feedback_roteiro import FeedbackRoteiro
from domain.registro_feedback import RegistroFeedback
from config import DATA_DIR
from services.consolidado_regional import ConsolidadoRegional
from services.data_loader import DataLoader
from services.registro_feedback import RegistroFeedbackService


class VendedorFalso:
    """Vendedor de mentira com apenas identidade (o bastante aqui)."""

    def __init__(self, vendedor_id: str, nome: str):
        self.vendedor_id = vendedor_id
        self.nome = nome


class LoaderFalso:
    """DataLoader de mentira: vendedores e anotações combinados."""

    def __init__(self, vendedores, anotacoes=None):
        self._vendedores = vendedores
        self._anotacoes = anotacoes or {}

    def listar_vendedores(self):
        """Devolve os vendedores na ordem combinada."""
        return list(self._vendedores)

    def obter_anotacoes_do_vendedor(self, vendedor_id: str):
        """Devolve as anotações daquela pessoa (tupla vazia se não houver)."""
        return tuple(self._anotacoes.get(vendedor_id, ()))


class RegistroFalso:
    """Registro de mentira: guarda registros em memória."""

    def __init__(self, registros=None):
        self._registros = list(registros or [])

    def listar(self, vendedor_id=None):
        """Sem filtro devolve todos; com filtro, só os da pessoa."""
        if vendedor_id is None:
            return list(self._registros)
        return [
            registro
            for registro in self._registros
            if registro.vendedor_id == vendedor_id
        ]


def registro_de(vendedor_id: str, quando: datetime) -> RegistroFeedback:
    """Cria um RegistroFeedback mínimo em memória, com o horário informado."""
    return RegistroFeedback(
        vendedor_id=vendedor_id,
        vendedor_nome=f"Pessoa {vendedor_id}",
        gerado_em=quando,
        roteiro={},
    )


def oito_vendedores() -> list[VendedorFalso]:
    """Devolve 8 vendedores falsos, na ordem C0001..C0008."""
    return [
        VendedorFalso(f"C{i:04d}", f"Pessoa {i}") for i in range(1, 9)
    ]


class TestAcompanhamentoComStubs(unittest.TestCase):
    """Testes das contas de cobertura com números controlados."""

    def test_sem_roteiros_e_ultima_anotacao(self):
        """Nenhum roteiro => cobertura 0; última anotação é a mais recente.

        A pessoa sem anotações fica com contagem 0 e data None.
        """
        anotacoes = {
            "C0001": (
                Anotacao(
                    data=date(2026, 8, 6),
                    sobre="Pessoa 1",
                    texto="primeira anotação",
                ),
                Anotacao(
                    data=date(2026, 10, 8),
                    sobre="Pessoa 1",
                    texto="última anotação",
                ),
            )
        }

        loader = LoaderFalso(
            [VendedorFalso("C0001", "Pessoa 1"), VendedorFalso("C0002", "Pessoa 2")],
            anotacoes,
        )
        consolidado = ConsolidadoRegional(loader, RegistroFalso())

        acompanhamento = consolidado.obter_acompanhamento_feedback()

        self.assertEqual(acompanhamento["total_vendedores"], 2)
        self.assertEqual(acompanhamento["vendedores_com_roteiro"], 0)
        self.assertEqual(acompanhamento["cobertura"], 0.0)
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 0)

        primeiro = acompanhamento["vendedores"][0]
        self.assertEqual(primeiro["anotacoes_do_gerente"], 2)
        self.assertEqual(primeiro["ultima_anotacao_em"], date(2026, 10, 8))
        self.assertEqual(primeiro["ultimo_roteiro_em"], None)
        self.assertEqual(primeiro["situacao"], "sem_roteiro")

        segundo = acompanhamento["vendedores"][1]
        self.assertEqual(segundo["anotacoes_do_gerente"], 0)
        self.assertIsNone(segundo["ultima_anotacao_em"])

    def test_cobertura_de_um_em_oito(self):
        """1 vendedor com 2 roteiros => cobertura 0,125 e total 2.

        O último roteiro é o mais recente entre os dois registros.
        """
        cedo = datetime(2026, 11, 1, 9, 0, tzinfo=timezone.utc)
        tarde = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)

        loader = LoaderFalso(oito_vendedores())
        registro = RegistroFalso(
            [registro_de("C0001", cedo), registro_de("C0001", tarde)]
        )
        consolidado = ConsolidadoRegional(loader, registro)

        acompanhamento = consolidado.obter_acompanhamento_feedback()

        self.assertEqual(acompanhamento["total_vendedores"], 8)
        self.assertEqual(acompanhamento["vendedores_com_roteiro"], 1)
        self.assertAlmostEqual(acompanhamento["cobertura"], 0.125)
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 2)

        primeiro = acompanhamento["vendedores"][0]
        self.assertEqual(primeiro["situacao"], "com_roteiro")
        self.assertEqual(primeiro["roteiros_preparados"], 2)
        self.assertEqual(primeiro["ultimo_roteiro_em"], tarde)

    def test_cobertura_de_oito_em_oito(self):
        """Todos com 1 roteiro => cobertura 1,0 e total 8."""
        quando = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
        registros = [
            registro_de(f"C{i:04d}", quando) for i in range(1, 9)
        ]

        consolidado = ConsolidadoRegional(
            LoaderFalso(oito_vendedores()), RegistroFalso(registros)
        )

        acompanhamento = consolidado.obter_acompanhamento_feedback()

        self.assertEqual(acompanhamento["vendedores_com_roteiro"], 8)
        self.assertEqual(acompanhamento["cobertura"], 1.0)
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 8)
        self.assertTrue(
            all(
                item["situacao"] == "com_roteiro"
                for item in acompanhamento["vendedores"]
            )
        )

    def test_ordem_dos_vendedores(self):
        """A lista segue a ordem do CSV (C0001, C0002, ...)."""
        consolidado = ConsolidadoRegional(
            LoaderFalso(oito_vendedores()), RegistroFalso()
        )

        ids = [
            item["vendedor_id"]
            for item in consolidado.obter_acompanhamento_feedback()[
                "vendedores"
            ]
        ]

        self.assertEqual(
            ids, [f"C{i:04d}" for i in range(1, 9)]
        )


class TestAcompanhamentoComDadosReais(unittest.TestCase):
    """Testes com os CSVs reais e um registro temporário."""

    def setUp(self):
        """Cria o consolidado real e um registro em pasta temporária."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.service = RegistroFeedbackService(
            arquivo=Path(self._diretorio_temporario.name)
            / "registro_feedbacks.json"
        )
        self.loader = DataLoader(data_dir=DATA_DIR)
        self.consolidado = ConsolidadoRegional(self.loader, self.service)

    def test_sem_roteiros_todos_ficam_sem_roteiro(self):
        """Registro vazio: 8 vendedores, cobertura 0 e nenhum com roteiro."""
        acompanhamento = self.consolidado.obter_acompanhamento_feedback()

        self.assertEqual(acompanhamento["total_vendedores"], 8)
        self.assertEqual(acompanhamento["vendedores_com_roteiro"], 0)
        self.assertEqual(acompanhamento["cobertura"], 0.0)
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 0)
        self.assertTrue(
            all(
                item["situacao"] == "sem_roteiro"
                for item in acompanhamento["vendedores"]
            )
        )

    def test_bianca_tem_tres_anotacoes_do_gerente(self):
        """A Bianca tem 3 anotações do Diego; a última é de 08/10/2026."""
        acompanhamento = self.consolidado.obter_acompanhamento_feedback()

        bianca = next(
            item
            for item in acompanhamento["vendedores"]
            if item["vendedor_id"] == "C0031"
        )

        self.assertEqual(bianca["anotacoes_do_gerente"], 3)
        self.assertEqual(bianca["ultima_anotacao_em"], date(2026, 10, 8))

    def test_cobertura_apos_registrar_um_roteiro(self):
        """Com 1 roteiro da Bianca, a cobertura vira 0,125 (1 de 8)."""
        self.service.registrar(
            "C0031",
            "Bianca Rocha",
            "2026-10",
            FeedbackRoteiro(
                pontos_positivos=["Alta conversão"],
                pontos_melhoria=["Oferecer mais peças"],
                possiveis_motivos=["Correria no sábado"],
                roteiro_conversa=["Como foi o sábado?"],
            ),
        )

        acompanhamento = self.consolidado.obter_acompanhamento_feedback()

        self.assertEqual(acompanhamento["vendedores_com_roteiro"], 1)
        self.assertEqual(acompanhamento["cobertura"], 0.125)
        self.assertEqual(acompanhamento["total_roteiros_preparados"], 1)

        bianca = next(
            item
            for item in acompanhamento["vendedores"]
            if item["vendedor_id"] == "C0031"
        )
        self.assertEqual(bianca["situacao"], "com_roteiro")
        self.assertEqual(bianca["roteiros_preparados"], 1)
        self.assertIsNotNone(bianca["ultimo_roteiro_em"])

    def test_desempenho_do_gerente_completo(self):
        """A resposta tem identidade, período, 4 meses e 5 anotações.

        E o dicionário é aceito direto pelo contrato Pydantic, sem conversão.
        """
        dados = self.consolidado.obter_desempenho_gerente()

        self.assertEqual(dados["gerente_id"], "C0030")
        self.assertEqual(dados["gerente_nome"], "Diego Furtado")
        self.assertEqual(dados["loja_id"], "L004")
        self.assertEqual(dados["loja_nome"], "Aurora Shopping Centro")

        self.assertEqual(dados["periodo_inicio"], date(2026, 8, 1))
        self.assertEqual(dados["periodo_fim"], date(2026, 11, 1))

        self.assertEqual(len(dados["resultado_loja"]), 4)
        self.assertEqual(len(dados["anotacoes_regional"]), 5)

        # As anotações da regional vêm em ordem cronológica.
        datas = [anotacao["data"] for anotacao in dados["anotacoes_regional"]]
        self.assertEqual(datas, sorted(datas))

        # O contrato aceita o dicionário exatamente como ele saiu.
        resposta = DesempenhoGerenteResposta(**dados)
        self.assertEqual(resposta.gerente_nome, "Diego Furtado")
