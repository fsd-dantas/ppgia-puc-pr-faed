"""
Busca em Largura (BFS — Breadth-First Search).

Estratégia: explora o grafo nível a nível usando uma fila FIFO.
Em grafos NÃO-ponderados, garante o caminho com menor número de saltos.
Em grafos ponderados (como este), NÃO garante custo mínimo — apenas
minimiza a quantidade de arestas percorridas.

Complexidade de tempo:  O(V + E)
Complexidade de espaço: O(V)
Otimalidade: apenas para grafos não-ponderados (mínimo de saltos)

Relevância para o backhaul:
  BFS é incluído para demonstrar empiricamente que minimizar saltos
  não equivale a minimizar latência/custo em redes sem fio, onde
  enlaces de longa distância têm custo muito superior a saltos extras.

Referência:
  Cormen, T.H. et al. — Introduction to Algorithms, 4ª ed.,
  Seção 20.2. MIT Press, 2022.
"""
from collections import deque
from typing import Dict, List, Optional, Tuple

from src.graph import Grafo


def bfs(
    grafo: Grafo,
    origem: int,
    destino: int,
) -> Tuple[List[int], float, List[int]]:
    """
    Busca em largura do grafo a partir de origem até destino.

    Retorna:
        caminho    : caminho com menor número de saltos encontrado
        custo      : custo real acumulado (pesos dos enlaces do caminho)
        expandidos : IDs dos nós na ordem de visita (FIFO)
    """
    anterior: Dict[int, Optional[int]] = {origem: None}
    custo_acumulado: Dict[int, float]  = {origem: 0.0}
    expandidos: List[int] = []

    fila: deque = deque([origem])

    while fila:
        no = fila.popleft()
        expandidos.append(no)

        if no == destino:
            break

        for vizinho, peso, _ in grafo.vizinhos(no):
            if vizinho not in anterior:
                anterior[vizinho] = no
                custo_acumulado[vizinho] = custo_acumulado[no] + peso
                fila.append(vizinho)

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
