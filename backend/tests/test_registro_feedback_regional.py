"""Testes do serviço que grava os roteiros do gerente num arquivo JSON.

Todos usam arquivos temporários (tempfile), nunca os registros reais do
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
from services.registro_feedback_regional import RegistroFeedbackRegionalService


def roteiro_valido() -> FeedbackRoteiro:
    """Devolve um roteiro simples para os testes (conteúdo não importa aqui)."""
    return FeedbackRoteiro(
        pontos_positivos=["Loja organizada e time engajado"],
        pontos_melhoria=["Delegar o caixa no horário de pico"],
        possiveis_motivos=["Movimento concentrado no almoço"],
        roteiro_conversa=["Como foi a semana com o time?"],
    )


class TestRegistroFeedbackRegionalService(unittest.TestCase):
    """Testes de leitura, gravação, persistência e concorrência do serviço."""

    def setUp(self):
        """Cria uma pasta temporária e um serviço apontando para um arquivo nela.

        TemporaryDirectory é apagada pelo próprio Python no fim do teste
        (registramos o cleanup com addCleanup).
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        self.diretorio = Path(self._diretorio_temporario.name)
        self.arquivo = self.diretorio / "registro_feedbacks_regional.json"
        self.service = RegistroFeedbackRegionalService(arquivo=self.arquivo)

    def _registrar(self, loja_id: str = "L004", mes: str | None = None):
        """Atalho para registrar com os dados da loja do desafio.

        Devolve o RegistroFeedbackGerente criado.
        """
        return self.service.registrar(
            loja_id,
            "Aurora Shopping Centro",
            "C0030",
            "Diego Furtado",
            mes,
            roteiro_valido(),
        )

    def test_arquivo_inexistente_devolve_lista_vazia(self):
        """Sem arquivo, a leitura devolve [] e não cria nada no disco.

        Arquivo ausente é o estado normal antes do primeiro roteiro; não é
        erro e nem deve criar um arquivo vazio à toa.
        """
        self.assertEqual(self.service.listar(), [])
        self.assertIsNone(self.service.ultimo_de("L004"))

        self.assertFalse(self.arquivo.exists())

    def test_registrar_e_listar(self):
        """O registro gravado volta na leitura, com loja, gerente e roteiro.

        Lemos de uma instância NOVA para garantir que o dado ficou no disco.
        """
        self._registrar(mes="2026-10")

        outro_service = RegistroFeedbackRegionalService(arquivo=self.arquivo)
        registros = outro_service.listar()

        self.assertEqual(len(registros), 1)
        registro = registros[0]
        self.assertEqual(registro.loja_id, "L004")
        self.assertEqual(registro.loja_nome, "Aurora Shopping Centro")
        self.assertEqual(registro.gerente_id, "C0030")
        self.assertEqual(registro.gerente_nome, "Diego Furtado")
        self.assertEqual(registro.mes_referencia, "2026-10")
        self.assertEqual(
            registro.roteiro["pontos_positivos"],
            ["Loja organizada e time engajado"],
        )
        # O horário é gravado com fuso UTC.
        self.assertIsNotNone(registro.gerado_em.tzinfo)

    def test_listar_do_mais_novo_para_o_mais_antigo(self):
        """Três registros saem na ordem inversa da gravação (mais novo antes).

        Esperamos alguns milissegundos entre um registro e outro para o
        horário ser diferente de forma garantida.
        """
        primeiro = self._registrar()
        time.sleep(0.005)
        segundo = self._registrar(mes="2026-10")
        time.sleep(0.005)
        terceiro = self._registrar(mes="2026-11")

        registros = self.service.listar()

        self.assertEqual(
            [registro.feedback_id for registro in registros],
            [
                terceiro.feedback_id,
                segundo.feedback_id,
                primeiro.feedback_id,
            ],
        )

    def test_listar_filtra_por_loja(self):
        """O filtro devolve só os registros da loja pedida."""
        self._registrar("L004")
        self._registrar("L005")
        self._registrar("L004")

        da_l004 = self.service.listar("L004")

        self.assertEqual(len(da_l004), 2)
        self.assertTrue(
            all(registro.loja_id == "L004" for registro in da_l004)
        )
        # Loja sem registro devolve lista vazia, não erro.
        self.assertEqual(self.service.listar("L999"), [])

    def test_ultimo_de(self):
        """ultimo_de devolve o registro mais recente da loja (ou None)."""
        self._registrar()
        time.sleep(0.005)
        recente = self._registrar(mes="2026-10")

        ultimo = self.service.ultimo_de("L004")

        self.assertEqual(ultimo.feedback_id, recente.feedback_id)
        self.assertEqual(ultimo.mes_referencia, "2026-10")
        self.assertIsNone(self.service.ultimo_de("L999"))

    def test_persistencia_entre_duas_instancias(self):
        """O segundo serviço lê o que o primeiro gravou (o dado fica no disco)."""
        self._registrar()

        outro_service = RegistroFeedbackRegionalService(arquivo=self.arquivo)

        self.assertEqual(len(outro_service.listar()), 1)

    def test_arquivo_corrompido_levanta_erro_e_preserva_conteudo(self):
        """JSON inválido dá erro claro e o arquivo não é apagado nem trocado."""
        conteudo_original = "isto não é um JSON!"
        self.arquivo.write_text(conteudo_original, encoding="utf-8")

        with self.assertRaises(DadosIndisponiveisError):
            self.service.listar()

        # Tentar registrar também falha e não sobrescreve o arquivo.
        with self.assertRaises(DadosIndisponiveisError):
            self._registrar()

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
        self._registrar()

        self.assertEqual(
            [caminho.name for caminho in self.diretorio.iterdir()],
            ["registro_feedbacks_regional.json"],
        )

    def test_vinte_threads_registram_vinte_sem_perder_nenhum(self):
        """20 gravações simultâneas resultam em 20 registros no arquivo.

        O FastAPI atende pedidos em threads; sem o cadeado, duas gravações
        leriam a mesma lista e uma apagaria o registro da outra.
        """

        def registrar_um(indice: int) -> None:
            """Grava um registro com um mês de referência diferente."""
            self._registrar(mes=f"2026-{indice + 1:02d}")

        # ThreadPoolExecutor executa funções em várias threads de uma vez.
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(registrar_um, range(20)))

        self.assertEqual(len(self.service.listar()), 20)

    def test_registrar_aqui_nao_altera_o_registro_dos_vendedores(self):
        """O roteiro do gerente vai para OUTRO arquivo.

        O teste cria também o serviço dos vendedores na mesma pasta. Depois de
        gravar um roteiro para o gerente, o arquivo dos vendedores continua
        exatamente como estava (1 registro, o mesmo ID).
        """
        arquivo_vendedores = self.diretorio / "registro_feedbacks.json"
        servico_vendedores = RegistroFeedbackService(
            arquivo=arquivo_vendedores
        )
        do_vendedor = servico_vendedores.registrar(
            "C0031", "Bianca Rocha", None, roteiro_valido()
        )

        self._registrar(mes="2026-10")

        registros_do_vendedor = servico_vendedores.listar()

        self.assertEqual(len(registros_do_vendedor), 1)
        self.assertEqual(
            registros_do_vendedor[0].feedback_id, do_vendedor.feedback_id
        )
        # E o registro do gerente existe, num arquivo diferente.
        self.assertEqual(len(self.service.listar()), 1)
        self.assertNotEqual(
            self.service.listar()[0].feedback_id, do_vendedor.feedback_id
        )


if __name__ == "__main__":
    unittest.main()
