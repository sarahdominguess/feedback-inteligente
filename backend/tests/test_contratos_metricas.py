"""Testes dos contratos de erro e de métricas e da exceção de loja.

Verificam que os modelos aceitam os dados certos, recusam valores impossíveis
(NaN, infinito, textos fora da lista permitida) e que valores ausentes viram
null no JSON, que é o formato combinado com o frontend.
"""

import json
import unittest

from pydantic import ValidationError

from contracts.erros import ErroResposta
from contracts.metricas import (
    MetricaComparadaDTO,
    MetricasDTO,
    ResumoMensalDTO,
)
from domain.excecoes import DominioError, LojaNaoEncontradaError


class TestErroResposta(unittest.TestCase):
    """Testes do formato único de erro {"erro": "..."}."""

    def test_formato_unico_de_erro(self):
        """O contrato tem exatamente o campo 'erro', em texto.

        Todo erro da API usa este molde, então o frontend só precisa tratar
        um formato.
        """
        resposta = ErroResposta(erro="Vendedor não encontrado.")

        self.assertEqual(
            resposta.model_dump(), {"erro": "Vendedor não encontrado."}
        )
        self.assertEqual(
            json.loads(resposta.model_dump_json()),
            {"erro": "Vendedor não encontrado."},
        )


class TestLojaNaoEncontradaError(unittest.TestCase):
    """Testes da exceção de loja inexistente."""

    def test_herda_de_dominio_error(self):
        """A exceção nova é filha de DominioError e preserva a mensagem.

        Herdar de DominioError é o que permite o tratamento global de erros
        da API capturar este caso sem conhecer cada exceção individualmente.
        """
        self.assertTrue(issubclass(LojaNaoEncontradaError, DominioError))

        erro = LojaNaoEncontradaError("Loja 'L999' não encontrada.")
        self.assertEqual(str(erro), "Loja 'L999' não encontrada.")

        with self.assertRaises(DominioError):
            raise erro


class TestMetricasDTO(unittest.TestCase):
    """Testes do contrato com os indicadores consolidados."""

    def _criar_valido(self, **alteracoes) -> MetricasDTO:
        """Cria um DTO válido, permitindo trocar campos para testar erros."""
        dados = {
            "valor_vendido": 128944.49,
            "vendas": 625,
            "pecas": 765,
            "atendimentos": 1238,
            "ticket_medio": 206.31,
            "pecas_por_atendimento": 1.224,
            "conversao": 0.505,
        }
        dados.update(alteracoes)
        return MetricasDTO(**dados)

    def test_criacao_valida_e_none_vira_null(self):
        """Campos sem valor viram null no JSON (nunca NaN).

        O domínio devolve None quando não há base para uma divisão; o JSON
        precisa trazer null para o frontend exibir "sem dados".
        """
        metricas = self._criar_valido(ticket_medio=None)

        self.assertIsNone(metricas.ticket_medio)
        self.assertEqual(metricas.conversao, 0.505)

        # model_dump_json gera o texto JSON, como a API devolve.
        texto_json = metricas.model_dump_json()
        self.assertIn('"ticket_medio":null', texto_json)

        # Conferindo pelo dicionário, que é mais fácil de ler.
        self.assertIsNone(json.loads(texto_json)["ticket_medio"])

    def test_recusa_nan_e_infinito(self):
        """NaN e infinito são recusados em campo obrigatório e opcional.

        NaN não existe em JSON e o infinito também não; se passassem, o
        frontend receberia um texto inválido.
        """
        for valor in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(campo="valor_vendido", valor=valor):
                with self.assertRaises(ValidationError):
                    self._criar_valido(valor_vendido=valor)

            with self.subTest(campo="conversao", valor=valor):
                with self.assertRaises(ValidationError):
                    self._criar_valido(conversao=valor)

    def test_descricoes_aparecem_no_esquema(self):
        """As descrições em português aparecem no esquema (Swagger).

        model_json_schema() é o que o FastAPI usa para montar a documentação;
        se a descrição estiver lá, ela aparece na tela do Swagger.
        """
        esquema = json.dumps(
            MetricasDTO.model_json_schema(), ensure_ascii=False
        )

        self.assertIn("fração de 0 a 1", esquema)
        self.assertIn("reais", esquema)


class TestMetricaComparadaDTO(unittest.TestCase):
    """Testes do contrato de uma métrica comparada com o time."""

    def _criar_valida(self, **alteracoes) -> MetricaComparadaDTO:
        """Cria um DTO válido, permitindo trocar campos para testar erros."""
        dados = {
            "nome": "conversao",
            "valor": 0.505,
            "media_time": 0.377,
            "diferenca_percentual": 0.34,
            "posicao": 1,
            "total_vendedores": 8,
            "situacao": "acima",
        }
        dados.update(alteracoes)
        return MetricaComparadaDTO(**dados)

    def test_criacao_valida(self):
        """Os três nomes de métrica e as quatro situações são aceitos."""
        nomes = ("ticket_medio", "pecas_por_atendimento", "conversao")
        situacoes = ("acima", "abaixo", "na_media", "indisponivel")

        for nome in nomes:
            with self.subTest(nome=nome):
                self.assertEqual(
                    self._criar_valida(nome=nome).nome, nome
                )

        for situacao in situacoes:
            with self.subTest(situacao=situacao):
                self.assertEqual(
                    self._criar_valida(situacao=situacao).situacao,
                    situacao,
                )

    def test_recusa_nome_de_metrica_invalido(self):
        """Um nome fora da lista das três métricas levanta ValidationError.

        Literal é a lista fechada de textos aceitos; qualquer outro valor é
        recusado na entrada.
        """
        with self.assertRaises(ValidationError):
            self._criar_valida(nome="ticket")

    def test_recusa_situacao_invalida(self):
        """Situação precisa ser uma das quatro previstas."""
        with self.assertRaises(ValidationError):
            self._criar_valida(situacao="muito_acima")

    def test_recusa_nan_na_diferenca(self):
        """A diferença percentual também não aceita NaN."""
        with self.assertRaises(ValidationError):
            self._criar_valida(diferenca_percentual=float("nan"))


class TestResumoMensalDTO(unittest.TestCase):
    """Testes do contrato do resumo de um mês."""

    def test_criacao_valida_com_mes_parcial(self):
        """Mês com 1 dia de dados é marcado como parcial e meta pode ser null."""
        resumo = ResumoMensalDTO(
            mes="2026-11",
            dias_com_dados=1,
            mes_parcial=True,
            valor_vendido=500.0,
            vendas=2,
            pecas=3,
            atendimentos=4,
            ticket_medio=250.0,
            pecas_por_atendimento=1.5,
            conversao=0.5,
            meta=None,
            atingimento_meta=None,
        )

        self.assertTrue(resumo.mes_parcial)
        self.assertIsNone(resumo.meta)
        self.assertIsNone(resumo.atingimento_meta)

        # No JSON, os campos sem valor aparecem como null.
        dados = json.loads(resumo.model_dump_json())
        self.assertIsNone(dados["meta"])
        self.assertIsNone(dados["atingimento_meta"])
        self.assertEqual(dados["mes"], "2026-11")
