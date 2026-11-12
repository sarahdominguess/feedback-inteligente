"""Testes do endpoint POST /api/regional/anotacoes.

Usam o app real e os CSVs reais, mas o serviço das anotações NOVAS da regional
aponta para um arquivo TEMPORÁRIO, trocado via dependency_overrides. O
DataLoader usado pelas rotas também recebe esse serviço temporário — sem isso,
o GET /api/regional/desempenho-gerente leria o arquivo real e não veria a
anotação recém-gravada.

Nenhum teste toca no arquivo real (backend/data/anotacoes_regional_novas.json)
nem chama a internet: a gravação acontece só na pasta temporária.
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
)
from main import app
from services.data_loader import DataLoader
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)

# Caminhos das duas rotas usadas aqui: a que grava e a que lista tudo.
ROTA_ANOTACOES = "/api/regional/anotacoes"
ROTA_DESEMPENHO = "/api/regional/desempenho-gerente"


class TestAnotacoesDaRegional(unittest.TestCase):
    """Testes de criação e validação da rota de anotações da regional."""

    @classmethod
    def setUpClass(cls):
        """Cria o cliente uma vez (o app real, com as rotas de verdade)."""
        cls.client = TestClient(app)

    def setUp(self):
        """Troca os serviços por versões de teste, dentro de uma pasta temporária.

        dependency_overrides é o "gancho" do FastAPI para substituir uma
        dependência: a rota continua pedindo obter_registro_anotacoes_regional
        ou obter_data_loader, mas recebe os nossos objetos. No fim do teste,
        addCleanup remove as trocas (evita que um teste contamine o próximo).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.arquivo = (
            Path(self._diretorio_temporario.name)
            / "anotacoes_regional_novas.json"
        )
        self.servico = RegistroAnotacoesRegionalService(arquivo=self.arquivo)

        # CSVs reais (data_dir padrão) + serviço temporário da regional.
        self.loader = DataLoader(
            registro_anotacoes_regional=self.servico
        )

        app.dependency_overrides[obter_registro_anotacoes_regional] = (
            lambda: self.servico
        )
        app.dependency_overrides[obter_data_loader] = lambda: self.loader

        self.addCleanup(
            app.dependency_overrides.pop,
            obter_registro_anotacoes_regional,
            None,
        )
        self.addCleanup(app.dependency_overrides.pop, obter_data_loader, None)

        # O consolidado regional guarda o resultado em cache por par de
        # dependências; como o loader muda a cada teste, limpamos o cache para
        # o GET enxergar o serviço temporário deste teste.
        obter_consolidado_regional.cache_clear()
        self.addCleanup(obter_consolidado_regional.cache_clear)

    def _postar(self, texto):
        """Faz o POST na rota de anotações e devolve a resposta crua."""
        return self.client.post(ROTA_ANOTACOES, json={"texto": texto})

    def _anotacoes_da_regional(self) -> list[dict]:
        """Busca o desempenho e devolve só a lista de anotações da regional."""
        resposta = self.client.get(ROTA_DESEMPENHO)
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return resposta.json()["anotacoes_regional"]

    def test_post_valido_devolve_a_anotacao_criada(self):
        """Um texto válido vira 201 com data de hoje, autora padrão e texto.

        A data e a autora NÃO vêm do cliente: o servidor usa o dia de hoje e a
        autora padrão do config (não existe login).
        """
        hoje = date.today()

        resposta = self._postar("Visitar a loja na sexta-feira")

        self.assertEqual(resposta.status_code, 201, resposta.text)
        dados = resposta.json()

        # O formato é exatamente o do contrato: nenhum campo a mais.
        self.assertEqual(set(dados), {"data", "autora", "texto"})
        self.assertEqual(dados["data"], hoje.isoformat())
        self.assertEqual(dados["autora"], "Patrícia Lemos")
        self.assertEqual(dados["texto"], "Visitar a loja na sexta-feira")

        # A gravação aconteceu de verdade no arquivo temporário.
        self.assertTrue(self.arquivo.exists())

    def test_anotacao_nova_aparece_no_desempenho(self):
        """Depois do POST, o GET da regional lista a anotação nova.

        O CSV tem 5 anotações; com a nova, a lista passa a ter 6. Isso prova
        que a rota de gravação e a de leitura usam a MESMA fonte (o serviço
        temporário injetado no DataLoader).
        """
        texto = "Retomar a conversa de feedback com o time"

        criacao = self._postar(texto)
        self.assertEqual(criacao.status_code, 201, criacao.text)

        anotacoes = self._anotacoes_da_regional()

        self.assertEqual(len(anotacoes), 6)
        self.assertIn(
            {
                "data": date.today().isoformat(),
                "autora": "Patrícia Lemos",
                "texto": texto,
            },
            anotacoes,
        )

    def test_texto_vazio_ou_so_espacos_e_recusado(self):
        """Texto vazio ("" ou só espaços) responde 400 com {"erro": ...}.

        A validação vem do contrato: str_strip_whitespace tira os espaços das
        pontas e min_length=1 recusa o que sobra vazio. Nada é gravado.
        """
        for texto in ("", "   "):
            with self.subTest(texto=texto):
                resposta = self._postar(texto)

                self.assertEqual(resposta.status_code, 400, resposta.text)
                corpo = resposta.json()
                self.assertIn("erro", corpo)
                self.assertTrue(corpo["erro"])

        # Nenhuma anotação foi parar no arquivo temporário.
        self.assertEqual(self.servico.listar(), [])

    def test_texto_acima_do_limite_e_recusado(self):
        """Texto maior que o limite (1000 caracteres) responde 400 com {"erro"}."""
        resposta = self._postar("a" * (ANOTACAO_TEXTO_MAXIMO + 1))

        self.assertEqual(resposta.status_code, 400, resposta.text)
        corpo = resposta.json()
        self.assertIn("erro", corpo)
        self.assertTrue(corpo["erro"])

        # O limite é checado ANTES de gravar: nada foi salvo.
        self.assertEqual(self.servico.listar(), [])


if __name__ == "__main__":
    unittest.main()
