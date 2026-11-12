"""Testes do endpoint POST /api/vendedores/{vendedor_id}/anotacoes.

Usam o app real e os CSVs reais, mas o serviço de anotações aponta para um
arquivo TEMPORÁRIO, trocado via dependency_overrides. O DataLoader usado pelas
rotas também recebe esse serviço temporário — sem isso, o histórico leria outro
arquivo e não veria a anotação recém-gravada.

Nenhum teste toca no arquivo real de anotações nem chama a internet.
"""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from config import ANOTACAO_TEXTO_MAXIMO
from domain.excecoes import AnotacaoInvalidaError
from endpoints.dependencias import (
    obter_consolidado_regional,
    obter_data_loader,
    obter_registro_anotacoes,
)
from main import app
from services.data_loader import DataLoader
from services.registro_anotacoes import RegistroAnotacoesService

# Caminho da rota, com um marcador para o código do vendedor.
ROTA_ANOTACOES = "/api/vendedores/{vendedor_id}/anotacoes"


class TestAnotacoesDoVendedor(unittest.TestCase):
    """Testes de criação, leitura no histórico e erros da rota de anotações."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente uma vez (o app real)."""
        cls.client = TestClient(app)

    def setUp(self):
        """Troca o serviço de anotações e o DataLoader por versões de teste.

        dependency_overrides é o "gancho" do FastAPI para substituir uma
        dependência: a rota continua pedindo obter_registro_anotacoes e
        obter_data_loader, mas recebe os nossos objetos. No fim do teste,
        addCleanup remove as trocas.
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.arquivo = (
            Path(self._diretorio_temporario.name) / "anotacoes_novas.json"
        )
        self.servico = RegistroAnotacoesService(arquivo=self.arquivo)

        # CSVs reais (data_dir padrão) + serviço temporário.
        self.loader = DataLoader(registro_anotacoes=self.servico)

        app.dependency_overrides[obter_registro_anotacoes] = (
            lambda: self.servico
        )
        app.dependency_overrides[obter_data_loader] = lambda: self.loader

        self.addCleanup(
            app.dependency_overrides.pop, obter_registro_anotacoes, None
        )
        self.addCleanup(app.dependency_overrides.pop, obter_data_loader, None)

        # O consolidado regional guarda o resultado em cache por par de
        # dependências; como o loader muda a cada teste, limpamos o cache.
        obter_consolidado_regional.cache_clear()
        self.addCleanup(obter_consolidado_regional.cache_clear)

    def _postar(self, corpo, vendedor_id: str = "C0031"):
        """Faz o POST na rota de anotações e devolve a resposta crua."""
        return self.client.post(
            ROTA_ANOTACOES.format(vendedor_id=vendedor_id),
            json=corpo,
        )

    def _historico(self, vendedor_id: str = "C0031") -> dict:
        """Busca o histórico e devolve o JSON, exigindo status 200."""
        resposta = self.client.get(
            f"/api/vendedores/{vendedor_id}/historico"
        )
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()

    def _contagem_da_bianca_no_regional(self) -> int:
        """Quantas anotações do gerente a regional conta para a Bianca."""
        resposta = self.client.get("/api/regional/desempenho-gerente")
        self.assertEqual(resposta.status_code, 200, resposta.text)

        acompanhamento = resposta.json()["acompanhamento_feedback"]
        for item in acompanhamento["vendedores"]:
            if item["vendedor_id"] == "C0031":
                return item["anotacoes_do_gerente"]

        raise AssertionError("A Bianca não está no acompanhamento da regional.")

    # -----------------------------------------------------------------
    # Criação
    # -----------------------------------------------------------------

    def test_cria_a_anotacao_e_devolve_201_com_o_contrato(self):
        """201 + AnotacaoDTO: data de hoje, sobre = nome, texto aparado.

        O texto vai com espaços nas pontas de propósito, para provar que a
        limpeza acontece antes de gravar. A data NÃO é enviada pelo cliente.
        """
        antes = date.today()

        resposta = self._postar({"texto": "  cliente elogiou o atendimento  "})

        depois = date.today()

        self.assertEqual(resposta.status_code, 201, resposta.text)
        dados = resposta.json()

        # Exatamente os campos do AnotacaoDTO, nem mais nem menos.
        self.assertEqual(
            set(dados.keys()), {"data", "sobre", "texto", "e_do_time"}
        )

        # A data é a de hoje do servidor (aceita antes/depois para o caso
        # improvável de o teste rodar na virada da meia-noite).
        self.assertIn(dados["data"], {antes.isoformat(), depois.isoformat()})

        # O "sobre" vem do vendedor_id, não do corpo da requisição.
        self.assertEqual(dados["sobre"], "Bianca Rocha")
        self.assertEqual(dados["texto"], "cliente elogiou o atendimento")
        self.assertFalse(dados["e_do_time"])

    def test_historico_mostra_a_anotacao_nova_e_mantem_as_antigas(self):
        """Depois do POST, o histórico da Bianca traz a nova e as 3 originais."""
        antes = self._historico()["anotacoes"]
        self.assertEqual(len(antes), 3)

        self._postar({"texto": "anotação que aparece no histórico"})

        depois = self._historico()["anotacoes"]
        textos = [anotacao["texto"] for anotacao in depois]

        self.assertEqual(len(depois), len(antes) + 1)
        self.assertIn("anotação que aparece no histórico", textos)

        # As anotações do CSV continuam todas lá.
        for anotacao_antiga in antes:
            self.assertIn(anotacao_antiga["texto"], textos)

    def test_anotacao_nao_aparece_no_historico_de_outra_pessoa(self):
        """A anotação é sobre a Bianca; o histórico do Lucas não a mostra."""
        texto = "esta anotação é só da Bianca"
        self._postar({"texto": texto})

        textos_do_lucas = [
            anotacao["texto"]
            for anotacao in self._historico("C0032")["anotacoes"]
        ]

        self.assertNotIn(texto, textos_do_lucas)

    def test_duas_anotacoes_seguidas_mantem_a_ordem(self):
        """Duas gravações seguidas ficam na ordem em que foram feitas."""
        self._postar({"texto": "primeira anotação"})
        self._postar({"texto": "segunda anotação"})

        textos_gravados = [
            anotacao.texto for anotacao in self.servico.listar()
        ]
        self.assertEqual(
            textos_gravados, ["primeira anotação", "segunda anotação"]
        )

        # No histórico, as novas vêm depois das do CSV e na ordem acima.
        textos_do_historico = [
            anotacao["texto"] for anotacao in self._historico()["anotacoes"]
        ]
        self.assertEqual(
            textos_do_historico[-2:], ["primeira anotação", "segunda anotação"]
        )

    # -----------------------------------------------------------------
    # Erros de "não encontrado"
    # -----------------------------------------------------------------

    def test_vendedor_inexistente_devolve_404(self):
        """ID que não existe responde 404 com a chave "erro"."""
        resposta = self._postar({"texto": "texto válido"}, vendedor_id="C9999")

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("erro", resposta.json())
        self.assertEqual(self.servico.listar(), ())

    def test_gerente_devolve_404(self):
        """O gerente (C0030) não é vendedor, então também dá 404."""
        resposta = self._postar({"texto": "texto válido"}, vendedor_id="C0030")

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("erro", resposta.json())
        self.assertEqual(self.servico.listar(), ())

    # -----------------------------------------------------------------
    # Erros de validação (400)
    # -----------------------------------------------------------------

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
        resposta = self._postar({"texto": "a" * (ANOTACAO_TEXTO_MAXIMO + 1)})

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())
        # A mensagem é em português, não o texto padrão em inglês do Pydantic.
        self.assertIn("texto muito longo", resposta.json()["erro"])
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

    def test_recusa_do_servico_vira_400_e_nao_500(self):
        """AnotacaoInvalidaError levantada pelo serviço sai como 400.

        O contrato já barra texto vazio/curto/longo antes de chegar ao
        serviço. Este teste cobre a REDE DE SEGURANÇA: se o serviço recusar
        algo por conta própria (ex.: uma regra nova no futuro), a rota não
        pode cair no tratador genérico de domínio, que responde 500.
        """
        mensagem = "A anotação foi recusada pela regra de teste."

        class ServicoQueRecusa:
            """Serviço falso que sempre recusa a gravação."""

            def registrar(self, sobre: str, texto: str):
                """Levanta a exceção de domínio em vez de gravar."""
                raise AnotacaoInvalidaError(mensagem)

            def listar(self):
                """Não guarda nada."""
                return ()

        # Troca só a dependência do serviço; o DataLoader segue o do setUp.
        app.dependency_overrides[obter_registro_anotacoes] = (
            lambda: ServicoQueRecusa()
        )

        resposta = self._postar({"texto": "texto que o contrato aceita"})

        self.assertEqual(resposta.status_code, 400, resposta.text)
        self.assertEqual(resposta.json()["erro"], mensagem)

    # -----------------------------------------------------------------
    # Formato do JSON e integração com a regional
    # -----------------------------------------------------------------

    def test_json_de_resposta_nao_tem_nan(self):
        """O corpo bruto não contém NaN/Infinity (JSON inválido para o JS)."""
        resposta = self._postar({"texto": "anotação normal"})

        self.assertEqual(resposta.status_code, 201)
        self.assertNotIn("NaN", resposta.text)
        self.assertNotIn("Infinity", resposta.text)

    def test_regional_mostra_uma_anotacao_a_mais(self):
        """A visão da regional passa a contar a anotação nova."""
        antes = self._contagem_da_bianca_no_regional()

        self._postar({"texto": "mais uma para a regional"})

        depois = self._contagem_da_bianca_no_regional()

        self.assertEqual(depois, antes + 1)

    def test_rota_aparece_na_documentacao_da_api(self):
        """A rota nova está registrada no app (aparece no /openapi.json).

        Endpoint: um endereço da API que faz uma tarefa. Este teste garante
        que o POST realmente foi incluído no roteador, e não só definido.
        """
        caminhos = app.openapi()["paths"]

        self.assertIn("/api/vendedores/{vendedor_id}/anotacoes", caminhos)
        self.assertIn(
            "post", caminhos["/api/vendedores/{vendedor_id}/anotacoes"]
        )

        # As rotas antigas continuam registradas.
        for caminho in (
            "/health",
            "/api/vendedores/{loja_id}",
            "/api/vendedores/{vendedor_id}/historico",
            "/api/feedback/gerar",
            "/api/regional/desempenho-gerente",
        ):
            self.assertIn(caminho, caminhos)


if __name__ == "__main__":
    unittest.main()
