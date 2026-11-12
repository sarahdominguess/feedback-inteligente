"""Testes das rotas por loja da regional (Etapa 8).

Usam o app real, os CSVs reais e registros TEMPORÁRIOS (vendedores e gerente)
via dependency_overrides. Nenhum teste toca os arquivos reais de backend/data
nem chama a internet.
"""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from domain.feedback_roteiro import FeedbackRoteiro
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_data_loader,
    obter_registro_feedbacks,
    obter_registro_feedbacks_regional,
)
from main import app
from services.data_loader import DataLoader
from services.registro_feedback import RegistroFeedbackService
from services.registro_feedback_regional import RegistroFeedbackRegionalService


def roteiro_valido() -> FeedbackRoteiro:
    """Devolve um roteiro simples para os testes (conteúdo não importa aqui)."""
    return FeedbackRoteiro(
        pontos_positivos=["Loja organizada e time engajado"],
        pontos_melhoria=["Delegar o caixa no horário de pico"],
        possiveis_motivos=["Movimento concentrado no almoço"],
        roteiro_conversa=["Como foi a semana com o time?"],
    )


class TestRotasPorLojaDaRegional(unittest.TestCase):
    """Testes de GET /lojas e GET /lojas/{loja_id}/historico."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente do app real uma vez."""
        cls.client = TestClient(app)

    def setUp(self):
        """Registros temporários + DataLoader sem anotações novas da regional.

        O DataLoader sem serviços extras garante que os testes leem só os CSVs
        do desafio (5 anotações), independentemente do que existir no disco de
        dados de execução.
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)
        diretorio = Path(self._diretorio_temporario.name)

        self.registro_vendedores = RegistroFeedbackService(
            arquivo=diretorio / "registro_feedbacks.json"
        )
        self.registro_regional = RegistroFeedbackRegionalService(
            arquivo=diretorio / "registro_feedbacks_regional.json"
        )

        app.dependency_overrides[obter_data_loader] = lambda: DataLoader()
        app.dependency_overrides[obter_registro_feedbacks] = (
            lambda: self.registro_vendedores
        )
        app.dependency_overrides[obter_registro_feedbacks_regional] = (
            lambda: self.registro_regional
        )

        self.addCleanup(app.dependency_overrides.pop, obter_data_loader, None)
        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_feedbacks, None
        )
        self.addCleanup(
            app.dependency_overrides.pop,
            obter_registro_feedbacks_regional,
            None,
        )

        # Caches por par de dependências: limpar para o serviço novo valer.
        obter_consolidado_regional.cache_clear()
        obter_registro_feedbacks_regional.cache_clear()
        self.addCleanup(obter_consolidado_regional.cache_clear)
        self.addCleanup(obter_registro_feedbacks_regional.cache_clear)

    def _historico(self, loja_id: str = "L004") -> dict:
        """Chama a rota do histórico e devolve o JSON, exigindo status 200."""
        resposta = self.client.get(
            f"/api/regional/lojas/{loja_id}/historico"
        )
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()

    def test_lista_de_lojas_tem_a_l004_com_o_diego(self):
        """A lista traz exatamente a loja do desafio e o gerente dela."""
        resposta = self.client.get("/api/regional/lojas")

        self.assertEqual(resposta.status_code, 200, resposta.text)
        self.assertEqual(
            resposta.json(),
            {
                "lojas": [
                    {
                        "loja_id": "L004",
                        "loja_nome": "Aurora Shopping Centro",
                        "gerente_id": "C0030",
                        "gerente_nome": "Diego Furtado",
                    }
                ]
            },
        )

    def test_historico_traz_os_mesmos_numeros_da_rota_antiga(self):
        """O histórico repete os blocos da rota antiga e acrescenta a lista."""
        antigo = self.client.get("/api/regional/desempenho-gerente")
        self.assertEqual(antigo.status_code, 200, antigo.text)
        dados_antigos = antigo.json()

        dados = self._historico()

        for chave in (
            "gerente_id",
            "gerente_nome",
            "loja_id",
            "loja_nome",
            "periodo_inicio",
            "periodo_fim",
            "resultado_loja",
            "acompanhamento_feedback",
            "anotacoes_regional",
        ):
            with self.subTest(chave=chave):
                self.assertEqual(dados[chave], dados_antigos[chave])

        # Sem nenhum roteiro gravado, a lista existe e está vazia.
        self.assertEqual(dados["feedbacks_preparados"], [])

    def test_roteiro_do_gerente_aparece_no_historico(self):
        """Depois de registrar, o roteiro preparado entra no topo da lista."""
        registro = self.registro_regional.registrar(
            "L004",
            "Aurora Shopping Centro",
            "C0030",
            "Diego Furtado",
            "2026-10",
            roteiro_valido(),
        )

        dados = self._historico()

        self.assertEqual(len(dados["feedbacks_preparados"]), 1)
        item = dados["feedbacks_preparados"][0]
        self.assertEqual(item["feedback_id"], registro.feedback_id)
        self.assertEqual(item["mes_referencia"], "2026-10")
        self.assertEqual(
            item["roteiro"]["pontos_positivos"],
            ["Loja organizada e time engajado"],
        )

    def test_loja_minuscula_e_com_espacos_funcionam(self):
        """\"l004\" e \" L004 \" apontam para a mesma loja."""
        for loja_id in ("l004", " L004 "):
            with self.subTest(loja_id=loja_id):
                dados = self._historico(loja_id)
                self.assertEqual(dados["loja_id"], "L004")

    def test_loja_desconhecida_devolve_404(self):
        """Loja fora da configuração responde 404 com {\"erro\": ...}."""
        resposta = self.client.get(
            "/api/regional/lojas/L999/historico"
        )

        self.assertEqual(resposta.status_code, 404)
        corpo = resposta.json()
        self.assertIn("erro", corpo)
        self.assertIn("L999", corpo["erro"])

    def test_rota_antiga_continua_sem_a_lista_de_roteiros(self):
        """A rota antiga mantém o contrato antigo (sem feedbacks_preparados)."""
        resposta = self.client.get("/api/regional/desempenho-gerente")

        self.assertEqual(resposta.status_code, 200, resposta.text)
        self.assertNotIn("feedbacks_preparados", resposta.json())


if __name__ == "__main__":
    unittest.main()
