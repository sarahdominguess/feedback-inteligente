"""Serviço que guarda num arquivo JSON os roteiros gerados para o gerente.

A gerente regional prepara roteiros de feedback para o gerente de cada loja.
Este registro fica separado de registro_feedbacks.json (o dos vendedores): são
acompanhamentos de naturezas diferentes, e misturar os dois tornaria confuso
saber o que cada item representa.

O arquivo é criado sozinho no primeiro registro e não vai para o git. O serviço
é a única camada que conhece o formato do arquivo; o resto do programa trabalha
com objetos RegistroFeedbackGerente.
"""

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from config import REGISTRO_FEEDBACKS_REGIONAL_ARQUIVO
from domain.excecoes import DadosIndisponiveisError
from domain.feedback_roteiro import FeedbackRoteiro
from domain.registro_feedback_gerente import RegistroFeedbackGerente

# Logger: canal de registro do servidor. Usamos só para avisar de um problema
# que não impede a gravação (o temporário que não pôde ser apagado).
logger = logging.getLogger(__name__)


class RegistroFeedbackRegionalService:
    """Lê e grava os roteiros do gerente num único arquivo JSON.

    Recebe:
        arquivo: caminho do arquivo de registro (padrão: o configurado em
            config.REGISTRO_FEEDBACKS_REGIONAL_ARQUIVO).

    Termos:
        JSON: formato de texto organizado em pares nome/valor, usado para
            gravar dados em arquivo de forma legível.
        Thread: uma "linha de execução" do programa. O FastAPI (servidor da
            API) atende vários pedidos ao mesmo tempo em threads diferentes;
            por isso duas gravações podem tentar acontecer juntas.
        Lock ("trava"): um cadeado do Python. Só a thread que pegou o cadeado
            mexe no arquivo; as outras esperam a vez. Isso evita que duas
            gravações se misturem e percam registros.
        Escrita atômica: gravar primeiro num arquivo temporário e só então
            trocar o oficial com os.replace. Quem lê vê sempre o arquivo
            antigo ou o novo completo, nunca um pela metade.

    O arquivo inexistente significa "nenhum registro ainda" (lista vazia) e
    não é criado até o primeiro registrar().
    """

    def __init__(self, arquivo: Path = REGISTRO_FEEDBACKS_REGIONAL_ARQUIVO):
        """Guarda o caminho do arquivo e cria o cadeado de uso interno."""
        self._arquivo = Path(arquivo)

        # Um cadeado por serviço: quem usa o serviço deve compartilhar a
        # MESMA instância entre as rotas para a proteção valer.
        self._lock = threading.Lock()

    def _ler(self) -> list[RegistroFeedbackGerente]:
        """Lê o arquivo e devolve a lista de registros na ordem gravada.

        Devolve lista vazia quando o arquivo ainda não existe (não é erro).

        Levanta DadosIndisponiveisError, SEM apagar nem alterar o arquivo,
        quando o conteúdo não é um JSON válido ou não tem o formato esperado
        (uma lista de registros). É melhor falhar com mensagem clara do que
        sobrescrever um arquivo que pode conter história.
        """
        if not self._arquivo.is_file():
            return []

        try:
            with self._arquivo.open(encoding="utf-8") as arquivo_aberto:
                dados = json.load(arquivo_aberto)
        except (OSError, json.JSONDecodeError) as erro:
            # OSError cobre falhas de leitura; JSONDecodeError, texto que não
            # é JSON. Nunca mostramos o conteúdo inteiro na mensagem.
            raise DadosIndisponiveisError(
                f"Não foi possível ler o registro de feedbacks da regional "
                f"({self._arquivo.name}): arquivo corrompido ou inválido."
            ) from erro

        # O formato esperado é uma lista de dicionários.
        if not isinstance(dados, list):
            raise DadosIndisponiveisError(
                f"O registro de feedbacks da regional "
                f"({self._arquivo.name}) está num formato inesperado: "
                "esperava uma lista de registros."
            )

        registros = []
        for posicao, item in enumerate(dados, start=1):
            try:
                registros.append(RegistroFeedbackGerente.de_dict(item))
            except ValueError as erro:
                # Um item inválido contamina o arquivo todo: avisamos qual é
                # o problema e deixamos o arquivo como está.
                raise DadosIndisponiveisError(
                    f"O registro de feedbacks da regional "
                    f"({self._arquivo.name}) tem um item inválido na posição "
                    f"{posicao}: {erro}"
                ) from erro

        return registros

    def _substituir_oficial(self, temporario: Path) -> None:
        """Troca o arquivo oficial pelo temporário, tentando algumas vezes.

        No Windows é comum um antivírus ou o indexador de arquivos abrir o
        temporário recém-gravado por alguns milissegundos. Nesse intervalo o
        os.replace falha com PermissionError ("arquivo em uso") mesmo estando
        tudo certo. Tentar de novo é seguro: a troca não tem efeito parcial —
        ou acontece, ou o oficial continua sendo o anterior.

        A espera é curta e o número de tentativas é pequeno de propósito: não
        queremos segurar um pedido da API por causa de um arquivo travado.
        """
        tentativas = 5

        for tentativa in range(1, tentativas + 1):
            try:
                os.replace(temporario, self._arquivo)
                return
            except PermissionError:
                if tentativa == tentativas:
                    raise
                # 20 milissegundos costumam bastar para o arquivo ser solto.
                time.sleep(0.02)

    def _gravar(self, registros: list[RegistroFeedbackGerente]) -> None:
        """Grava a lista inteira no arquivo de forma atômica.

        1) Escreve num arquivo temporário na MESMA pasta (assim a troca é
           rápida e não muda de disco);
        2) força a gravação no disco com flush + fsync (durabilidade);
        3) troca o arquivo oficial pelo temporário com os.replace, que é uma
           operação atômica do sistema operacional.
        """
        # Lista de dicionários prontos para virar JSON.
        conteudo = [registro.para_dict() for registro in registros]

        # O temporário fica ao lado do oficial, com o sufixo .tmp.
        temporario = self._arquivo.with_name(self._arquivo.name + ".tmp")

        try:
            # A pasta pode não existir ainda (ex.: backend/data apagada).
            self._arquivo.parent.mkdir(parents=True, exist_ok=True)

            with temporario.open("w", encoding="utf-8") as arquivo_aberto:
                # ensure_ascii=False mantém acentos legíveis no arquivo.
                json.dump(
                    conteudo,
                    arquivo_aberto,
                    ensure_ascii=False,
                    indent=2,
                )
                arquivo_aberto.flush()
                # fsync garante que os dados saíram da memória para o disco.
                os.fsync(arquivo_aberto.fileno())

            # Troca o oficial pelo temporário (com tentativas no Windows).
            self._substituir_oficial(temporario)
        except OSError as erro:
            raise DadosIndisponiveisError(
                f"Não foi possível gravar o registro de feedbacks da regional "
                f"({self._arquivo.name})."
            ) from erro
        finally:
            # Se algo falhou antes da troca, o temporário pode ter sobrado;
            # missing_ok evita erro quando ele já foi movido.
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                # O arquivo pode continuar preso por um instante (antivírus).
                # Deixar o temporário para trás não corrompe nada: a próxima
                # gravação abre o mesmo nome com "w" e o reaproveita. Não
                # podemos levantar erro aqui, senão esconderíamos o erro real
                # que está subindo do bloco acima.
                logger.warning(
                    "Não foi possível remover o temporário %s; ele será "
                    "reaproveitado na próxima gravação.",
                    temporario,
                )

    def registrar(
        self,
        loja_id: str,
        loja_nome: str,
        gerente_id: str,
        gerente_nome: str,
        mes_referencia: str | None,
        roteiro: FeedbackRoteiro,
    ) -> RegistroFeedbackGerente:
        """Guarda um novo registro e devolve o objeto criado.

        Recebe a loja, o gerente avaliado, o mês de referência (ou None) e o
        roteiro que a IA gerou. O ID e o horário em UTC são criados aqui, no
        momento do registro.

        O ciclo ler → acrescentar → gravar acontece dentro do cadeado, para
        dois pedidos simultâneos não apagarem o registro um do outro.

        Exemplo: registrar("L004", "Aurora Shopping Centro", "C0030",
        "Diego Furtado", "2026-10", roteiro)
        """
        # Horário em UTC: o mesmo instante em qualquer fuso do mundo.
        registro = RegistroFeedbackGerente(
            loja_id=loja_id,
            loja_nome=loja_nome,
            gerente_id=gerente_id,
            gerente_nome=gerente_nome,
            gerado_em=datetime.now(timezone.utc),
            mes_referencia=mes_referencia,
            roteiro=roteiro.para_dict(),
        )

        with self._lock:
            registros = self._ler()
            registros.append(registro)
            self._gravar(registros)

        return registro

    def listar(self, loja_id: str | None = None) -> list[RegistroFeedbackGerente]:
        """Lista os registros do mais novo para o mais antigo.

        Com loja_id, devolve só os registros daquela loja. Sem ele, devolve
        todos.

        A ordem segue a mesma convenção do registro dos vendedores: a data
        mais recente primeiro, para a tela mostrar o roteiro recém-gerado no
        topo da lista.
        """
        with self._lock:
            registros = self._ler()

        if loja_id is not None:
            registros = [
                registro
                for registro in registros
                if registro.loja_id == loja_id
            ]

        # reverse=True coloca a data mais recente primeiro.
        return sorted(
            registros, key=lambda registro: registro.gerado_em, reverse=True
        )

    def ultimo_de(self, loja_id: str) -> RegistroFeedbackGerente | None:
        """Devolve o registro mais recente de uma loja, ou None.

        None significa "essa loja ainda não teve roteiro para o gerente".
        """
        registros = self.listar(loja_id)
        if not registros:
            return None
        return registros[0]
