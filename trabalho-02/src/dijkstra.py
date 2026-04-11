"""
Algoritmo de Dijkstra — caminho mínimo por custo acumulado.

Estratégia: expande sempre o nó com menor custo g(n) acumulado desde a origem.
Garante solução ótima em grafos com pesos não-negativos.

Complexidade de tempo:  O((V + E) log V)  com heap binário
Complexidade de espaço: O(V)
Otimalidade: garantida (pesos ≥ 0)

Referência:
  Dijkstra, E.W. — A Note on Two Problems in Connexion with Graphs.
  Numerische Mathematik, 1(1):269–271, 1959.
"""
import heapq
from typing import Dict, List, Optional, Tuple

from src.graph import Grafo


def dijkstra(
    grafo: Grafo,
    origem: int,
    destino: int,
) -> Tuple[List[int], float, List[int]]:
    """
    Encontra o caminho de custo mínimo entre origem e destino.

    Retorna:
        caminho    : lista de IDs de nós do caminho encontrado (vazia se inexistente)
        custo      : custo total acumulado (inf se inexistente)
        expandidos : IDs dos nós na ordem em que foram expandidos (fechados)
    """
    dist: Dict[int, float] = {no: float('inf') for no in grafo.nos}
    dist[origem] = 0.0
    anterior: Dict[int, Optional[int]] = {no: None for no in grafo.nos}
    expandidos: List[int] = []
    fechados: set = set()

    # Heap: (custo_acumulado, id_no)
    heap: List[Tuple[float, int]] = [(0.0, origem)]

    while heap:
        custo_atual, no = heapq.heappop(heap)

        if no in fechados:
            continue
        fechados.add(no)
        expandidos.append(no)

        if no == destino:
            break

        for vizinho, peso, _ in grafo.vizinhos(no):
            if vizinho in fechados:
                continue
            novo_custo = custo_atual + peso
            if novo_custo < dist[vizinho]:
                dist[vizinho] = novo_custo
                anterior[vizinho] = no
                heapq.heappush(heap, (novo_custo, vizinho))

    return _reconstruir_caminho(anterior, origem, destino), dist[destino], expandidos


def _reconstruir_caminho(
    anterior: Dict[int, Optional[int]],
    origem: int,
    destino: int,
) -> List[int]:
    caminho: List[int] = []
    atual: Optional[int] = destino
    while atual is not None:
        caminho.append(atual)
        atual = anterior.get(atual)
    caminho.reverse()
    return caminho if caminho and caminho[0] == origem else []
