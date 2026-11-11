"""Serviço que guarda num arquivo JSON local os roteiros já gerados.

O arquivo é criado sozinho no primeiro registro e não vai para o git. A visão
da regional lê deste registro para saber para quais vendedores já existe um
preparo. O serviço é a única camada que conhece o formato do arquivo; o resto
do programa trabalha com objetos RegistroFeedback.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from config import REGISTRO_FEEDBACKS_ARQUIVO
from domain.excecoes import DadosIndisponiveisError
from domain.feedback_roteiro import FeedbackRoteiro
from domain.registro_feedback import RegistroFeedback


class RegistroFeedbackService:
    """Lê e grava registros de roteiros num único arquivo JSON.

    Recebe:
        arquivo: caminho do arquivo de registro (padrão: o configurado em
            config.REGISTRO_FEEDBACKS_ARQUIVO).

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

    def __init__(self, arquivo: Path = REGISTRO_FEEDBACKS_ARQUIVO):
        """Guarda o caminho do arquivo e cria o cadeado de uso interno."""
        self._arquivo = Path(arquivo)

        # Um cadeado por serviço: quem usa o serviço deve compartilhar a
        # MESMA instância entre as rotas para a proteção valer.
        self._lock = threading.Lock()

    def _ler(self) -> list[RegistroFeedback]:
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
                f"Não foi possível ler o registro de feedbacks "
                f"({self._arquivo.name}): arquivo corrompido ou inválido."
            ) from erro

        # O formato esperado é uma lista de dicionários.
        if not isinstance(dados, list):
            raise DadosIndisponiveisError(
                f"O registro de feedbacks ({self._arquivo.name}) está num "
                "formato inesperado: esperava uma lista de registros."
            )

        registros = []
        for posicao, item in enumerate(dados, start=1):
            try:
                registros.append(RegistroFeedback.de_dict(item))
            except ValueError as erro:
                # Um item inválido contamina o arquivo todo: avisamos qual é
                # o problema e deixamos o arquivo como está.
                raise DadosIndisponiveisError(
                    f"O registro de feedbacks ({self._arquivo.name}) tem um "
                    f"item inválido na posição {posicao}: {erro}"
                ) from erro

        return registros

    def _gravar(self, registros: list[RegistroFeedback]) -> None:
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

            # Troca o oficial pelo temporário de uma vez só.
            os.replace(temporario, self._arquivo)
        except OSError as erro:
            raise DadosIndisponiveisError(
                f"Não foi possível gravar o registro de feedbacks "
                f"({self._arquivo.name})."
            ) from erro
        finally:
            # Se algo falhou antes da troca, o temporário pode ter sobrado;
            # missing_ok evita erro quando ele já foi movido.
            temporario.unlink(missing_ok=True)

    def registrar(
        self,
        vendedor_id: str,
        vendedor_nome: str,
        mes_referencia: str | None,
        roteiro: FeedbackRoteiro,
    ) -> RegistroFeedback:
        """Guarda um novo registro e devolve o objeto criado.

        Recebe os dados da pessoa, o mês de referência (ou None) e o roteiro
        que a IA gerou. O ID e o horário em UTC são criados aqui, no momento
        do registro.

        O ciclo ler → acrescentar → gravar acontece dentro do cadeado, para
        dois pedidos simultâneos não apagarem o registro um do outro.
        """
        # Horário em UTC: o mesmo instante em qualquer fuso do mundo.
        registro = RegistroFeedback(
            vendedor_id=vendedor_id,
            vendedor_nome=vendedor_nome,
            gerado_em=datetime.now(timezone.utc),
            mes_referencia=mes_referencia,
            roteiro=roteiro.para_dict(),
        )

        with self._lock:
            registros = self._ler()
            registros.append(registro)
            self._gravar(registros)

        return registro

    def listar(self, vendedor_id: str | None = None) -> list[RegistroFeedback]:
        """Lista os registros do mais novo para o mais antigo.

        Com vendedor_id, devolve só os registros daquela pessoa. Sem ele,
        devolve todos.
        """
        with self._lock:
            registros = self._ler()

        if vendedor_id is not None:
            registros = [
                registro
                for registro in registros
                if registro.vendedor_id == vendedor_id
            ]

        # reverse=True coloca a data mais recente primeiro.
        return sorted(
            registros, key=lambda registro: registro.gerado_em, reverse=True
        )

    def ultimo_de(self, vendedor_id: str) -> RegistroFeedback | None:
        """Devolve o registro mais recente de um vendedor, ou None.

        None significa "essa pessoa ainda não teve roteiro gerado".
        """
        registros = self.listar(vendedor_id)
        if not registros:
            return None
        return registros[0]

    def contar_por_vendedor(self) -> dict[str, int]:
        """Conta quantos registros existem para cada vendedor.

        Devolve um dicionário "vendedor_id → quantidade". Quem não tem
        registro simplesmente não aparece.
        """
        with self._lock:
            registros = self._ler()

        contagem: dict[str, int] = {}
        for registro in registros:
            # get com padrão 0 evita KeyError na primeira ocorrência.
            contagem[registro.vendedor_id] = (
                contagem.get(registro.vendedor_id, 0) + 1
            )
        return contagem
