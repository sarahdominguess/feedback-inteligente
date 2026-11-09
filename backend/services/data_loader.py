"""Serviço de carga dos CSVs do desafio, usando Pandas.

DataLoader é a única camada que conhece Pandas: lê os arquivos de backend/data,
valida as colunas e monta objetos de domínio (Vendedor, Gerente, Anotacao,
IndicadorDiario). Assim, nenhum DataFrame ou NaN vaza para o domínio.
"""

from pathlib import Path

import pandas as pd

from config import (
    ARQUIVO_ANOTACOES_GERENTE,
    ARQUIVO_INDICADORES_DIARIOS,
    ARQUIVO_METAS_VENDEDOR,
    ARQUIVO_VENDEDORES,
    DATA_DIR,
    LOJA_ID,
    LOJA_NOME,
)
from domain.anotacao import Anotacao
from domain.comparativo_time import ComparativoTime, MetricaComparada
from domain.excecoes import DadosIndisponiveisError, VendedorNaoEncontradoError
from domain.gerente import Gerente
from domain.indicador_diario import IndicadorDiario
from domain.texto import nome_corresponde
from domain.vendedor import Vendedor


def _texto(valor) -> str:
    """Converte uma célula do CSV em texto, trocando vazio (NaN) por "".

    NaN: o valor que o Pandas usa para representar célula vazia ("não é
    número"). Dentro do domínio queremos texto de verdade, nunca NaN.
    """
    if pd.isna(valor):
        return ""
    return str(valor)


def _numero(valor, arquivo: str, coluna: str) -> float:
    """Converte uma célula em número decimal, com erro claro se for inválida.

    Recebe o valor lido do CSV, o nome do arquivo e o nome da coluna (usados
    apenas na mensagem de erro). Devolve um float.
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError) as erro:
        raise DadosIndisponiveisError(
            f"O arquivo {arquivo} tem valor inválido na coluna '{coluna}': "
            f"{valor!r}."
        ) from erro

    # float("nan") não gera erro, mas NaN não pode entrar no domínio.
    if pd.isna(numero):
        raise DadosIndisponiveisError(
            f"O arquivo {arquivo} tem célula vazia na coluna '{coluna}'."
        )
    return numero


def _inteiro(valor, arquivo: str, coluna: str) -> int:
    """Converte uma célula em número inteiro, reaproveitando _numero."""
    return int(_numero(valor, arquivo, coluna))


class DataLoader:
    """Lê os CSVs do desafio e entrega objetos de domínio prontos.

    Recebe:
        data_dir: pasta onde estão os CSVs (padrão: backend/data).
        loja_id: código da loja dos funcionários (padrão: L004).
        loja_nome: nome da loja (padrão: Aurora Shopping Centro).

    A leitura é preguiçosa: nada é lido no construtor. Na primeira chamada de
    um método público, os quatro arquivos são lidos uma única vez e ficam em
    cache interno; as chamadas seguintes reaproveitam os dados.
    """

    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        loja_id: str = LOJA_ID,
        loja_nome: str = LOJA_NOME,
    ):
        """Guarda a configuração; os arquivos só serão lidos depois."""
        self._data_dir = Path(data_dir)
        self._loja_id = loja_id
        self._loja_nome = loja_nome

        # "Cache": guardar o resultado para não recalcular (aqui, para não
        # reler os arquivos a cada chamada).
        self._carregado = False

        # DataFrames privados (o "_" indica uso interno). Ficam como None até
        # a primeira chamada de método público.
        self._vendedores_df: pd.DataFrame | None = None
        self._indicadores_df: pd.DataFrame | None = None
        self._metas_df: pd.DataFrame | None = None
        self._anotacoes_df: pd.DataFrame | None = None

        # Coleções montadas a partir dos DataFrames.
        self._indicadores_por_vendedor: dict[str, list[IndicadorDiario]] = {}
        self._metas_por_vendedor: dict[str, dict[str, float]] = {}
        self._anotacoes: tuple[Anotacao, ...] = ()
        self._vendedores: tuple[Vendedor, ...] = ()
        self._gerente: Gerente | None = None

    def _ler_csv(
        self,
        nome_arquivo: str,
        colunas_obrigatorias: tuple[str, ...],
        colunas_texto: tuple[str, ...] = (),
        coluna_data: str | None = None,
    ) -> pd.DataFrame:
        """Lê um CSV, confere as colunas e converte a coluna de data.

        Recebe o nome do arquivo (dentro de data_dir), a lista de colunas que
        precisam existir, quais colunas devem ser lidas como texto (IDs e
        meses) e, opcionalmente, qual coluna guarda datas.

        Devolve um DataFrame (tabela do Pandas). Levanta
        DadosIndisponiveisError quando o arquivo não existe, não pode ser lido
        ou não tem uma coluna obrigatória.
        """
        caminho = self._data_dir / nome_arquivo

        if not caminho.is_file():
            raise DadosIndisponiveisError(
                f"Arquivo de dados não encontrado: {caminho}"
            )

        # dtype força o Pandas a ler certas colunas como texto. Sem isso, um
        # ID como "0031" poderia virar número e perder os zeros à esquerda.
        tipos = {coluna: str for coluna in colunas_texto}

        try:
            df = pd.read_csv(caminho, encoding="utf-8", dtype=tipos)
        except Exception as erro:
            # Qualquer falha de leitura (arquivo corrompido, codificação
            # errada etc.) vira o erro de domínio com mensagem em português.
            raise DadosIndisponiveisError(
                f"Não foi possível ler o arquivo {nome_arquivo}: {erro}"
            ) from erro

        # Colunas que o restante do código espera encontrar.
        faltantes = [
            coluna
            for coluna in colunas_obrigatorias
            if coluna not in df.columns
        ]
        if faltantes:
            raise DadosIndisponiveisError(
                f"O arquivo {nome_arquivo} não tem a(s) coluna(s) "
                f"obrigatória(s): {', '.join(faltantes)}."
            )

        # Converte a coluna de data de texto ("2026-08-01") para data do
        # Python, para o domínio nunca receber texto nem NaN nesse campo.
        if coluna_data is not None:
            try:
                df[coluna_data] = pd.to_datetime(
                    df[coluna_data], format="%Y-%m-%d"
                ).dt.date
            except Exception as erro:
                raise DadosIndisponiveisError(
                    f"O arquivo {nome_arquivo} tem datas inválidas na coluna "
                    f"'{coluna_data}'."
                ) from erro

            # Data vazia vira NaT ("not a time"), que também não pode entrar
            # no domínio; tratamos como arquivo indisponível.
            if df[coluna_data].isna().any():
                raise DadosIndisponiveisError(
                    f"O arquivo {nome_arquivo} tem datas vazias na coluna "
                    f"'{coluna_data}'."
                )

        return df

    def _carregar_dados(self) -> None:
        """Lê os quatro CSVs e monta todas as coleções internas uma vez.

        É chamado apenas por _garantir_carregado, na primeira necessidade.
        """
        # 1) Lê os arquivos e valida as colunas obrigatórias de cada um.
        self._vendedores_df = self._ler_csv(
            ARQUIVO_VENDEDORES,
            ("vendedor_id", "nome", "cargo"),
            colunas_texto=("vendedor_id",),
        )
        self._indicadores_df = self._ler_csv(
            ARQUIVO_INDICADORES_DIARIOS,
            (
                "data",
                "vendedor_id",
                "valor_vendido",
                "vendas",
                "pecas",
                "atendimentos",
            ),
            colunas_texto=("vendedor_id",),
            coluna_data="data",
        )
        self._metas_df = self._ler_csv(
            ARQUIVO_METAS_VENDEDOR,
            ("vendedor_id", "mes", "meta_valor"),
            colunas_texto=("vendedor_id", "mes"),
        )
        self._anotacoes_df = self._ler_csv(
            ARQUIVO_ANOTACOES_GERENTE,
            ("data", "sobre", "anotacao"),
            coluna_data="data",
        )

        # 2) Agrupa os indicadores por vendedor_id.
        # dict.setdefault(id, []) cria a lista na primeira vez em que o ID
        # aparece e devolve a lista existente nas próximas.
        for _, linha in self._indicadores_df.iterrows():
            vendedor_id = _texto(linha["vendedor_id"])
            indicador = IndicadorDiario(
                data=linha["data"],
                vendedor_id=vendedor_id,
                valor_vendido=_numero(
                    linha["valor_vendido"],
                    ARQUIVO_INDICADORES_DIARIOS,
                    "valor_vendido",
                ),
                vendas=_inteiro(
                    linha["vendas"], ARQUIVO_INDICADORES_DIARIOS, "vendas"
                ),
                pecas=_inteiro(
                    linha["pecas"], ARQUIVO_INDICADORES_DIARIOS, "pecas"
                ),
                atendimentos=_inteiro(
                    linha["atendimentos"],
                    ARQUIVO_INDICADORES_DIARIOS,
                    "atendimentos",
                ),
            )
            self._indicadores_por_vendedor.setdefault(
                vendedor_id, []
            ).append(indicador)

        # 3) Agrupa as metas por vendedor: {"2026-08": 42542.86, ...}.
        # O mês é mantido como texto "AAAA-MM" (exatamente como está no CSV).
        for _, linha in self._metas_df.iterrows():
            vendedor_id = _texto(linha["vendedor_id"])
            mes = _texto(linha["mes"])
            meta = _numero(
                linha["meta_valor"], ARQUIVO_METAS_VENDEDOR, "meta_valor"
            )
            self._metas_por_vendedor.setdefault(vendedor_id, {})[mes] = meta

        # 4) Monta as anotações. O texto "sobre" pode ser um nome ou "(time)".
        anotacoes = []
        for _, linha in self._anotacoes_df.iterrows():
            anotacoes.append(
                Anotacao(
                    data=linha["data"],
                    sobre=_texto(linha["sobre"]),
                    texto=_texto(linha["anotacao"]),
                )
            )
        self._anotacoes = tuple(anotacoes)

        # 5) Monta a lista de vendedores (só cargo "vendedor"), mantendo a
        # ordem em que aparecem no CSV. O gerente fica de fora desta lista.
        vendedores = []
        for _, linha in self._vendedores_df.iterrows():
            cargo = _texto(linha["cargo"])
            if cargo != "vendedor":
                continue

            vendedor_id = _texto(linha["vendedor_id"])
            vendedores.append(
                Vendedor(
                    vendedor_id=vendedor_id,
                    nome=_texto(linha["nome"]),
                    cargo=cargo,
                    loja_id=self._loja_id,
                    loja_nome=self._loja_nome,
                    indicadores=self._indicadores_por_vendedor.get(
                        vendedor_id, ()
                    ),
                    metas=self._metas_por_vendedor.get(vendedor_id),
                )
            )
        self._vendedores = tuple(vendedores)

        # 6) Monta o gerente (linha com cargo "gerente"). Todas as anotações
        # do arquivo pertencem ao gerente da loja.
        linhas_gerente = self._vendedores_df[
            self._vendedores_df["cargo"] == "gerente"
        ]
        if linhas_gerente.empty:
            raise DadosIndisponiveisError(
                f"Nenhum gerente encontrado no arquivo {ARQUIVO_VENDEDORES}."
            )

        linha_gerente = linhas_gerente.iloc[0]
        self._gerente = Gerente(
            gerente_id=_texto(linha_gerente["vendedor_id"]),
            nome=_texto(linha_gerente["nome"]),
            loja_id=self._loja_id,
            loja_nome=self._loja_nome,
            anotacoes=self._anotacoes,
        )

    def _garantir_carregado(self) -> None:
        """Carrega os arquivos na primeira chamada; depois só reaproveita."""
        if self._carregado:
            return
        self._carregar_dados()
        self._carregado = True

    def obter_gerente(self) -> Gerente:
        """Devolve o gerente da loja, com todas as anotações do CSV.

        O gerente é a linha de vendedores.csv cujo cargo é "gerente".
        """
        self._garantir_carregado()
        return self._gerente

    def listar_vendedores(self) -> list[Vendedor]:
        """Devolve os vendedores (cargo "vendedor") na ordem do CSV.

        Cada Vendedor já vem com seus indicadores diários e suas metas,
        cruzados pelo vendedor_id. Devolvemos uma lista nova para o chamador
        poder mexer nela sem afetar o cache interno.
        """
        self._garantir_carregado()
        return list(self._vendedores)

    def obter_vendedor(self, vendedor_id: str) -> Vendedor:
        """Busca um vendedor pelo ID exato.

        Levanta VendedorNaoEncontradoError quando o ID não existe ou quando
        pertence a alguém que não é vendedor (por exemplo, o gerente).
        """
        self._garantir_carregado()

        for vendedor in self._vendedores:
            if vendedor.vendedor_id == vendedor_id:
                return vendedor

        raise VendedorNaoEncontradoError(
            f"Vendedor com ID '{vendedor_id}' não encontrado."
        )

    def buscar_vendedor_por_nome(self, nome: str) -> Vendedor:
        """Busca um vendedor pelo nome completo ou pelo primeiro nome.

        Ignora acentos, maiúsculas e espaços extras. Se nenhum vendedor
        corresponder, ou se mais de um corresponder (por exemplo, "Ana" para
        "Ana Silva" e "Ana Souza"), levanta VendedorNaoEncontradoError com
        uma mensagem explicando o problema.
        """
        self._garantir_carregado()

        encontrados = [
            vendedor
            for vendedor in self._vendedores
            if nome_corresponde(vendedor.nome, nome)
        ]

        if not encontrados:
            raise VendedorNaoEncontradoError(
                f"Nenhum vendedor encontrado com o nome '{nome}'."
            )

        if len(encontrados) > 1:
            raise VendedorNaoEncontradoError(
                f"Mais de um vendedor encontrado com o nome '{nome}'. "
                "Use o nome completo ou o ID."
            )

        return encontrados[0]

    def obter_anotacoes_do_vendedor(
        self, vendedor_id: str
    ) -> tuple[Anotacao, ...]:
        """Devolve as anotações do gerente que falam desse vendedor.

        Usa o nome do vendedor para filtrar as anotações; as anotações sobre
        o time ("(time)") ficam de fora. Levanta VendedorNaoEncontradoError
        se o ID não for de um vendedor.
        """
        vendedor = self.obter_vendedor(vendedor_id)
        gerente = self.obter_gerente()
        return gerente.anotacoes_sobre(vendedor.nome)

    @staticmethod
    def _posicao_no_ranking(
        valor: float | None, valores: list[float | None]
    ) -> int | None:
        """Calcula a posição do valor no ranking (1 = maior valor).

        Recebe o valor do vendedor e a lista de valores de todos os colegas.
        Devolve None quando o vendedor não tem valor (fica fora do ranking).
        Empates compartilham a mesma posição.
        """
        if valor is None:
            return None

        # Quantos colegas têm valor maior? A posição é esse número + 1.
        return 1 + sum(
            1 for outro in valores if outro is not None and outro > valor
        )

    @staticmethod
    def _comparar_com_media(
        valor: float | None, media: float | None
    ) -> tuple[float | None, str]:
        """Calcula a diferença percentual e a situação em relação à média.

        A diferença é (valor - média) ÷ média. A situação é:
        - "na_media" quando a diferença fica entre -5% e +5% (inclusive);
        - "acima" quando passa de +5%;
        - "abaixo" quando fica abaixo de -5%;
        - "indisponivel" quando falta valor ou média (ou a média é zero).

        Devolve uma dupla: (diferença percentual, situação).
        """
        if valor is None or media is None or media == 0:
            return None, "indisponivel"

        diferenca = (valor - media) / media

        # Tolerância de 5% para mais ou para menos em torno da média.
        if abs(diferenca) <= 0.05:
            return diferenca, "na_media"
        if diferenca > 0:
            return diferenca, "acima"
        return diferenca, "abaixo"

    def obter_comparativo_time(
        self, vendedor_id: str, mes: str | None = None
    ) -> ComparativoTime:
        """Compara um vendedor com a média dos vendedores do time.

        A média é calculada com as somas de todos os vendedores no período:
        - ticket médio do time = valor vendido total ÷ vendas totais;
        - P.A. do time = peças totais ÷ vendas totais;
        - conversão do time = vendas totais ÷ atendimentos totais.

        O ranking usa as mesmas três métricas (1 = maior valor). Vendedor
        sem dados no período fica com valor None e fora do ranking, mas
        continua contando no total de vendedores.
        """
        self._garantir_carregado()
        vendedor = self.obter_vendedor(vendedor_id)
        vendedores = self._vendedores

        # Somas do time no período pedido (mes=None usa todo o histórico).
        total_valor = sum(v.valor_vendido(mes) for v in vendedores)
        total_vendas = sum(v.vendas(mes) for v in vendedores)
        total_pecas = sum(v.pecas(mes) for v in vendedores)
        total_atendimentos = sum(v.atendimentos(mes) for v in vendedores)

        # Média do time = somas totais ÷ base total. Se a base for zero, a
        # média fica None (não inventamos divisão por zero).
        media_ticket = total_valor / total_vendas if total_vendas > 0 else None
        media_pa = total_pecas / total_vendas if total_vendas > 0 else None
        media_conversao = (
            total_vendas / total_atendimentos
            if total_atendimentos > 0
            else None
        )

        # Para cada métrica, pegamos o valor do vendedor e de todos os
        # colegas via getattr (chama o método pelo nome: "ticket_medio",
        # "pecas_por_atendimento" ou "conversao").
        definicoes = (
            ("ticket_medio", media_ticket),
            ("pecas_por_atendimento", media_pa),
            ("conversao", media_conversao),
        )

        metricas = []
        for nome_metrica, media in definicoes:
            valor = getattr(vendedor, nome_metrica)(mes)
            valores = [
                getattr(colega, nome_metrica)(mes) for colega in vendedores
            ]

            posicao = self._posicao_no_ranking(valor, valores)
            diferenca, situacao = self._comparar_com_media(valor, media)

            metricas.append(
                MetricaComparada(
                    nome=nome_metrica,
                    valor=valor,
                    media_time=media,
                    diferenca_percentual=diferenca,
                    posicao=posicao,
                    total_vendedores=len(vendedores),
                    situacao=situacao,
                )
            )

        return ComparativoTime(
            vendedor_id=vendedor.vendedor_id,
            nome=vendedor.nome,
            metricas=tuple(metricas),
            mes=mes,
        )
