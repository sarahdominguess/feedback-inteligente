"""Testes do servidor base: /health, erros, CORS e aquecimento.

Usam o app REAL (backend/main.py) com TestClient, que chama a API em
memória, sem abrir porta de rede.
"""

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from config import ENV_FRONTEND_ORIGINS, FRONTEND_ORIGINS_PADRAO
from endpoints.dependencias import obter_data_loader
from main import app, ler_origens_permitidas


class TestServidorBase(unittest.TestCase):
    """Testes da configuração geral do app."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente uma vez para todos os testes.

        Aqui NÃO usamos o TestClient como context manager: sem o `with`, o
        ciclo de vida (lifespan) não roda. É o que queremos nos testes de
        rota, para não carregar os CSVs a cada classe.
        """
        cls.client = TestClient(app)

    def test_health_continua_ok(self):
        """A rota /health segue respondendo {"status": "ok"}."""
        resposta = self.client.get("/health")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"status": "ok"})

    def test_rota_inexistente_404_com_corpo_de_erro(self):
        """Rota que não existe devolve 404 no formato {"erro": ...}."""
        resposta = self.client.get("/nao-existe")

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            resposta.json(), {"erro": "Recurso não encontrado."}
        )

    def test_post_em_health_devolve_405(self):
        """/health só aceita GET: POST devolve 405 com {"erro": ...}."""
        resposta = self.client.post("/health")

        self.assertEqual(resposta.status_code, 405)
        self.assertEqual(
            resposta.json(),
            {"erro": "Método não permitido para esta rota."},
        )

    def test_preflight_cors_libera_origem_do_vite(self):
        """O preflight (OPTIONS) da origem permitida recebe o cabeçalho.

        Preflight é o "pedido de permissão" que o navegador faz antes de uma
        chamada com método/cabeçalho diferentes do simples. O servidor precisa
        responder com access-control-allow-origin para o navegador liberar.
        """
        resposta = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.headers.get("access-control-allow-origin"),
            "http://localhost:5173",
        )

    def test_origem_estranha_nao_recebe_liberacao(self):
        """Origem fora da lista não ganha o cabeçalho de liberação."""
        resposta = self.client.options(
            "/health",
            headers={
                "Origin": "http://site-estranho.com",
                "Access-Control-Request-Method": "POST",
            },
        )

        self.assertNotIn("access-control-allow-origin", resposta.headers)


class TestLerOrigensPermitidas(unittest.TestCase):
    """Testes da leitura da variável FRONTEND_ORIGINS."""

    def test_variavel_vazia_usa_o_padrao(self):
        """Vazio = padrão do config (localhost e 127.0.0.1 na porta 5173)."""
        with patch.dict(os.environ, {ENV_FRONTEND_ORIGINS: ""}, clear=False):
            self.assertEqual(
                ler_origens_permitidas(), list(FRONTEND_ORIGINS_PADRAO)
            )

    def test_variavel_ausente_usa_o_padrao(self):
        """Variável inexistente também cai no padrão (sem erro)."""
        # patch.dict guarda uma cópia do ambiente e restaura tudo na saída,
        # inclusive o que for apagado aqui dentro.
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ENV_FRONTEND_ORIGINS, None)

            self.assertEqual(
                ler_origens_permitidas(), list(FRONTEND_ORIGINS_PADRAO)
            )

    def test_uma_origem(self):
        """Uma origem só vira uma lista de um item."""
        with patch.dict(
            os.environ,
            {ENV_FRONTEND_ORIGINS: "http://192.168.0.10:5173"},
            clear=False,
        ):
            self.assertEqual(
                ler_origens_permitidas(), ["http://192.168.0.10:5173"]
            )

    def test_duas_origens_com_espacos(self):
        """Vírgulas separam; espaços em volta são removidos."""
        with patch.dict(
            os.environ,
            {
                ENV_FRONTEND_ORIGINS: (
                    "http://localhost:5173 ,  http://192.168.0.10:5173 "
                )
            },
            clear=False,
        ):
            self.assertEqual(
                ler_origens_permitidas(),
                ["http://localhost:5173", "http://192.168.0.10:5173"],
            )


class TestAquecimento(unittest.TestCase):
    """Testes do lifespan (ciclo de vida) do servidor."""

    def test_subida_executa_o_aquecimento(self):
        """Usar o TestClient como context manager roda o lifespan sem erro.

        Dentro do `with`, o FastAPI executa o código antes do yield do
        lifespan — que é onde os CSVs são lidos uma vez (aquecimento).
        cache_info().currsize == 1 prova que o DataLoader compartilhado foi
        criado nesse momento.
        """
        obter_data_loader.cache_clear()

        with TestClient(app) as cliente:
            resposta = cliente.get("/health")
            self.assertEqual(resposta.status_code, 200)

        self.assertEqual(obter_data_loader.cache_info().currsize, 1)
