# Geração de dados sintéticos para benchmarks de estruturas de dados.
#
# Gera N registros fictícios por volume, com 5 rodadas independentes cada.
# Cada registro contém: Matrícula (inteiro de 9 dígitos único), Nome, Salário, Código do Setor.
#
# Reprodutibilidade: usa random.Random(seed) — gerador determinístico e seedável.
# Cada par (volume, rodada) recebe uma seed derivada (SEED + N + k), garantindo
# que os 5 datasets de cada volume sejam distintos entre si mas sempre reprodutíveis.
# O embaralhamento final usa o mesmo gerador seedado, mantendo a consistência.

import random
import csv
import os
import time

SEED     = 42
VOLUMES  = [10_000, 50_000, 100_000]
RODADAS  = 5
OUT_DIR  = "data"

NOMES = [
    "Roger Walters", "Freddie Mercury", "Brian May", "Tyler Joseph",
    "Josh Dun", "Hayley Williams", "Ozzy Osbourne", "David Bowie",
    "Kurt Cobain", "Janis Joplin", "Jimi Hendrix", "Amy Winehouse",
    "Jim Morrison", "Mick Jagger", "Robert Plant", "Elvis Presley"
]


def gerar_registros(n: int, rng: random.Random) -> list:
    """Gera n registros únicos com matrícula de 9 dígitos usando rng seedado."""
    usadas = set()
    registros = []
    while len(registros) < n:
        mat = rng.randint(100_000_000, 999_999_999)
        if mat in usadas:
            continue
        usadas.add(mat)
        registros.append([
            mat,
            rng.choice(NOMES),
            round(rng.uniform(1_500, 25_000), 2),
            rng.randint(1, 50)
        ])
    rng.shuffle(registros)
    return registros


def salvar_csv(registros: list, caminho: str) -> None:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Mat", "Name", "Sal", "CodSec"])
        writer.writerows(registros)


if __name__ == "__main__":
    t0 = time.perf_counter()
    print(f"Gerando dados — seed={SEED}, volumes={VOLUMES}, rodadas={RODADAS}")

    for n in VOLUMES:
        print(f"\n  N = {n:,}")
        for k in range(RODADAS):
            # Seed derivada de (SEED, N, k): cada rodada produz um dataset
            # distinto e reprodutível sem depender de estado global.
            rng = random.Random(SEED + n + k)
            registros = gerar_registros(n, rng)
            caminho = os.path.join(OUT_DIR, f"data_{n}_{k+1}.csv")
            salvar_csv(registros, caminho)
            mat_exemplo = registros[0][0]
            print(f"    rodada {k+1}: {len(registros):,} registros | "
                  f"mat[0]={mat_exemplo} | salvo em {caminho}")

    print(f"\nConcluido em {time.perf_counter() - t0:.2f}s")
