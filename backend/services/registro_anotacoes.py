"""Serviço que guarda num arquivo JSON as anotações NOVAS escritas no site.

As anotações originais continuam no CSV (anotacoes_gerente.csv), que é dado de
origem e não é alterado pelo programa. As anotações digitadas pelo gerente na
interface ficam neste arquivo à parte, criado sozinho na primeira gravação e
ignorado pelo git (é dado de execução, não código).

Este serviço é a única camada que conhece o formato do arquivo; o resto do
programa trabalha com objetos Anotacao, do domínio.
"""

import json
import os
import threading
from datetime import date, datetime
from pathlib import Path

from config import ANOTACAO_TEXTO_MAXIMO, ANOTACOES_NOVAS_ARQUIVO
from domain.anotacao import Anotacao
from domain.excecoes import AnotacaoInvalidaError, DadosIndisponiveisError


def _anotacao_para_dict(anotacao: Anotacao) -> dict:
    """Transforma uma Anotacao no formato gravado no arquivo.

    Recebe a anotação do domínio e devolve um dicionário simples (o formato
    que vira JSON). A data vira texto "AAAA-MM-DD" porque JSON não tem tipo
    de data; esse formato é o mesmo que o resto do sistema já usa.

    Exemplo: uma anotação de 08/10/2026 vira
    {"data": "2026-10-08", "sobre": "Bianca Rocha", "texto": "..."}.
    """
    return {
        "data": anotacao.data.isoformat(),
        "sobre": anotacao.sobre,
        "texto": anotacao.texto,
    }


def _anotacao_de_dict(item) -> Anotacao:
    """Transforma um item lido do arquivo numa Anotacao.

    Recebe o dicionário gravado e devolve a entidade do domínio. Levanta
    ValueError quando o item não tem o formato esperado; quem chama (o
    serviço) transforma isso num erro amigável e NÃO apaga o arquivo.

    O texto é devolvido exatamente como está no arquivo: nada é corrigido,
    resumido ou reinterpretado.
    """
    # Cada item precisa ser um objeto com os três campos de texto.
    if not isinstance(item, dict):
        raise ValueError("cada item deve ser um objeto com data, sobre e texto")

    data_texto = item.get("data")
    sobre = item.get("sobre")
    texto = item.get("texto")

    if not all(
        isinstance(valor, str) for valor in (data_texto, sobre, texto)
    ):
        raise ValueError("os campos data, sobre e texto devem ser textos")

    try:
        # fromisoformat entende "AAAA-MM-DD" e devolve um objeto date.
        dia = date.fromisoformat(data_texto)
    except ValueError as erro:
        raise ValueError(f'data inválida: "{data_texto}"') from erro

    return Anotacao(data=dia, sobre=sobre, texto=texto)


class RegistroAnotacoesService:
    """Lê e grava anotações novas num único arquivo JSON.

    Recebe:
        arquivo: caminho do arquivo de registro (padrão: o configurado em
            config.ANOTACOES_NOVAS_ARQUIVO).

    Termos:
        JSON: arquivo de texto com dados organizados em pares nome/valor,
            usado para gravar informações de forma legível.
        Thread: uma "linha de execução" do programa. O FastAPI (servidor da
            API) atende vários pedidos ao mesmo tempo em threads diferentes;
            por isso duas gravações podem tentar acontecer juntas.
        Lock ("trava"): um cadeado do Python. Só a thread que pegou o cadeado
            mexe no arquivo; as outras esperam a vez. Isso evita que duas
            gravações se misturem e percam anotações.
        Escrita atômica: gravar primeiro num arquivo temporário e só então
            trocar o oficial com os.replace. Quem lê vê sempre o arquivo
            antigo ou o novo completo, nunca um pela metade.

    O arquivo inexistente significa "nenhuma anotação nova ainda" (lista
    vazia) e não é criado até o primeiro registrar().
    """

    def __init__(self, arquivo: Path = ANOTACOES_NOVAS_ARQUIVO):
        """Guarda o caminho do arquivo e cria o cadeado de uso interno."""
        self._arquivo = Path(arquivo)

        # Um cadeado por serviço: quem usa o serviço deve compartilhar a
        # MESMA instância entre as rotas para a proteção valer.
        self._lock = threading.Lock()

    def _ler(self) -> list[Anotacao]:
        """Lê o arquivo e devolve as anotações na ordem em que foram gravadas.

        Devolve lista vazia quando o arquivo ainda não existe (não é erro).

        Levanta DadosIndisponiveisError, SEM apagar nem alterar o arquivo,
        quando o conteúdo não é um JSON válido ou não tem o formato esperado
        (uma lista de anotações). É melhor falhar com mensagem clara do que
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
                f"Não foi possível ler o registro de anotações "
                f"({self._arquivo.name}): arquivo corrompido ou inválido."
            ) from erro

        # O formato esperado é uma lista de dicionários.
        if not isinstance(dados, list):
            raise DadosIndisponiveisError(
                f"O registro de anotações ({self._arquivo.name}) está num "
                "formato inesperado: esperava uma lista de anotações."
            )

        anotacoes = []
        for posicao, item in enumerate(dados, start=1):
            try:
                anotacoes.append(_anotacao_de_dict(item))
            except ValueError as erro:
                # Um item inválido contamina o arquivo todo: avisamos qual é
                # o problema e deixamos o arquivo como está.
                raise DadosIndisponiveisError(
                    f"O registro de anotações ({self._arquivo.name}) tem um "
                    f"item inválido na posição {posicao}: {erro}"
                ) from erro

        return anotacoes

    def _gravar(self, anotacoes: list[Anotacao]) -> None:
        """Grava a lista inteira no arquivo de forma atômica.

        1) Escreve num arquivo temporário na MESMA pasta (assim a troca é
           rápida e não muda de disco);
        2) força a gravação no disco com flush + fsync (durabilidade);
        3) troca o arquivo oficial pelo temporário com os.replace, que é uma
           operação atômica do sistema operacional.
        """
        # Lista de dicionários prontos para virar JSON.
        conteudo = [_anotacao_para_dict(anotacao) for anotacao in anotacoes]

        # O temporário fica ao lado do oficial, com o sufixo .tmp.
        temporario = self._arquivo.with_name(self._arquivo.name + ".tmp")

        try:
            # A pasta pode não existir ainda (ex.: backend/data apagada).
            self._arquivo.parent.mkdir(parents=True, exist_ok=True)

            with temporario.open("w", encoding="utf-8") as arquivo_aberto:
                # ensure_ascii=False mantém acentos e quebras de linha
                # legíveis no arquivo.
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
                f"Não foi possível gravar o registro de anotações "
                f"({self._arquivo.name})."
            ) from erro
        finally:
            # Se algo falhou antes da troca, o temporário pode ter sobrado;
            # missing_ok evita erro quando ele já foi movido.
            temporario.unlink(missing_ok=True)

    def registrar(
        self,
        sobre: str,
        texto: str,
        data: date | None = None,
    ) -> Anotacao:
        """Valida, grava e devolve uma anotação nova.

        Recebe:
            sobre: sobre quem é a anotação (ex.: "Bianca Rocha" ou "(time)").
            texto: o que o gerente escreveu. É gravado como digitado, sem
                corrigir nem resumir; só os espaços das pontas saem.
            data: dia da anotação. O padrão None usa a data de hoje NO
                SERVIDOR — e não a data do computador de quem usa o site,
                que poderia ser adulterada. O parâmetro existe para os testes
                conseguirem fixar um dia.

        Devolve a Anotacao criada (com a data já resolvida).

        Levanta AnotacaoInvalidaError quando "sobre" está vazio, quando o
        texto está vazio (ou só com espaços), quando passa de
        ANOTACAO_TEXTO_MAXIMO caracteres ou quando a data não é um dia.

        Exemplo: registrar("Bianca Rocha", " cliente elogiou ")
        grava o texto "cliente elogiou" e devolve a anotação do dia.
        """
        # ----- De quem é a anotação ---------------------------------------
        if not isinstance(sobre, str) or sobre.strip() == "":
            raise AnotacaoInvalidaError(
                "Não foi possível saber sobre quem é a anotação. "
                "Escolha um colaborador e tente de novo."
            )

        # ----- O que foi escrito ------------------------------------------
        if not isinstance(texto, str):
            raise AnotacaoInvalidaError(
                "A anotação precisa ser um texto."
            )

        # strip() tira espaços, tabulações e quebras de linha das PONTAS.
        # As quebras de linha do meio do texto continuam intactas.
        texto_limpo = texto.strip()

        if texto_limpo == "":
            raise AnotacaoInvalidaError(
                "Escreva alguma coisa antes de salvar a anotação."
            )

        if len(texto_limpo) > ANOTACAO_TEXTO_MAXIMO:
            raise AnotacaoInvalidaError(
                f"A anotação pode ter no máximo {ANOTACAO_TEXTO_MAXIMO} "
                f"caracteres. Esta tem {len(texto_limpo)}."
            )

        # ----- Quando foi escrita -----------------------------------------
        if data is None:
            # date.today() usa o relógio do servidor.
            dia = date.today()
        elif isinstance(data, datetime):
            # datetime é "dia + hora". O registro guarda só o dia, então
            # recusamos em vez de descartar a hora em silêncio.
            raise AnotacaoInvalidaError(
                "A data da anotação deve ser um dia, sem horário."
            )
        elif isinstance(data, date):
            dia = data
        else:
            raise AnotacaoInvalidaError("A data da anotação é inválida.")

        # Entidade do domínio: imutável e igual à usada pelas anotações do
        # CSV, para o resto do sistema não precisar saber de onde veio.
        anotacao = Anotacao(
            data=dia,
            sobre=sobre.strip(),
            texto=texto_limpo,
        )

        # O ciclo ler → acrescentar → gravar acontece dentro do cadeado, para
        # dois pedidos simultâneos não apagarem a anotação um do outro.
        with self._lock:
            anotacoes = self._ler()
            anotacoes.append(anotacao)
            self._gravar(anotacoes)

        return anotacao

    def listar(self) -> tuple[Anotacao, ...]:
        """Devolve todas as anotações novas, na ordem em que foram gravadas.

        A ordem é a do arquivo (mais antiga primeiro). Quem precisar da mais
        recente primeiro ordena na hora de exibir — o serviço não impõe uma
        ordem diferente da que foi registrada.

        Exemplo: listar() devolve () antes da primeira gravação.
        """
        with self._lock:
            anotacoes = self._ler()

        # tuple deixa claro que a coleção é só de leitura para quem recebe.
        return tuple(anotacoes)
