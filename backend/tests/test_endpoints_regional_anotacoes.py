"""Testes do endpoint POST /api/regional/lojas/{loja_id}/anotacoes.

Usam o app real e os CSVs reais, mas o serviço de anotações da regional aponta
para um arquivo TEMPORÁRIO (dependency_overrides). O DataLoader das rotas
recebe esse mesmo serviço — sem isso, o histórico leria outro arquivo e não
veria a anotação recém-gravada.

Nenhum teste toca no arquivo real de backend/data nem chama a internet.
"""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from config import ANOTACAO_TEXTO_MAXIMO
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_data_loader,
    obter_registro_anotacoes_regional,
    obter_registro_feedbacks,
    obter_registro_feedbacks_regional,
)
from main import app
from services.data_loader import DataLoader
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)
from services.registro_feedback import RegistroFeedbackService
from services.registro_feedback_regional import RegistroFeedbackRegionalService

# Caminho da rota, com um marcador para o código da loja.
ROTA_ANOTACOES = "/api/regional/lojas/{loja_id}/anotacoes"


class TestAnotacoesDaRegional(unittest.TestCase):
    """Testes de criação, leitura nas rotas da regional e erros."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente uma vez (o app real)."""
        cls.client = TestClient(app)

    def setUp(self):
        """Troca os serviços por versões temporárias e limpa os caches."""
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)
        diretorio = Path(self._diretorio_temporario.name)

        self.servico = RegistroAnotacoesRegionalService(
            arquivo=diretorio / "anotacoes_regional_novas.json"
        )
        self.registro_vendedores = RegistroFeedbackService(
            arquivo=diretorio / "registro_feedbacks.json"
        )
        self.registro_gerente = RegistroFeedbackRegionalService(
            arquivo=diretorio / "registro_feedbacks_regional.json"
        )

        # CSVs reais + serviço temporário de anotações da regional: é esse
        # loader que faz a anotação nova aparecer no histórico e na rota antiga.
        self.loader = DataLoader(registro_anotacoes_regional=self.servico)

        app.dependency_overrides[obter_data_loader] = lambda: self.loader
        app.dependency_overrides[obter_registro_anotacoes_regional] = (
            lambda: self.servico
        )
        app.dependency_overrides[obter_registro_feedbacks] = (
            lambda: self.registro_vendedores
        )
        app.dependency_overrides[obter_registro_feedbacks_regional] = (
            lambda: self.registro_gerente
        )

        self.addCleanup(app.dependency_overrides.pop, obter_data_loader, None)
        self.addCleanup(
            app.dependency_overrides.pop,
            obter_registro_anotacoes_regional,
            None,
        )
        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_feedbacks, None
        )
        self.addCleanup(
            app.dependency_overrides.pop,
            obter_registro_feedbacks_regional,
            None,
        )

        # O consolidado guarda o resultado em cache por par de dependências;
        # como o loader muda a cada teste, limpamos.
        obter_consolidado_regional.cache_clear()
        self.addCleanup(obter_consolidado_regional.cache_clear)

    def _postar(self, corpo, loja_id: str = "L004"):
        """Faz o POST na rota e devolve a resposta crua."""
        return self.client.post(
            ROTA_ANOTACOES.format(loja_id=loja_id),
            json=corpo,
        )

    def _historico(self) -> dict:
        """Busca o histórico da loja e devolve o JSON, exigindo 200."""
        resposta = self.client.get(
            "/api/regional/lojas/L004/historico"
        )
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()

    def test_cria_a_anotacao_e_devolve_201_com_o_contrato(self):
        """201 com exatamente data, autora e texto.

        A autora é a regional do config (não vem do corpo) e a data é a de
        hoje no servidor. O texto vai com espaços nas pontas para provar a
        limpeza antes de gravar.
        """
        antes = date.today()

        resposta = self._postar({"texto": "  visitar a loja na sexta  "})

        depois = date.today()

        self.assertEqual(resposta.status_code, 201, resposta.text)
        dados = resposta.json()

        self.assertEqual(set(dados), {"data", "autora", "texto"})
        self.assertEqual(dados["autora"], "Patrícia Lemos")
        self.assertIn(dados["data"], {antes.isoformat(), depois.isoformat()})
        self.assertEqual(dados["texto"], "visitar a loja na sexta")

    def test_anotacao_aparece_no_historico_da_loja(self):
        """Depois do POST, o histórico traz a nova (6 no total)."""
        antes = self._historico()["anotacoes_regional"]
        self.assertEqual(len(antes), 5)

        texto = "anotação que aparece no histórico"
        self._postar({"texto": texto})

        depois = self._historico()["anotacoes_regional"]
        textos = [anotacao["texto"] for anotacao in depois]

        self.assertEqual(len(depois), 6)
        self.assertIn(texto, textos)
        # As 5 do CSV continuam lá.
        for anotacao_antiga in antes:
            self.assertIn(anotacao_antiga["texto"], textos)

    def test_anotacao_aparece_na_rota_antiga(self):
        """A rota antiga da regional também enxerga a anotação nova."""
        texto = "anotação vista na rota antiga"
        self._postar({"texto": texto})

        resposta = self.client.get("/api/regional/desempenho-gerente")
        self.assertEqual(resposta.status_code, 200, resposta.text)

        anotacoes = resposta.json()["anotacoes_regional"]
        self.assertEqual(len(anotacoes), 6)
        self.assertIn(texto, [anotacao["texto"] for anotacao in anotacoes])

    def test_texto_vazio_devolve_400(self):
        """Texto vazio é recusado com 400 e nada é gravado."""
        resposta = self._postar({"texto": ""})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(self.servico.listar(), ())

    def test_texto_so_com_espacos_devolve_400(self):
        """Texto só com espaços vira vazio depois da limpeza e é recusado."""
        resposta = self._postar({"texto": "    "})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(self.servico.listar(), ())

    def test_texto_acima_do_limite_devolve_400(self):
        """Uma letra além de ANOTACAO_TEXTO_MAXIMO já é recusada."""
        resposta = self._postar(
            {"texto": "a" * (ANOTACAO_TEXTO_MAXIMO + 1)}
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertEqual(self.servico.listar(), ())

    def test_loja_desconhecida_devolve_404(self):
        """Loja fora da configuração responde 404 e não grava nada."""
        resposta = self._postar({"texto": "texto válido"}, loja_id="L999")

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("erro", resposta.json())
        self.assertIn("L999", resposta.json()["erro"])
        self.assertEqual(self.servico.listar(), ())

    def test_corpo_sem_texto_devolve_400(self):
        """Corpo {} não tem o campo obrigatório: 400, não 500."""
        resposta = self._postar({})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        self.assertIn("texto", resposta.json()["erro"])

    def test_texto_que_nao_e_string_devolve_400(self):
        """Número no lugar do texto também é recusado com 400."""
        resposta = self._postar({"texto": 123})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())

    def test_autora_e_data_enviadas_no_corpo_sao_ignoradas(self):
        """Campos a mais no corpo não mudam autora nem data.

        O contrato lê só o texto (os campos extras são ignorados), então o
        servidor continua gravando a autora do config e o dia de hoje.
        """
        antes = date.today()

        resposta = self._postar(
            {
                "texto": "texto normal",
                "autora": "Outra Pessoa",
                "data": "2000-01-01",
            }
        )

        depois = date.today()

        self.assertEqual(resposta.status_code, 201, resposta.text)
        dados = resposta.json()
        self.assertEqual(dados["autora"], "Patrícia Lemos")
        self.assertNotEqual(dados["data"], "2000-01-01")
        self.assertIn(dados["data"], {antes.isoformat(), depois.isoformat()})


if __name__ == "__main__":
    unittest.main()
