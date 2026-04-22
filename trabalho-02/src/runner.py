"""
Executor de experimentos — orquestra pares de teste e coleta estatísticas.

Para cada par (origem, destino) e cada algoritmo:
  1. Executa N_RODADAS repetições de medição
  2. Coleta métricas por rodada (tempo, nós, custo, saltos, memória)
  3. Calcula média e desvio padrão
  4. Exporta resultados brutos e sumário em CSV

Saída:
  results/metrics/rodadas_brutas.csv  — uma linha por (algoritmo × par × rodada)
  results/metrics/sumario.csv         — média ± desvio padrão por (algoritmo × par)

Conformidade com a rubrica:
  - ≥ 5 pares origem-destino distintos       (PARES_TESTE)
  - ≥ 5 repetições de medição por par        (N_RODADAS)
  - Médias e desvios padrão para cada métrica
  - Visualização Pyvis gerada para cada algoritmo no primeiro par

Uso:
    python -m src.runner
"""
import csv
import os
import statistics
from typing import Callable, Dict, List, Tuple

from src.astar import astar
from src.bfs import bfs
from src.dfs import dfs
from src.dijkstra import dijkstra
from src.graph import Grafo
from src.graph_data import carregar_grafo
from src.greedy import busca_gananciosa
from src.metrics import medir
from src.visualization import renderizar

# ──────────────────────────────────────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────────────────────────────────────

N_RODADAS = 5
DIR_METRICAS = 'results/metrics'
DIR_GRAFOS   = 'results/graphs'

# Pares de teste: (src_id, dst_id, descrição)
# Cobrem cenários distintos do backhaul:
#   1. Folha → raiz (caminho hierárquico típico)
#   2. Extremo leste → AP norte (cross-zone de longa distância)
#   3. Extremo oeste → extremo sul (diagonal máxima)
#   4. Cross-branch entre SAFs (rota com cross-links)
#   5. Remoto SW → Remoto NE (diagonal entre folhas)
PARES_TESTE: List[Tuple[int, int, str]] = [
    (11,  1, 'remoto-para-AP-raiz'),
    (24,  2, 'extremo-leste-para-AP-norte'),
    (11, 25, 'extremo-oeste-para-extremo-sul'),
    (17, 22, 'cross-branch-SAF4-para-SAF7'),
    (12, 19, 'remoto-SW-para-remoto-NE'),
]

ALGORITMOS: Dict[str, Callable] = {
    'Dijkstra':   medir(dijkstra),
    'Gananciosa': medir(busca_gananciosa),
    'A*':         medir(astar),
    'BFS':        medir(bfs),
    'DFS':        medir(dfs),
}

CAMPOS_METRICAS = [
    'tempo_ms', 'nos_expandidos', 'custo', 'comprimento', 'memoria_pico_kb'
]

# ──────────────────────────────────────────────────────────────────────────────

def executar() -> None:
    """Ponto de entrada principal."""
    grafo = carregar_grafo()
    os.makedirs(DIR_METRICAS, exist_ok=True)
    os.makedirs(DIR_GRAFOS,   exist_ok=True)

    resultados_brutos: List[Dict] = []
    sumario:           List[Dict] = []

    for src, dst, descricao in PARES_TESTE:
        nome_src = grafo.nos[src]['nome']
        nome_dst = grafo.nos[dst]['nome']
        print(f"\n{'=' * 65}")
        print(f"  Par: {nome_src} -> {nome_dst}  [{descricao}]")
        print(f"{'-' * 65}")

        for nome_alg, func_alg in ALGORITMOS.items():
            rodadas: List[Dict] = []

            for rodada in range(1, N_RODADAS + 1):
                resultado = func_alg(grafo, src, dst)
                resultado.update({
                    'par':       descricao,
                    'algoritmo': nome_alg,
                    'origem':    nome_src,
                    'destino':   nome_dst,
                    'rodada':    rodada,
                })
                rodadas.append(resultado)
                resultados_brutos.append(resultado)

            # Estatísticas descritivas
            stats: Dict = {
                'par': descricao, 'algoritmo': nome_alg,
                'origem': nome_src, 'destino': nome_dst,
            }
            for campo in CAMPOS_METRICAS:
                valores = [r[campo] for r in rodadas if r[campo] is not None]
                if valores:
                    stats[f'{campo}_media'] = round(statistics.mean(valores), 4)
                    stats[f'{campo}_dp']    = round(
                        statistics.stdev(valores) if len(valores) > 1 else 0.0, 4
                    )
                else:
                    stats[f'{campo}_media'] = None
                    stats[f'{campo}_dp']    = None
            sumario.append(stats)

            print(
                f"  {nome_alg:12s} | "
                f"tempo={stats['tempo_ms_media']:.3f}±{stats['tempo_ms_dp']:.3f} ms | "
                f"nós={stats['nos_expandidos_media']:.1f} | "
                f"custo={stats['custo_media']}"
            )

            # Gera visualização Pyvis para o primeiro par apenas
            if src == PARES_TESTE[0][0] and dst == PARES_TESTE[0][1]:
                caminho = rodadas[0]['caminho']
                renderizar(grafo, nome_alg, caminho, saida=DIR_GRAFOS)

    _exportar_csv(
        resultados_brutos,
        os.path.join(DIR_METRICAS, 'rodadas_brutas.csv'),
    )
    _exportar_csv(
        sumario,
        os.path.join(DIR_METRICAS, 'sumario.csv'),
    )

    print(f"\n{'=' * 65}")
    print(f"  Resultados exportados em {DIR_METRICAS}/")
    print(f"  Grafos Pyvis em {DIR_GRAFOS}/")


def _exportar_csv(registros: List[Dict], caminho_arquivo: str) -> None:
    if not registros:
        return
    campos = list(registros[0].keys())
    with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)


if __name__ == '__main__':
    executar()
