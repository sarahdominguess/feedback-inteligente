"""Consolidado da visão regional: junta loja, time e gerente mês a mês.

Este serviço monta os números que a regional acompanha. É a única camada que
cruza as vendas dos 8 vendedores com as vendas do próprio gerente e com a
meta da loja. Nenhuma fórmula nova aparece nas rotas: elas só pedem o
resultado aqui.

Regras (escritas em palavras):
- meses com dados = união dos meses de todos os vendedores com os do gerente,
  em ordem crescente;
- vendas dos vendedores = soma do valor vendido pelos 8 vendedores no mês;
- vendas do gerente = valor vendido pelo gerente no mês;
- vendas da loja = vendas dos vendedores MAIS vendas do gerente;
- atingimento da loja = vendas da loja dividido pela meta da loja;
- atingimento dos vendedores = vendas dos vendedores dividido pela meta;
- participação do gerente = vendas do gerente dividido pelas vendas da loja;
- dias com dados = o maior número de dias com dados entre as pessoas do mês;
- mês parcial = menos de DIAS_MINIMOS_MES_COMPLETO dias com dados.
"""

from config import DIAS_MINIMOS_MES_COMPLETO
from services.data_loader import DataLoader
from services.registro_feedback import RegistroFeedbackService


def _razao(numerador: float, denominador: float | None) -> float | None:
    """Divide com segurança: denominador zero ou ausente devolve None.

    Divisão por zero é erro em qualquer linguagem; e "sem meta" não é 0% de
    atingimento, é "não dá para calcular". Por isso devolvemos None (que vira
    null no JSON), nunca NaN.
    """
    if denominador is None or denominador == 0:
        return None
    return numerador / denominador


class ConsolidadoRegional:
    """Calcula o consolidado mensal da loja para a visão da regional.

    Recebe:
        data_loader: fonte dos vendedores, do gerente como Vendedor e da
            meta da loja.
        registro: serviço de registro dos roteiros (usado nas próximas
            partes; neste método ainda não é necessário).
    """

    def __init__(
        self,
        data_loader: DataLoader,
        registro: RegistroFeedbackService,
    ):
        """Guarda as dependências; nada é lido nem calculado aqui."""
        self._data_loader = data_loader
        self._registro = registro

    def obter_resultado_loja(self) -> list[dict]:
        """Devolve o resultado da loja, um dicionário por mês.

        Cada dicionário tem exatamente os campos de ResultadoLojaMesDTO
        (mes, mes_parcial, dias_com_dados, meta_loja, vendas_loja,
        atingimento_loja, vendas_vendedores, atingimento_vendedores,
        vendas_gerente, participacao_gerente), em ordem cronológica.

        Por que mostramos DOIS atingimentos: a meta da loja é a soma das
        metas dos vendedores e NÃO inclui o gerente. As vendas do gerente
        ajudam a loja a bater a meta, mas não contam para a meta individual
        de ninguém. Mostrar os dois números deixa isso claro para a regional,
        em vez de esconder a diferença num único percentual.

        Exemplo: obter_resultado_loja()[0]["mes"] == "2026-08"
        """
        vendedores = self._data_loader.listar_vendedores()
        gerente = self._data_loader.obter_vendas_do_gerente()

        # União dos meses: set() evita repetir o mesmo mês; sorted() deixa em
        # ordem cronológica (o formato AAAA-MM ordena como texto).
        meses = set()
        for vendedor in vendedores:
            meses.update(vendedor.meses_com_dados())
        meses.update(gerente.meses_com_dados())

        resultado = []
        for mes in sorted(meses):
            # Somas do mês: valor vendido, nunca a média das razões diárias.
            vendas_vendedores = sum(
                vendedor.valor_vendido(mes) for vendedor in vendedores
            )
            vendas_gerente = gerente.valor_vendido(mes)
            vendas_loja = vendas_vendedores + vendas_gerente

            meta_loja = self._data_loader.obter_meta_loja(mes)

            # O maior número de dias entre as pessoas representa o mês: se
            # alguém trabalhou 27 dias, o mês não é parcial.
            dias_com_dados = max(
                [vendedor.dias_com_dados(mes) for vendedor in vendedores]
                + [gerente.dias_com_dados(mes)]
            )

            resultado.append(
                {
                    "mes": mes,
                    "mes_parcial": dias_com_dados
                    < DIAS_MINIMOS_MES_COMPLETO,
                    "dias_com_dados": dias_com_dados,
                    "meta_loja": meta_loja,
                    "vendas_loja": vendas_loja,
                    "atingimento_loja": _razao(vendas_loja, meta_loja),
                    "vendas_vendedores": vendas_vendedores,
                    "atingimento_vendedores": _razao(
                        vendas_vendedores, meta_loja
                    ),
                    "vendas_gerente": vendas_gerente,
                    "participacao_gerente": _razao(
                        vendas_gerente, vendas_loja
                    ),
                }
            )

        return resultado
