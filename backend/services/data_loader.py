"""Serviço de carga dos CSVs do desafio, usando Pandas.

DataLoader é a única camada que conhece Pandas: lê os arquivos de backend/data,
valida as colunas e monta objetos de domínio (Vendedor, Gerente, Anotacao,
AnotacaoRegional, IndicadorDiario). Nenhum DataFrame ou NaN vaza para o domínio.
"""

from pathlib import Path

import pandas as pd

from config import (
    ARQUIVO_ANOTACOES_GERENTE,
    ARQUIVO_ANOTACOES_REGIONAL,
    ARQUIVO_INDICADORES_DIARIOS,
    ARQUIVO_METAS_LOJA,
    ARQUIVO_METAS_VENDEDOR,
    ARQUIVO_VENDEDORES,
    DATA_DIR,
    LOJA_ID,
    LOJA_NOME,
)
from domain.anotacao import Anotacao
from domain.anotacao_regional import AnotacaoRegional
from domain.comparativo_time import ComparativoTime, MetricaComparada
from domain.excecoes import DadosIndisponiveisError, VendedorNaoEncontradoError
from domain.gerente import Gerente
from domain.indicador_diario import IndicadorDiario
from domain.texto import nome_corresponde
from domain.vendedor import Vendedor
from services.registro_anotacoes import RegistroAnotacoesService
from services.registro_anotacoes_regional import (
    RegistroAnotacoesRegionalService,
)


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
        registro_anotacoes: serviço das anotações NOVAS, escritas na
            interface (padrão: None = ignora essas anotações e usa só o CSV).
        registro_anotacoes_regional: serviço das anotações NOVAS da regional,
            também escritas na interface (padrão: None = usa só o CSV da
            regional, mantendo o comportamento antigo).

    A leitura é preguiçosa: nada é lido no construtor. Na primeira chamada de
    um método público, os quatro arquivos de vendas são lidos uma única vez e
    ficam em cache interno; as chamadas seguintes reaproveitam os dados. Os
    dois CSVs da regional têm um cache próprio, carregado apenas quando a
    visão executiva precisar deles.

    Exceção ao cache: quando registro_anotacoes é informado, as anotações
    novas são lidas do serviço a cada obter_gerente(). Elas mudam a cada
    gravação feita na interface, então guardar uma cópia faria uma anotação
    recém-escrita só aparecer depois de reiniciar o servidor. O CSV, que não
    muda durante a execução, continua sendo lido uma vez só.
    """

    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        loja_id: str = LOJA_ID,
        loja_nome: str = LOJA_NOME,
        registro_anotacoes: RegistroAnotacoesService | None = None,
        registro_anotacoes_regional: RegistroAnotacoesRegionalService
        | None = None,
    ):
        """Guarda a configuração; os arquivos só serão lidos depois."""
        self._data_dir = Path(data_dir)
        self._loja_id = loja_id
        self._loja_nome = loja_nome

        # Fonte extra de anotações (as escritas no site). None é o padrão
        # histórico: nesse caso o comportamento é exatamente o de antes.
        self._registro_anotacoes = registro_anotacoes

        # Fonte extra das anotações da REGIONAL (as escritas na visão dela).
        # Separado do serviço acima porque são arquivos e públicos diferentes:
        # um texto do gerente não pode invadir o histórico da regional. None
        # mantém o comportamento antigo (só o CSV).
        self._registro_anotacoes_regional = registro_anotacoes_regional

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

        # O gerente também tem vendas próprias no arquivo de indicadores.
        # Guardamos essas vendas separadamente para a visão executiva, sem
        # misturar com a lista de vendedores nem com o comparativo do time.
        self._vendas_gerente: Vendedor | None = None

        # Dados da visão regional (Etapa 3). Ficam num cache separado porque
        # só a visão executiva precisa deles: o feedback individual continua
        # funcionando mesmo que estes dois CSVs não existam na pasta.
        self._regional_carregado = False
        self._anotacoes_regional: tuple[AnotacaoRegional, ...] = ()
        self._metas_loja: dict[str, float] = {}

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

    def _montar_vendedor(
        self,
        vendedor_id: str,
        nome: str,
        cargo: str,
        metas: dict[str, float] | None = None,
    ) -> Vendedor:
        """Monta um Vendedor com os indicadores já agrupados por ID.

        Recebe o ID, o nome, o cargo e, opcionalmente, as metas do mês.
        Devolve um Vendedor com a loja da configuração e a lista de
        indicadores que já foi agrupada em _carregar_dados. metas=None vira
        um dicionário vazio dentro do próprio Vendedor.

        Existe para o gerente reaproveitar exatamente a mesma rotina dos
        vendedores, sem duplicar a montagem em dois lugares.
        """
        return Vendedor(
            vendedor_id=vendedor_id,
            nome=nome,
            cargo=cargo,
            loja_id=self._loja_id,
            loja_nome=self._loja_nome,
            indicadores=self._indicadores_por_vendedor.get(vendedor_id, ()),
            metas=metas,
        )

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
                self._montar_vendedor(
                    vendedor_id=vendedor_id,
                    nome=_texto(linha["nome"]),
                    cargo=cargo,
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

        # 7) Monta as vendas do gerente como um Vendedor, para a visão da
        # regional reaproveitar as mesmas métricas (ticket médio, P.A. etc.).
        # Sem metas: metas=None porque o gerente não tem meta individual.
        # Este objeto NÃO entra em _vendedores, então continua fora das
        # listagens, das buscas por ID e do comparativo do time.
        self._vendas_gerente = self._montar_vendedor(
            vendedor_id=self._gerente.gerente_id,
            nome=self._gerente.nome,
            cargo="gerente",
        )

    def _garantir_carregado(self) -> None:
        """Carrega os arquivos na primeira chamada; depois só reaproveita."""
        if self._carregado:
            return
        self._carregar_dados()
        self._carregado = True

    def obter_gerente(self) -> Gerente:
        """Devolve o gerente da loja, com todas as anotações conhecidas.

        O gerente é a linha de vendedores.csv cujo cargo é "gerente".

        As anotações vêm de duas fontes:
        1) o CSV (anotacoes_gerente.csv), lido uma vez e guardado em cache;
        2) o serviço de anotações novas (as escritas na interface), quando
           ele foi informado no construtor.

        Por que o serviço é lido a cada chamada: uma anotação nova pode ser
        gravada a qualquer momento e a próxima leitura já precisa mostrá-la.
        Uma cópia congelada só apareceria depois de reiniciar o servidor. O
        CSV, que não muda durante a execução, continua em cache — assim a
        parte cara (ler o arquivo com Pandas) é feita uma vez só.

        Ordem: o Gerente ordena por data com sorted, que é estável. Passamos
        primeiro as anotações do CSV e depois as novas; por isso, em datas
        iguais, as do CSV vêm antes, e entre as novas vale a ordem em que
        foram registradas.

        Sem o serviço informado, devolvemos o MESMO objeto montado na carga
        do CSV: o comportamento de quem não usa anotações novas não muda.
        """
        self._garantir_carregado()

        if self._registro_anotacoes is None:
            return self._gerente

        # Uma anotação nova é gravada a cada POST; o serviço é relido aqui.
        anotacoes_novas = self._registro_anotacoes.listar()

        # Tupla nova, do CSV para as novas. O gerente do cache não é alterado
        # (ele pode continuar sendo usado por quem não vê anotações novas).
        anotacoes = (*self._anotacoes, *anotacoes_novas)

        return Gerente(
            gerente_id=self._gerente.gerente_id,
            nome=self._gerente.nome,
            loja_id=self._gerente.loja_id,
            loja_nome=self._gerente.loja_nome,
            anotacoes=anotacoes,
        )

    def obter_vendas_do_gerente(self) -> Vendedor:
        """Devolve as vendas do próprio gerente como um Vendedor.

        Serve para a visão executiva da regional reaproveitar os mesmos
        métodos de métrica do Vendedor (valor_vendido, ticket_medio,
        pecas_por_atendimento etc.) sem criar fórmulas novas.

        O objeto vem com cargo "gerente", a loja da configuração e SEM metas
        (o gerente não tem meta individual), então atingimento_meta devolve
        None.

        Importante: ele NÃO entra em listar_vendedores(), obter_vendedor()
        nem no comparativo do time; continua sendo só uma leitura das vendas
        do gerente.
        """
        self._garantir_carregado()
        return self._vendas_gerente

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

        Como a busca parte de obter_gerente(), o resultado já inclui as
        anotações novas gravadas na interface (quando o DataLoader recebeu o
        serviço delas). É por aqui que o histórico, o prompt da IA e a visão
        regional enxergam o texto recém-escrito.
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

    # ------------------------------------------------------------------
    # Dados da visão regional (Etapa 3)
    # ------------------------------------------------------------------

    def _carregar_regional(self) -> None:
        """Lê os CSVs da regional e monta as coleções internas uma vez.

        Usa um cache próprio (self._regional_carregado), separado do cache
        principal: as anotações da regional e as metas da loja só são usadas
        pela visão executiva. Assim, a leitura dos dados de vendas não passa
        a depender destes dois arquivos.
        """
        # 1) Lê os arquivos reaproveitando _ler_csv, que já valida a
        # existência do arquivo e as colunas obrigatórias.
        anotacoes_df = self._ler_csv(
            ARQUIVO_ANOTACOES_REGIONAL,
            ("data", "autora", "anotacao"),
            coluna_data="data",
        )
        metas_df = self._ler_csv(
            ARQUIVO_METAS_LOJA,
            ("mes", "meta_valor"),
            colunas_texto=("mes",),
        )

        # 2) Monta as anotações e ordena por data. O CSV pode não estar em
        # ordem cronológica, e a visão executiva precisa da leitura em ordem.
        anotacoes = [
            AnotacaoRegional(
                data=linha["data"],
                autora=_texto(linha["autora"]),
                texto=_texto(linha["anotacao"]),
            )
            for _, linha in anotacoes_df.iterrows()
        ]
        self._anotacoes_regional = tuple(
            sorted(anotacoes, key=lambda anotacao: anotacao.data)
        )

        # 3) Monta o dicionário de metas da loja: {"2026-10": 317200.0, ...}.
        metas: dict[str, float] = {}
        for _, linha in metas_df.iterrows():
            mes = _texto(linha["mes"])
            metas[mes] = _numero(
                linha["meta_valor"], ARQUIVO_METAS_LOJA, "meta_valor"
            )
        self._metas_loja = metas

    def _garantir_regional_carregado(self) -> None:
        """Carrega os CSVs da regional na primeira chamada; depois reaproveita."""
        if self._regional_carregado:
            return
        self._carregar_regional()
        self._regional_carregado = True

    def listar_anotacoes_regional(self) -> tuple[AnotacaoRegional, ...]:
        """Devolve as anotações da regional em ordem cronológica.

        As anotações vêm de duas fontes:
        1) o CSV (anotacoes_regional.csv), lido uma vez e guardado em cache;
        2) o serviço de anotações novas da regional (as escritas na
           interface), quando ele foi informado no construtor.

        Por que o serviço é lido a cada chamada: uma anotação nova pode ser
        gravada a qualquer momento e a próxima leitura já precisa mostrá-la.
        Uma cópia congelada só apareceria depois de reiniciar o servidor. O
        CSV, que não muda durante a execução, continua em cache — assim a
        parte cara (ler o arquivo com Pandas) é feita uma vez só.

        Ordem: sorted por data é estável. Passamos primeiro as do CSV e depois
        as novas; por isso, em datas iguais, as do CSV vêm antes, e entre as
        novas vale a ordem em que foram registradas.

        Sem o serviço informado, devolvemos o MESMO objeto montado na carga
        do CSV: o comportamento de quem não usa anotações novas não muda.

        Levanta DadosIndisponiveisError se o arquivo não existir ou se
        faltar uma coluna obrigatória.
        """
        self._garantir_regional_carregado()

        if self._registro_anotacoes_regional is None:
            return self._anotacoes_regional

        # Uma anotação nova é gravada a cada POST; o serviço é relido aqui.
        anotacoes_novas = self._registro_anotacoes_regional.listar()

        # Tupla nova, do CSV para as novas, e ordenação estável por data.
        # O cache do CSV não é alterado (ele continua valendo para quem não
        # vê anotações novas).
        anotacoes = (*self._anotacoes_regional, *anotacoes_novas)
        return tuple(
            sorted(anotacoes, key=lambda anotacao: anotacao.data)
        )

    def obter_meta_loja(self, mes: str) -> float | None:
        """Devolve a meta da loja em reais para o mês "AAAA-MM".

        Devolve None quando o mês não existe no arquivo (não é erro: a loja
        pode simplesmente não ter meta cadastrada naquele mês).

        Exemplo: obter_meta_loja("2026-10") devolve 317200.0.
        """
        self._garantir_regional_carregado()
        return self._metas_loja.get(mes)

    def listar_metas_loja(self) -> dict[str, float]:
        """Devolve todas as metas da loja: mês ("AAAA-MM") → valor em reais.

        Devolvemos uma CÓPIA do dicionário (dict(...)). Sem a cópia, quem
        chamasse este método poderia alterar o cache interno e mudar as
        metas para o resto do programa.
        """
        self._garantir_regional_carregado()
        return dict(self._metas_loja)
