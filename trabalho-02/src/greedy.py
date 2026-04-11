"""
Busca Gananciosa (Greedy Best-First Search).

Estratégia: expande sempre o nó com menor valor heurístico h(n),
ignorando completamente o custo acumulado g(n).
Tende a encontrar soluções rapidamente, mas NÃO garante otimalidade.

Complexidade de tempo:  O((V + E) log V)  no pior caso
Complexidade de espaço: O(V)
Otimalidade: não garantida

Aplicação no backhaul: prioriza nós geograficamente mais próximos do destino,
o que é eficiente em topologias hierárquicas sem cruzamentos complexos,
mas pode falhar em grafos com cross-links de baixo custo.

Referência:
  Russell, S.; Norvig, P. — Artificial Intelligence: A Modern Approach,
  4ª ed., Seção 3.5.1. Pearson, 2020.
"""
import heapq
from typing import Dict, List, Optional, Tuple

from src.graph import Grafo
from src.heuristic import heuristica


def busca_gananciosa(
    grafo: Grafo,
    origem: int,
    destino: int,
) -> Tuple[List[int], float, List[int]]:
    """
    Busca pelo nó com menor h(n) a cada passo.

    Retorna:
        caminho    : lista de IDs de nós encontrada (pode ser subótima)
        custo      : custo real acumulado do caminho retornado
        expandidos : IDs dos nós na ordem de expansão
    """
    anterior: Dict[int, Optional[int]] = {origem: None}
    custo_acumulado: Dict[int, float]  = {origem: 0.0}
    expandidos: List[int] = []
    fechados: set = set()

    # Heap: (h(n), contador_desempate, no_id)
    # O contador evita comparação direta entre IDs em caso de empate em h
    _contador = 0
    heap: List[Tuple[float, int, int]] = [
        (heuristica(grafo, origem, destino), _contador, origem)
    ]

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
            if vizinho not in anterior:
                anterior[vizinho] = no
                custo_acumulado[vizinho] = custo_acumulado[no] + peso
                h = heuristica(grafo, vizinho, destino)
                _contador += 1
                heapq.heappush(heap, (h, _contador, vizinho))

    caminho = _reconstruir_caminho(anterior, origem, destino)
    custo   = custo_acumulado.get(destino, float('inf'))
    return caminho, custo, expandidos


def _reconstruir_caminho(
    anterior: Dict[int, Optional[int]],
    origem: int,
    destino: int,
) -> List[int]:
    if destino not in anterior:
        return []
    caminho: List[int] = []
    atual: Optional[int] = destino
    while atual is not None:
        caminho.append(atual)
        atual = anterior.get(atual)
    caminho.reverse()
    return caminho if caminho and caminho[0] == origem else []
