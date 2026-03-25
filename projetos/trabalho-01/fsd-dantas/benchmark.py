"""
benchmark.py
------------
Framework unificado de benchmarking — Trabalho 01 – FAED/PPGIA-PUCPR.

Executa todos os cenários de teste em uma única chamada:
  - Array linear  : inserção, busca linear, busca binária
  - BST           : inserção, busca (sem balanceamento)
  - AVL           : inserção, busca (com balanceamento)
  - Hash Table    : inserção e busca para cada combinação de
                    função hash × tamanho M

Para cada cenário: 5 rodadas independentes → média e desvio padrão.

Saídas:
  resultados/resultados_brutos.csv  — uma linha por (estrutura, N, rodada)
  resultados/resumo.csv             — médias e desvios por cenário
  Console                           — tabela comparativa formatada

Uso:
    python benchmark.py
    python benchmark.py --volumes 10000 100000
    python benchmark.py --rodadas 10
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Garante que os módulos do mesmo diretório são importáveis
sys.path.insert(0, str(Path(__file__).parent))

from data_generator import carregar_csv, gerar_registros, salvar_csv
from linear_array   import (LinearArray,
                             benchmark_insercao  as la_ins,
                             benchmark_busca     as la_bus)
from bst            import (BST, AVL,
                             benchmark_insercao  as arv_ins,
                             benchmark_busca     as arv_bus)
from hash_table     import (HashTable,
                             benchmark_insercao  as ht_ins,
                             benchmark_busca     as ht_bus)

# ---------------------------------------------------------------------------
# Configuração dos cenários
# ---------------------------------------------------------------------------

VOLUMES_DEFAULT    = [10_000, 50_000, 100_000]
RODADAS_DEFAULT    = 5
FRACOES_BUSCA      = [0.5]          # alvo no meio — caso médio

HT_TAMANHOS_M      = [100, 1_000, 5_000]
HT_FUNCOES         = ["divisao", "multiplicacao", "dobramento"]


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def _estat(valores: list[float]) -> tuple[float, float]:
    """Retorna (média, desvio_padrão)."""
    n   = len(valores)
    med = sum(valores) / n
    dp  = (sum((x - med) ** 2 for x in valores) / n) ** 0.5
    return med, dp


def _preparar_dados(n: int, pasta: Path) -> list[dict]:
    """Carrega CSV se existir; senão gera e salva."""
    arq = pasta / f"registros_{n}.csv"
    if arq.exists():
        return carregar_csv(arq)
    print(f"  [aviso] CSV nao encontrado para N={n:,}. Gerando e salvando...")
    registros = gerar_registros(n)
    salvar_csv(registros, arq)
    return registros


# ---------------------------------------------------------------------------
# Coletores por estrutura
# ---------------------------------------------------------------------------

def _coletar_array(registros: list[dict], rodadas: int) -> list[dict]:
    """Coleta métricas do array linear (inserção + busca linear + binária)."""
    linhas = []
    n      = len(registros)

    for rodada in range(1, rodadas + 1):
        # Inserção
        r = la_ins(registros)
        linhas.append({
            "estrutura": "Array", "parametro": "—", "n": n,
            "rodada": rodada, "operacao": "insercao",
            "tempo_s": r["tempo_s"], "iteracoes": r["iteracoes"],
            "mem_pico_mb": r["mem_pico_mb"],
            "mem_rss_mb": r["mem_rss_delta_mb"],
            "extra_chave": "—", "extra_valor": "—",
        })

        # Busca linear (alvo no meio)
        rb = la_bus(registros, metodo="linear", fracoes=FRACOES_BUSCA)[0]
        linhas.append({
            "estrutura": "Array-Linear", "parametro": "—", "n": n,
            "rodada": rodada, "operacao": "busca",
            "tempo_s": rb["tempo_s"], "iteracoes": rb["iteracoes"],
            "mem_pico_mb": rb["mem_pico_mb"],
            "mem_rss_mb": rb["mem_rss_delta_mb"],
            "extra_chave": "—", "extra_valor": "—",
        })

        # Busca binária (alvo no meio)
        rb2 = la_bus(registros, metodo="binaria", fracoes=FRACOES_BUSCA)[0]
        linhas.append({
            "estrutura": "Array-Binaria", "parametro": "—", "n": n,
            "rodada": rodada, "operacao": "busca",
            "tempo_s": rb2["tempo_s"], "iteracoes": rb2["iteracoes"],
            "mem_pico_mb": rb2["mem_pico_mb"],
            "mem_rss_mb": rb2["mem_rss_delta_mb"],
            "extra_chave": "—", "extra_valor": "—",
        })

    return linhas


def _coletar_arvore(registros: list[dict], classe, rodadas: int) -> list[dict]:
    """Coleta métricas de BST ou AVL."""
    linhas = []
    n      = len(registros)
    nome   = classe.__name__

    for rodada in range(1, rodadas + 1):
        ri = arv_ins(registros, classe)
        linhas.append({
            "estrutura": nome, "parametro": "—", "n": n,
            "rodada": rodada, "operacao": "insercao",
            "tempo_s": ri["tempo_s"], "iteracoes": ri["iteracoes"],
            "mem_pico_mb": ri["mem_pico_mb"],
            "mem_rss_mb": ri["mem_rss_delta_mb"],
            "extra_chave": "altura", "extra_valor": ri["altura"],
        })

        rb = arv_bus(registros, classe, fracoes=FRACOES_BUSCA)[0]
        linhas.append({
            "estrutura": nome, "parametro": "—", "n": n,
            "rodada": rodada, "operacao": "busca",
            "tempo_s": rb["tempo_s"], "iteracoes": rb["iteracoes"],
            "mem_pico_mb": rb["mem_pico_mb"],
            "mem_rss_mb": rb["mem_rss_delta_mb"],
            "extra_chave": "—", "extra_valor": "—",
        })

    return linhas


def _coletar_hash(registros: list[dict], m: int, funcao: str,
                  rodadas: int) -> list[dict]:
    """Coleta métricas da tabela hash para uma combinação (M, função)."""
    linhas = []
    n      = len(registros)
    param  = f"M={m},fn={funcao}"

    for rodada in range(1, rodadas + 1):
        ri = ht_ins(registros, m, funcao)
        linhas.append({
            "estrutura": "HashTable", "parametro": param, "n": n,
            "rodada": rodada, "operacao": "insercao",
            "tempo_s": ri["tempo_s"], "iteracoes": ri["total_iteracoes"],
            "mem_pico_mb": ri["mem_pico_mb"],
            "mem_rss_mb": ri["mem_rss_delta_mb"],
            "extra_chave": "load_factor", "extra_valor": ri["load_factor"],
        })

        rb = ht_bus(registros, m, funcao, fracoes=FRACOES_BUSCA)[0]
        linhas.append({
            "estrutura": "HashTable", "parametro": param, "n": n,
            "rodada": rodada, "operacao": "busca",
            "tempo_s": rb["tempo_s"], "iteracoes": rb["iteracoes"],
            "mem_pico_mb": rb["mem_pico_mb"],
            "mem_rss_mb": rb["mem_rss_delta_mb"],
            "extra_chave": "colisoes", "extra_valor": ri["colisoes"],
        })

    return linhas


# ---------------------------------------------------------------------------
# Persistência dos resultados
# ---------------------------------------------------------------------------

CAMPOS_CSV = [
    "estrutura", "parametro", "n", "rodada", "operacao",
    "tempo_s", "iteracoes", "mem_pico_mb", "mem_rss_mb",
    "extra_chave", "extra_valor",
]


def salvar_brutos(linhas: list[dict], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        w.writeheader()
        w.writerows(linhas)


def salvar_resumo(linhas: list[dict], caminho: Path) -> list[dict]:
    """Agrega por (estrutura, parametro, n, operacao) → média e desvio."""
    from collections import defaultdict
    grupos: dict[tuple, list] = defaultdict(list)
    for l in linhas:
        chave = (l["estrutura"], l["parametro"], l["n"], l["operacao"])
        grupos[chave].append(l)

    resumo = []
    for (est, par, n, op), grupo in sorted(grupos.items()):
        tempos  = [g["tempo_s"]     for g in grupo]
        iters   = [g["iteracoes"]   for g in grupo]
        mems    = [g["mem_pico_mb"] for g in grupo]

        tm, td = _estat(tempos)
        im, id_ = _estat(iters)
        mm, md = _estat(mems)

        resumo.append({
            "estrutura":     est, "parametro": par,
            "n":             n,   "operacao":  op,
            "rodadas":       len(grupo),
            "tempo_med_s":   tm,  "tempo_dp_s":    td,
            "iter_media":    im,  "iter_dp":        id_,
            "mem_pico_med":  mm,  "mem_pico_dp":    md,
        })

    caminho.parent.mkdir(parents=True, exist_ok=True)
    campos = ["estrutura", "parametro", "n", "operacao", "rodadas",
              "tempo_med_s", "tempo_dp_s", "iter_media", "iter_dp",
              "mem_pico_med", "mem_pico_dp"]
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(resumo)

    return resumo


# ---------------------------------------------------------------------------
# Impressão da tabela comparativa
# ---------------------------------------------------------------------------

def imprimir_tabela(resumo: list[dict]) -> None:
    """Imprime tabela comparativa por N, separando inserção e busca."""
    ns = sorted({r["n"] for r in resumo})

    for n in ns:
        print(f"\n{'='*78}")
        print(f"  N = {n:,}")
        print(f"{'='*78}")

        for op in ("insercao", "busca"):
            label = "INSERCAO" if op == "insercao" else "BUSCA"
            print(f"\n  [{label}]")
            print(f"  {'Estrutura':<20} {'Parametro':<22} "
                  f"{'Iter. media':>13} {'Tempo med(s)':>14} "
                  f"{'Mem pico(MB)':>13}")
            print(f"  {'-'*84}")

            bloco = [r for r in resumo if r["n"] == n and r["operacao"] == op]
            bloco.sort(key=lambda r: (r["estrutura"], r["parametro"]))

            for r in bloco:
                print(
                    f"  {r['estrutura']:<20} {str(r['parametro']):<22} "
                    f"{r['iter_media']:>13.1f} "
                    f"{r['tempo_med_s']:>14.6f} "
                    f"{r['mem_pico_med']:>13.4f}"
                )


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main(volumes: list[int], rodadas: int) -> None:
    pasta_dados = Path(__file__).parent / "dados"
    pasta_res   = Path(__file__).parent / "resultados"
    ts          = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 78)
    print("  Benchmark unificado — Trabalho 01 FAED/PPGIA-PUCPR")
    print(f"  Volumes: {volumes}  |  Rodadas: {rodadas}")
    print("=" * 78)

    todas_linhas: list[dict] = []

    for n in volumes:
        print(f"\n--- Carregando dados N={n:,} ---")
        registros = _preparar_dados(n, pasta_dados)

        cenarios = [
            ("Array linear",   lambda: _coletar_array(registros, rodadas)),
            ("BST",            lambda: _coletar_arvore(registros, BST, rodadas)),
            ("AVL",            lambda: _coletar_arvore(registros, AVL, rodadas)),
        ] + [
            (f"Hash M={m} fn={fn}",
             lambda m=m, fn=fn: _coletar_hash(registros, m, fn, rodadas))
            for m in HT_TAMANHOS_M
            for fn in HT_FUNCOES
        ]

        for nome_cenario, coletor in cenarios:
            print(f"\n  >> {nome_cenario} (N={n:,})")
            linhas = coletor()
            todas_linhas.extend(linhas)

    # Salva resultados brutos
    arq_brutos = pasta_res / f"resultados_brutos_{ts}.csv"
    salvar_brutos(todas_linhas, arq_brutos)
    print(f"\n[OK] Resultados brutos: {arq_brutos}")

    # Salva e imprime resumo
    arq_resumo = pasta_res / f"resumo_{ts}.csv"
    resumo     = salvar_resumo(todas_linhas, arq_resumo)
    print(f"[OK] Resumo           : {arq_resumo}")

    imprimir_tabela(resumo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark comparativo de estruturas de dados"
    )
    parser.add_argument(
        "--volumes", nargs="+", type=int, default=VOLUMES_DEFAULT,
        help=f"Volumes N a testar (default: {VOLUMES_DEFAULT})"
    )
    parser.add_argument(
        "--rodadas", type=int, default=RODADAS_DEFAULT,
        help=f"Rodadas independentes por cenario (default: {RODADAS_DEFAULT})"
    )
    args = parser.parse_args()
    main(volumes=args.volumes, rodadas=args.rodadas)
