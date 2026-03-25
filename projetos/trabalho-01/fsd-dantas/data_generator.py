"""
data_generator.py
-----------------
Gerador de registros fictícios para o Trabalho 01 – FAED/PPGIA-PUCPR.

Cada registro representa um funcionário com:
  - matricula  : inteiro de 9 dígitos (chave primária de busca)
  - nome       : string aleatória (sobrenome + nome)
  - salario    : float entre 1.500 e 25.000
  - cod_setor  : inteiro entre 1 e 50

Uso:
    from data_generator import gerar_registros, salvar_csv, medir_memoria

    registros = gerar_registros(n=10_000, seed=42)
    salvar_csv(registros, "dados_10k.csv")
    info = medir_memoria(n=10_000)
"""

import csv
import random
import sys
import tracemalloc
from pathlib import Path


# ---------------------------------------------------------------------------
# Banco de nomes simplificado para geração realista sem dependências externas
# ---------------------------------------------------------------------------
_NOMES = [
    "Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda", "Gabriel",
    "Helena", "Igor", "Julia", "Lucas", "Mariana", "Nicolas", "Olivia",
    "Paulo", "Queila", "Rafael", "Sabrina", "Thiago", "Ursula", "Victor",
    "Wendy", "Xavier", "Yasmin", "Zeca",
]

_SOBRENOMES = [
    "Alves", "Barbosa", "Carvalho", "Dias", "Esteves", "Ferreira", "Gomes",
    "Hernandes", "Ito", "Jesus", "Klein", "Lima", "Martins", "Nascimento",
    "Oliveira", "Pereira", "Queiroz", "Ribeiro", "Santos", "Teixeira",
    "Ueda", "Vargas", "Wagner", "Xavier", "Yamamoto", "Zago",
]


def _nome_aleatorio(rng: random.Random) -> str:
    """Retorna 'SOBRENOME, Nome' usando o gerador local."""
    return f"{rng.choice(_SOBRENOMES)}, {rng.choice(_NOMES)}"


# ---------------------------------------------------------------------------
# Geração de registros
# ---------------------------------------------------------------------------

def gerar_registros(n: int, seed: int = 42) -> list[dict]:
    """
    Gera uma lista de *n* registros fictícios com matrículas únicas.

    Parâmetros
    ----------
    n    : quantidade de registros a gerar
    seed : semente do gerador (garante reprodutibilidade)

    Retorno
    -------
    list[dict] com chaves: 'matricula', 'nome', 'salario', 'cod_setor'
    """
    rng = random.Random(seed)
    matriculas = rng.sample(range(100_000_000, 1_000_000_000), n)

    registros = []
    for mat in matriculas:
        registros.append({
            "matricula": mat,
            "nome":      _nome_aleatorio(rng),
            "salario":   round(rng.uniform(1_500.0, 25_000.0), 2),
            "cod_setor": rng.randint(1, 50),
        })

    return registros


# ---------------------------------------------------------------------------
# Exportação CSV (opcional)
# ---------------------------------------------------------------------------

def carregar_csv(caminho: str | Path) -> list[dict]:
    """
    Carrega registros de um CSV previamente gerado por salvar_csv().

    Converte os campos de volta aos tipos corretos (int, float).
    Use esta função nos benchmarks para garantir que todas as estruturas
    de dados recebam exatamente os mesmos registros, independente de
    versão do Python ou do módulo random.

    Parâmetros
    ----------
    caminho : caminho do arquivo CSV

    Retorno
    -------
    list[dict] com chaves: 'matricula', 'nome', 'salario', 'cod_setor'
    """
    registros = []
    with Path(caminho).open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            registros.append({
                "matricula": int(row["matricula"]),
                "nome":      row["nome"],
                "salario":   float(row["salario"]),
                "cod_setor": int(row["cod_setor"]),
            })
    return registros


def salvar_csv(registros: list[dict], caminho: str | Path) -> Path:
    """
    Salva a lista de registros em um arquivo CSV.

    Parâmetros
    ----------
    registros : lista retornada por gerar_registros()
    caminho   : caminho do arquivo de saída (str ou Path)

    Retorno
    -------
    Path do arquivo criado
    """
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)

    with destino.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["matricula", "nome", "salario", "cod_setor"])
        writer.writeheader()
        writer.writerows(registros)

    return destino


# ---------------------------------------------------------------------------
# Análise de memória
# ---------------------------------------------------------------------------

def _tamanho_registro(r: dict) -> int:
    """
    Estimativa do tamanho raso de um único registro em bytes.

    Usa sys.getsizeof(), que retorna o tamanho do objeto sem seus filhos
    (shallow size). Para uma estimativa conservadora já serve; a medição
    real via tracemalloc captura o custo total.
    """
    return (
        sys.getsizeof(r)                  # dict shell
        + sys.getsizeof(r["matricula"])   # int
        + sys.getsizeof(r["nome"])        # str
        + sys.getsizeof(r["salario"])     # float
        + sys.getsizeof(r["cod_setor"])   # int
    )


def estimativa_teorica(n: int) -> dict:
    """
    Calcula a estimativa teórica de memória para *n* registros
    com base nos tamanhos típicos dos objetos Python (CPython 3.13).

    Componentes considerados por registro:
      - dict shell       : ~232 B  (tabela de hash interna com 4 entradas)
      - int matricula    :  ~28 B  (inteiro grande, fora do cache)
      - str nome         :  ~60 B  (média "Sobrenome, Nome" ≈ 14 chars)
      - float salario    :  ~24 B
      - int cod_setor    :  ~28 B  (1-50, cached pelo CPython, mas alocado)
      - ponteiro na list :   ~8 B  (referência na lista)

    Retorno
    -------
    dict com chaves: por_registro_bytes, total_bytes, total_mb
    """
    por_registro = 232 + 28 + 60 + 24 + 28 + 8   # = 380 bytes
    total = por_registro * n
    return {
        "por_registro_bytes": por_registro,
        "total_bytes":        total,
        "total_kb":           total / 1_024,
        "total_mb":           total / (1_024 ** 2),
    }


def medir_memoria(n: int, seed: int = 42) -> dict:
    """
    Mede o consumo real de memória ao gerar *n* registros usando tracemalloc.

    O tracemalloc rastreia todas as alocações Python entre start/stop,
    capturando o pico de uso — mais preciso que sys.getsizeof() recursivo.

    Retorno
    -------
    dict com: n, pico_bytes, pico_kb, pico_mb, atual_bytes, atual_mb,
              estimativa (resultado de estimativa_teorica)
    """
    tracemalloc.start()

    registros = gerar_registros(n, seed)

    atual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Tamanho amostral de 1 registro real
    amostra = _tamanho_registro(registros[0])

    est = estimativa_teorica(n)

    return {
        "n":                  n,
        "pico_bytes":         pico,
        "pico_kb":            pico / 1_024,
        "pico_mb":            pico / (1_024 ** 2),
        "atual_bytes":        atual,
        "atual_mb":           atual / (1_024 ** 2),
        "amostra_1reg_bytes": amostra,
        "estimativa":         est,
    }


# ---------------------------------------------------------------------------
# Execução direta
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerador de dados – Trabalho 01 FAED")
    parser.add_argument(
        "--csv", action="store_true",
        help="Salva os datasets em arquivos CSV na pasta 'dados/'"
    )
    parser.add_argument(
        "--memoria", action="store_true",
        help="Exibe análise de memória (estimativa teórica + tracemalloc)"
    )
    parser.add_argument(
        "--volumes", nargs="+", type=int,
        default=[10_000, 50_000, 100_000],
        help="Volumes a gerar (default: 10000 50000 100000)"
    )
    args = parser.parse_args()

    PASTA_CSV = Path(__file__).parent / "dados"

    for n in args.volumes:
        print(f"\n{'='*52}")
        print(f"  N = {n:>7,}")
        print(f"{'='*52}")

        dados = gerar_registros(n)
        mats  = [r["matricula"] for r in dados]
        sals  = [r["salario"]   for r in dados]

        print(f"  Matriculas unicas : {len(set(mats)) == n}")
        print(f"  Matricula min/max : {min(mats):,} / {max(mats):,}")
        print(f"  Salario   min/max : R$ {min(sals):,.2f} / R$ {max(sals):,.2f}")
        print(f"  Exemplo           : {dados[0]}")

        if args.csv:
            dest = PASTA_CSV / f"registros_{n}.csv"
            salvar_csv(dados, dest)
            print(f"  CSV salvo em      : {dest}")

        if args.memoria:
            info = medir_memoria(n)
            est  = info["estimativa"]
            print(f"\n  --- Memoria ---")
            print(f"  Estimativa teorica  : {est['total_mb']:.2f} MB  "
                  f"({est['por_registro_bytes']} B/registro)")
            print(f"  Medicao tracemalloc : {info['pico_mb']:.2f} MB (pico)  |  "
                  f"{info['atual_mb']:.2f} MB (final)")
            print(f"  Tamanho 1 registro  : {info['amostra_1reg_bytes']} B (sys.getsizeof shallow)")
