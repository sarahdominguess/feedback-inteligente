"""Testes da integração entre o DataLoader e as anotações novas.

Mostram que uma anotação escrita na interface (gravada pelo
RegistroAnotacoesService) aparece em TODOS os lugares que leem as anotações
do gerente: o histórico do vendedor, o prompt enviado à IA e o acompanhamento
da regional.

Tudo roda em pastas temporárias: nenhum teste toca os CSVs nem os arquivos
reais do projeto, e nada acessa a internet.
"""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from services.consolidado_regional import ConsolidadoRegional
from services.data_loader import DataLoader
from services.prompt_feedback import montar_mensagens
from services.registro_anotacoes import RegistroAnotacoesService
from services.registro_feedback import RegistroFeedbackService
from tests.test_data_loader import arquivos_padrao, escrever_arquivos

# Textos das três anotações do CSV sintético (ver tests/test_data_loader.py),
# já na ordem cronológica em que o Gerente as devolve.
TEXTO_BIANCA_CSV = "atendeu bem no sábado"
TEXTO_TIME_CSV = "sábado corrido"
TEXTO_ANA_CSV = "boa argumentação"


def achar_anotacoes_do_vendedor(acompanhamento: dict, vendedor_id: str) -> int:
    """Devolve quantas anotações o acompanhamento regional conta da pessoa.

    Recebe o dicionário devolvido por obter_acompanhamento_feedback() e o
    código do vendedor. Serve para comparar o número antes e depois de gravar
    uma anotação nova.

    Exemplo: achar_anotacoes_do_vendedor(acompanhamento, "C0031") -> 1
    """
    for item in acompanhamento["vendedores"]:
        if item["vendedor_id"] == vendedor_id:
            return item["anotacoes_do_gerente"]

    # Se o vendedor não estiver na lista, o teste falha com mensagem clara em
    # vez de devolver um número inventado.
    raise AssertionError(f"Vendedor {vendedor_id} não está no acompanhamento.")


class TestDataLoaderComAnotacoesNovas(unittest.TestCase):
    """Testes da junção entre as anotações do CSV e as gravadas no site."""

    def setUp(self):
        """Monta CSVs sintéticos e o serviço de anotações numa pasta temporária.

        TemporaryDirectory é apagada pelo próprio Python no fim do teste.
        """
        self._diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self._diretorio_temporario.cleanup)

        raiz = Path(self._diretorio_temporario.name)
        self.data_dir = raiz / "data"
        self.data_dir.mkdir()
        escrever_arquivos(self.data_dir, arquivos_padrao())

        # O arquivo das anotações novas fica FORA da pasta de dados: assim os
        # dois assuntos não se misturam nem no teste.
        self.arquivo_anotacoes = raiz / "anotacoes_novas.json"
        self.registro = RegistroAnotacoesService(arquivo=self.arquivo_anotacoes)

        # DataLoader com o serviço: é o modo usado pela API.
        self.loader = DataLoader(
            data_dir=self.data_dir,
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
            registro_anotacoes=self.registro,
        )

    def _loader_sem_servico(self) -> DataLoader:
        """Cria um DataLoader do jeito antigo, sem o serviço de anotações."""
        return DataLoader(
            data_dir=self.data_dir,
            loja_id="L004",
            loja_nome="Aurora Shopping Centro",
        )

    # -----------------------------------------------------------------
    # Sem o serviço, nada muda
    # -----------------------------------------------------------------

    def test_sem_servico_o_resultado_e_igual_ao_do_csv(self):
        """Sem registro_anotacoes, o gerente traz só as anotações do CSV.

        É a garantia de compatibilidade: quem monta o DataLoader do jeito
        antigo continua vendo exatamente o que via antes.
        """
        self.registro.registrar(
            "Bianca Rocha", "texto que não deve aparecer", data=date(2026, 10, 8)
        )

        gerente = self._loader_sem_servico().obter_gerente()

        self.assertEqual(
            [anotacao.texto for anotacao in gerente.anotacoes()],
            [TEXTO_BIANCA_CSV, TEXTO_TIME_CSV, TEXTO_ANA_CSV],
        )

    # -----------------------------------------------------------------
    # A anotação nova aparece no histórico, no prompt e na regional
    # -----------------------------------------------------------------

    def test_anotacao_nova_aparece_nas_anotacoes_do_vendedor(self):
        """A anotação sobre a Bianca entra em obter_anotacoes_do_vendedor."""
        self.registro.registrar(
            "Bianca Rocha",
            "cliente elogiou o atendimento",
            data=date(2026, 10, 8),
        )

        anotacoes = self.loader.obter_anotacoes_do_vendedor("C0031")

        # Uma do CSV + uma nova.
        self.assertEqual(len(anotacoes), 2)
        self.assertIn("cliente elogiou o atendimento", [
            anotacao.texto for anotacao in anotacoes
        ])

    def test_anotacao_nova_aparece_no_gerente(self):
        """O Gerente devolvido também carrega a anotação nova."""
        self.registro.registrar(
            "Bianca Rocha", "anotação do site", data=date(2026, 10, 8)
        )

        gerente = self.loader.obter_gerente()

        # Três do CSV + uma nova.
        self.assertEqual(len(gerente.anotacoes()), 4)
        self.assertIn(
            "anotação do site",
            [anotacao.texto for anotacao in gerente.anotacoes()],
        )

    def test_anotacao_de_outra_pessoa_nao_entra_nas_da_bianca(self):
        """Filtrar por pessoa continua funcionando com as anotações novas."""
        self.registro.registrar(
            "Ana Silva", "boa argumentação no sábado", data=date(2026, 10, 9)
        )

        anotacoes_da_bianca = self.loader.obter_anotacoes_do_vendedor("C0031")
        anotacoes_da_ana = self.loader.obter_anotacoes_do_vendedor("C0032")

        # A Bianca continua com a única anotação que já estava no CSV...
        self.assertEqual(
            [anotacao.texto for anotacao in anotacoes_da_bianca],
            [TEXTO_BIANCA_CSV],
        )
        # ...e a Ana recebe a do CSV + a nova.
        self.assertEqual(
            [anotacao.texto for anotacao in anotacoes_da_ana],
            [TEXTO_ANA_CSV, "boa argumentação no sábado"],
        )

    def test_anotacao_do_time_aparece_em_anotacoes_do_time(self):
        """Anotação com "sobre" = "(time)" entra nas do time, não nas da pessoa."""
        self.registro.registrar(
            "(time)", "reunião de equipe na segunda", data=date(2026, 10, 10)
        )

        gerente = self.loader.obter_gerente()
        textos_do_time = [
            anotacao.texto for anotacao in gerente.anotacoes_do_time()
        ]
        textos_da_bianca = [
            anotacao.texto
            for anotacao in self.loader.obter_anotacoes_do_vendedor("C0031")
        ]

        self.assertEqual(len(textos_do_time), 2)
        self.assertIn("reunião de equipe na segunda", textos_do_time)
        self.assertNotIn("reunião de equipe na segunda", textos_da_bianca)

    def test_anotacao_gravada_depois_do_uso_aparece_na_leitura_seguinte(self):
        """A anotação não pode ficar "congelada" na primeira leitura.

        Chamamos obter_gerente() antes de gravar: se o DataLoader guardasse a
        lista, o texto novo só apareceria depois de reiniciar o servidor.
        """
        antes = self.loader.obter_gerente().anotacoes()
        self.assertEqual(len(antes), 3)

        self.registro.registrar(
            "Bianca Rocha",
            "escrita depois da primeira leitura",
            data=date(2026, 10, 9),
        )

        depois = self.loader.obter_gerente().anotacoes()

        self.assertEqual(len(depois), 4)
        self.assertIn(
            "escrita depois da primeira leitura",
            [anotacao.texto for anotacao in depois],
        )

    def test_ordem_por_data_e_desempate(self):
        """Ordena por data; em datas iguais, CSV antes das novas.

        Entre as novas da mesma data vale a ordem em que foram registradas.
        """
        self.registro.registrar(
            "Bianca Rocha", "antes de todas", data=date(2026, 8, 1)
        )
        self.registro.registrar(
            "Bianca Rocha", "mesma data de uma do CSV", data=date(2026, 9, 1)
        )
        self.registro.registrar(
            "Bianca Rocha", "outra no mesmo dia", data=date(2026, 9, 1)
        )

        textos = [
            anotacao.texto for anotacao in self.loader.obter_gerente().anotacoes()
        ]

        self.assertEqual(
            textos,
            [
                "antes de todas",          # 2026-08-01 (nova)
                TEXTO_BIANCA_CSV,          # 2026-08-06 (CSV)
                TEXTO_TIME_CSV,            # 2026-08-24 (CSV)
                TEXTO_ANA_CSV,             # 2026-09-01 (CSV, vem antes no empate)
                "mesma data de uma do CSV",  # 2026-09-01 (nova, registrada antes)
                "outra no mesmo dia",      # 2026-09-01 (nova, registrada depois)
            ],
        )

    def test_regional_conta_a_anotacao_nova(self):
        """O acompanhamento da regional passa a contar a anotação nova.

        Usa o ConsolidadoRegional de verdade, com o DataLoader de teste e um
        registro de feedbacks num arquivo temporário (sem internet).
        """
        registro_feedbacks = RegistroFeedbackService(
            arquivo=Path(self._diretorio_temporario.name) / "registro.json"
        )
        consolidado = ConsolidadoRegional(
            data_loader=self.loader,
            registro=registro_feedbacks,
        )

        antes = achar_anotacoes_do_vendedor(
            consolidado.obter_acompanhamento_feedback(), "C0031"
        )

        self.registro.registrar(
            "Bianca Rocha", "mais uma para a regional", data=date(2026, 10, 10)
        )

        depois = achar_anotacoes_do_vendedor(
            consolidado.obter_acompanhamento_feedback(), "C0031"
        )

        # Exatamente uma a mais: a que acabou de ser gravada.
        self.assertEqual(depois, antes + 1)

    def test_prompt_da_ia_inclui_a_anotacao_nova(self):
        """O texto que vai para a IA contém a anotação escrita no site.

        Monta as mensagens com a MESMA função usada pelo LLMService, a partir
        do que o DataLoader devolve. Nenhum cliente de IA é chamado.
        """
        texto_novo = "pediu o contato da loja pelo Instagram"
        self.registro.registrar(
            "Bianca Rocha", texto_novo, data=date(2026, 10, 8)
        )

        bianca = self.loader.buscar_vendedor_por_nome("Bianca")
        comparativo = self.loader.obter_comparativo_time(bianca.vendedor_id)
        gerente = self.loader.obter_gerente()

        mensagens = montar_mensagens(
            vendedor=bianca,
            comparativo=comparativo,
            anotacoes_do_vendedor=self.loader.obter_anotacoes_do_vendedor(
                bianca.vendedor_id
            ),
            anotacoes_do_time=gerente.anotacoes_do_time(),
            gerente_nome=gerente.nome,
            loja_nome=gerente.loja_nome,
        )

        # A segunda mensagem é a do usuário, que leva os dados para a IA.
        usuario = mensagens[1]["content"]

        self.assertIn(texto_novo, usuario)

        # Controle: sem o serviço, o mesmo prompt não teria o texto novo.
        loader_antigo = self._loader_sem_servico()
        mensagens_antigas = montar_mensagens(
            vendedor=bianca,
            comparativo=comparativo,
            anotacoes_do_vendedor=loader_antigo.obter_anotacoes_do_vendedor(
                bianca.vendedor_id
            ),
            anotacoes_do_time=loader_antigo.obter_gerente().anotacoes_do_time(),
            gerente_nome=gerente.nome,
            loja_nome=gerente.loja_nome,
        )

        self.assertNotIn(texto_novo, mensagens_antigas[1]["content"])


if __name__ == "__main__":
    unittest.main()
