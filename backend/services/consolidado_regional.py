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

from config import DIAS_MINIMOS_MES_COMPLETO, LOJA_ID, LOJA_NOME
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

    def obter_acompanhamento_feedback(self) -> dict:
        """Monta o acompanhamento de feedbacks preparados por vendedor.

        Devolve exatamente os campos de AcompanhamentoFeedbackDTO:
        total_vendedores, vendedores_com_roteiro, cobertura,
        total_roteiros_preparados e a lista "vendedores" (um item por
        vendedor, na ordem do CSV).

        IMPORTANTE: "roteiro preparado" quer dizer que o roteiro foi GERADO
        pela IA. NÃO é "feedback realizado": o sistema não sabe se a
        conversa chegou a acontecer.

        Contas em palavras:
        - roteiros_preparados = quantos registros existem para a pessoa;
        - cobertura = vendedores com pelo menos 1 roteiro dividido pelo
          total de vendedores (0 quando não há vendedores);
        - situacao = "com_roteiro" quando há pelo menos 1 roteiro gerado.
        """
        vendedores = self._data_loader.listar_vendedores()

        # Lemos o registro UMA vez e agrupamos por vendedor. Reler o arquivo
        # para cada pessoa seriam 8 leituras dentro de um único pedido.
        registros_por_vendedor: dict[str, list] = {}
        for registro_gravado in self._registro.listar():
            registros_por_vendedor.setdefault(
                registro_gravado.vendedor_id, []
            ).append(registro_gravado)

        itens = []
        vendedores_com_roteiro = 0
        total_roteiros = 0

        for vendedor in vendedores:
            # Anotações do gerente SOBRE a pessoa (sem as do time), em ordem
            # cronológica — por isso a última da tupla é a mais recente.
            anotacoes = self._data_loader.obter_anotacoes_do_vendedor(
                vendedor.vendedor_id
            )
            registros = registros_por_vendedor.get(vendedor.vendedor_id, [])

            total_roteiros += len(registros)
            if registros:
                vendedores_com_roteiro += 1

            itens.append(
                {
                    "vendedor_id": vendedor.vendedor_id,
                    "nome": vendedor.nome,
                    "anotacoes_do_gerente": len(anotacoes),
                    "ultima_anotacao_em": (
                        anotacoes[-1].data if anotacoes else None
                    ),
                    "roteiros_preparados": len(registros),
                    # max() pega o roteiro mais recente sem depender da ordem
                    # em que o registro devolveu a lista.
                    "ultimo_roteiro_em": max(
                        (registro.gerado_em for registro in registros),
                        default=None,
                    ),
                    "situacao": (
                        "com_roteiro" if registros else "sem_roteiro"
                    ),
                }
            )

        total_vendedores = len(vendedores)

        # Sem vendedores, a cobertura é 0 (evita divisão por zero).
        cobertura = (
            vendedores_com_roteiro / total_vendedores
            if total_vendedores > 0
            else 0.0
        )

        return {
            "total_vendedores": total_vendedores,
            "vendedores_com_roteiro": vendedores_com_roteiro,
            "cobertura": cobertura,
            "total_roteiros_preparados": total_roteiros,
            "vendedores": itens,
        }

    def obter_desempenho_gerente(self) -> dict:
        """Monta a resposta completa da visão executiva da regional.

        Devolve exatamente os campos de DesempenhoGerenteResposta: identidade
        do gerente e da loja, período com dados, resultado mês a mês,
        acompanhamento dos roteiros e anotações da regional.

        Período: menor e maior data entre TODOS os indicadores (vendedores e
        gerente); None quando não há nenhuma data.

        Reforçando o vocabulário: os "roteiros preparados" foram apenas
        GERADOS; não sabemos se a conversa de feedback aconteceu.

        Exemplo: obter_desempenho_gerente()["gerente_nome"] == "Diego Furtado"
        """
        gerente = self._data_loader.obter_gerente()
        gerente_como_vendedor = self._data_loader.obter_vendas_do_gerente()

        # Junta as datas de todos os indicadores para achar o período.
        datas = []
        for vendedor in self._data_loader.listar_vendedores():
            for indicador in vendedor.indicadores:
                datas.append(indicador.data)
        for indicador in gerente_como_vendedor.indicadores:
            datas.append(indicador.data)

        # Anotações da regional já vêm em ordem cronológica do DataLoader.
        anotacoes_regional = [
            {
                "data": anotacao.data,
                "autora": anotacao.autora,
                "texto": anotacao.texto,
            }
            for anotacao in self._data_loader.listar_anotacoes_regional()
        ]

        return {
            "gerente_id": gerente.gerente_id,
            "gerente_nome": gerente.nome,
            "loja_id": gerente.loja_id,
            "loja_nome": gerente.loja_nome,
            "periodo_inicio": min(datas) if datas else None,
            "periodo_fim": max(datas) if datas else None,
            "resultado_loja": self.obter_resultado_loja(),
            "acompanhamento_feedback": self.obter_acompanhamento_feedback(),
            "anotacoes_regional": anotacoes_regional,
        }

    def listar_lojas(self) -> list[dict]:
        """Devolve as lojas que a regional pode acompanhar.

        Hoje o desafio tem UMA loja com dados (a L004, da configuração), então
        a lista traz um único item: código e nome da loja + código e nome do
        gerente carregado.

        Por que devolver uma LISTA em vez de um objeto só: o frontend já é
        escrito para escolher entre N lojas. Quando existirem outras, basta
        acrescentar itens aqui, sem mudar o contrato nem a tela. Nenhuma conta
        é feita: os dados vêm do config e do próprio gerente.

        Exemplo: listar_lojas()[0]["loja_id"] == "L004"
        """
        gerente = self._data_loader.obter_gerente()

        return [
            {
                "loja_id": LOJA_ID,
                "loja_nome": LOJA_NOME,
                "gerente_id": gerente.gerente_id,
                "gerente_nome": gerente.nome,
            }
        ]
