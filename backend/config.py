"""Configuração central do backend: caminhos e informações fixas do desafio.

Este arquivo reúne num só lugar onde ficam os arquivos de dados e os dados
fixos da loja (L004). O resto do código importa estas constantes em vez de
repetir caminhos e nomes soltos, o que evita erros de digitação e facilita
mudanças futuras.
"""

from pathlib import Path

# Path: o "molde" (classe) do Python para representar caminhos de arquivos e
# pastas. __file__ é o caminho deste próprio arquivo (config.py). .resolve()
# devolve o caminho absoluto (completo, desde a raiz do disco) e .parent pega a
# pasta que contém o arquivo (backend/). Assim, DATA_DIR aponta sempre para
# backend/data, não importa de qual pasta o projeto seja executado.
DATA_DIR = Path(__file__).resolve().parent / "data"

# Nomes dos arquivos CSV que vivem dentro de DATA_DIR. São só os nomes (sem
# caminho); quem for ler o arquivo junta DATA_DIR + nome.
ARQUIVO_VENDEDORES = "vendedores.csv"
ARQUIVO_INDICADORES_DIARIOS = "indicadores_diarios_vendedor.csv"
ARQUIVO_METAS_VENDEDOR = "metas_vendedor.csv"
ARQUIVO_ANOTACOES_GERENTE = "anotacoes_gerente.csv"

# Identificação da loja do desafio. O arquivo vendedores.csv não tem coluna de
# loja, então esse dado vem do LEIAME do desafio. Todos os funcionários do CSV
# pertencem a esta loja.
LOJA_ID = "L004"
LOJA_NOME = "Aurora Shopping Centro"

# Texto que aparece na coluna "sobre" das anotações quando o gerente escreve
# sobre o time inteiro, e não sobre uma pessoa específica.
ANOTACAO_SOBRE_TIME = "(time)"
