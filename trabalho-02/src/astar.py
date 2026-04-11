"""
Algoritmo A* — busca informada com custo acumulado e heurística.

Estratégia: expande o nó com menor f(n) = g(n) + h(n), onde:
  g(n) = custo acumulado desde a origem até n
  h(n) = estimativa heurística do custo de n até o destino

Com heurística admissível e consistente, garante solução ótima e
não re-expande nós já fechados (propriedade de consistência).

Complexidade de tempo:  O((V + E) log V)  com heurística de qualidade
Complexidade de espaço: O(V)
Otimalidade: garantida (heurística admissível + consistente)

No contexto de backhaul:
  A* combina a robustez de Dijkstra (custo acumulado) com a eficiência
  da busca gananciosa (direcionamento heurístico), sendo o algoritmo
  mais adequado para roteamento em redes com coordenadas geográficas.

Referência:
  Hart, P.E.; Nilsson, N.J.; Raphael, B. — A Formal Basis for the
  Heuristic Determination of Minimum Cost Paths.
  IEEE Trans. Systems Science and Cybernetics, 4(2):100–107, 1968.
"""
import heapq
from typing import Dict, List, Optional, Tuple

from src.graph import Grafo
from src.heuristic import heuristica


def astar(
    grafo: Grafo,
    origem: int,
    destino: int,
) -> Tuple[List[int], float, List[int]]:
    """
    Encontra o caminho ótimo entre origem e destino usando A*.

    Retorna:
        caminho    : lista de IDs de nós do caminho ótimo
        custo      : custo total g(destino)
        expandidos : IDs dos nós na ordem de expansão
    """
    g: Dict[int, float] = {no: float('inf') for no in grafo.nos}
    g[origem] = 0.0
    anterior: Dict[int, Optional[int]] = {no: None for no in grafo.nos}
    expandidos: List[int] = []
    fechados: set = set()

    # Heap: (f(n), contador_desempate, no_id)
    _contador = 0
    h0 = heuristica(grafo, origem, destino)
    heap: List[Tuple[float, int, int]] = [(g[origem] + h0, _contador, origem)]

    while heap:
        _, _, no = heapq.heappop(heap)

        if no in fechados:
            continue
        fechados.add(no)
        expandidos.append(no)

        if no == destino:
            break

        for vizinho, peso, _ in grafo.vizinhos(no):
            if vizinho in fechados:
                continue
            novo_g = g[no] + peso
            if novo_g < g[vizinho]:
                g[vizinho] = novo_g
                anterior[vizinho] = no
                h = heuristica(grafo, vizinho, destino)
                _contador += 1
                heapq.heappush(heap, (novo_g + h, _contador, vizinho))

    return _reconstruir_caminho(anterior, origem, destino), g[destino], expandidos


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
