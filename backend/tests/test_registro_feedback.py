"""Testes do serviço que grava os roteiros gerados num arquivo JSON.

Todos usam um arquivo temporário (tempfile), nunca o registro real do
projeto: assim os testes não dependem nem alteram dados de execução.
"""

import json
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from domain.excecoes import DadosIndisponiveisError
from domain.feedback_roteiro import FeedbackRoteiro
from services.registro_feedback import RegistroFeedbackService


def roteiro_valido() -> FeedbackRoteiro:
    """Devolve um roteiro simples para os testes (conteúdo não importa aqui)."""
    return FeedbackRoteiro(
        pontos_positivos=["Bom atendimento às clientes"],
        pontos_melhoria=["Vender mais de uma peça por atendimento"],
        possiveis_motivos=["Correria no sábado"],
        roteiro_conversa=["Como foi o seu sábado mais cheio?"],
    )


class TestRegistroFeedbackService(unittest.TestCase):
    """Testes de leitura, gravação, persistência e concorrência do serviço."""

    def setUp(self):
        """Cria uma pasta temporária e um serviço apontando para um arquivo nela.

        TemporaryDirectory é apagada pelo próprio Python no fim do teste
        (registramos o cleanup com addCleanup).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.diretorio = Path(self._diretorio_temporario.name)
        self.arquivo = self.diretorio / "registro_feedbacks.json"
        self.service = RegistroFeedbackService(arquivo=self.arquivo)

    def test_arquivo_inexistente_devolve_lista_vazia(self):
        """Sem arquivo, a leitura devolve [] e não cria nada no disco.

        Arquivo ausente é o estado normal antes do primeiro roteiro; não é
        erro e nem deve criar um arquivo vazio à toa.
        """
        self.assertEqual(self.service.listar(), [])
        self.assertEqual(self.service.contar_por_vendedor(), {})
        self.assertIsNone(self.service.ultimo_de("C0031"))

        self.assertFalse(self.arquivo.exists())

    def test_registrar_e_listar_do_mais_novo_para_o_mais_antigo(self):
        """Três registros saem na ordem inversa da gravação (mais novo antes).

        Esperamos alguns milissegundos entre um registro e outro para o
        horário ser diferente de forma garantida.
        """
        primeiro = self.service.registrar(
            "C0031", "Bianca Rocha", None, roteiro_valido()
        )
        time.sleep(0.005)
        segundo = self.service.registrar(
            "C0031", "Bianca Rocha", "2026-10", roteiro_valido()
        )
        time.sleep(0.005)
        terceiro = self.service.registrar(
            "C0032", "Ana Silva", None, roteiro_valido()
        )

        registros = self.service.listar()

        self.assertEqual(
            [registro.feedback_id for registro in registros],
            [
                terceiro.feedback_id,
                segundo.feedback_id,
                primeiro.feedback_id,
            ],
        )
        # O horário é gravado com fuso UTC.
        self.assertIsNotNone(primeiro.gerado_em.tzinfo)

    def test_listar_filtra_por_vendedor(self):
        """O filtro devolve só os registros da pessoa pedida."""
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())
        self.service.registrar("C0032", "Ana Silva", None, roteiro_valido())
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())

        da_bianca = self.service.listar("C0031")

        self.assertEqual(len(da_bianca), 2)
        self.assertTrue(
            all(registro.vendedor_id == "C0031" for registro in da_bianca)
        )
        # Vendedor sem registro devolve lista vazia, não erro.
        self.assertEqual(self.service.listar("C9999"), [])

    def test_ultimo_de(self):
        """ultimo_de devolve o registro mais recente da pessoa (ou None)."""
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())
        time.sleep(0.005)
        recente = self.service.registrar(
            "C0031", "Bianca Rocha", "2026-10", roteiro_valido()
        )

        ultimo = self.service.ultimo_de("C0031")

        self.assertEqual(ultimo.feedback_id, recente.feedback_id)
        self.assertEqual(ultimo.mes_referencia, "2026-10")
        self.assertIsNone(self.service.ultimo_de("C9999"))

    def test_contar_por_vendedor(self):
        """A contagem agrupa por ID: 2 da Bianca e 1 da Ana."""
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())
        self.service.registrar("C0032", "Ana Silva", None, roteiro_valido())

        self.assertEqual(
            self.service.contar_por_vendedor(), {"C0031": 2, "C0032": 1}
        )

    def test_persistencia_entre_duas_instancias(self):
        """O segundo serviço lê o que o primeiro gravou (o dado fica no disco)."""
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())

        outro_service = RegistroFeedbackService(arquivo=self.arquivo)

        self.assertEqual(len(outro_service.listar()), 1)
        self.assertEqual(outro_service.listar()[0].vendedor_id, "C0031")

    def test_arquivo_corrompido_levanta_erro_e_preserva_conteudo(self):
        """JSON inválido dá erro claro e o arquivo não é apagado nem trocado."""
        conteudo_original = "isto não é um JSON!"
        self.arquivo.write_text(conteudo_original, encoding="utf-8")

        with self.assertRaises(DadosIndisponiveisError):
            self.service.listar()

        # Tentar registrar também falha e não sobrescreve o arquivo.
        with self.assertRaises(DadosIndisponiveisError):
            self.service.registrar(
                "C0031", "Bianca Rocha", None, roteiro_valido()
            )

        self.assertEqual(
            self.arquivo.read_text(encoding="utf-8"), conteudo_original
        )

    def test_formato_inesperado_levanta_erro(self):
        """JSON válido que não é uma lista (ex.: um objeto) também é recusado."""
        self.arquivo.write_text(
            json.dumps({"registros": []}), encoding="utf-8"
        )

        with self.assertRaises(DadosIndisponiveisError):
            self.service.listar()

    def test_nao_deixa_arquivo_temporario(self):
        """Depois de gravar, sobra só o arquivo oficial na pasta."""
        self.service.registrar("C0031", "Bianca Rocha", None, roteiro_valido())

        self.assertEqual(
            [caminho.name for caminho in self.diretorio.iterdir()],
            ["registro_feedbacks.json"],
        )

    def test_vinte_threads_registram_vinte_sem_perder_nenhum(self):
        """20 gravações simultâneas resultam em 20 registros no arquivo.

        O FastAPI atende pedidos em threads; sem o cadeado, duas gravações
        leriam a mesma lista e uma apagaria o registro da outra.
        """
        def registrar_um(indice: int) -> None:
            """Grava um registro com um ID de vendedor diferente."""
            self.service.registrar(
                f"C{indice:04d}",
                f"Pessoa {indice}",
                None,
                roteiro_valido(),
            )

        # ThreadPoolExecutor executa funções em várias threads de uma vez.
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(registrar_um, range(20)))

        registros = self.service.listar()

        self.assertEqual(len(registros), 20)
        self.assertEqual(sum(self.service.contar_por_vendedor().values()), 20)
