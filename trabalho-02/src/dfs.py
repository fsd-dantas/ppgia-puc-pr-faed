"""
Busca em Profundidade (DFS — Depth-First Search).

Estratégia: explora o grafo seguindo um caminho o mais fundo possível
antes de retroceder, usando uma pilha LIFO.
Implementação iterativa com pilha explícita (evita limite de recursão).
NÃO garante otimalidade nem caminho com menor número de saltos.

Complexidade de tempo:  O(V + E)
Complexidade de espaço: O(V)
Otimalidade: não garantida

Relevância para o backhaul:
  DFS é apresentado como contraponto algorítmico: explora profundamente
  um ramo antes de considerar alternativas, o que em grafos de backhaul
  pode resultar em caminhos longos e de alto custo. A comparação com
  Dijkstra e A* evidencia o custo da ausência de informação de custo.

Referência:
  Cormen, T.H. et al. — Introduction to Algorithms, 4ª ed.,
  Seção 20.3. MIT Press, 2022.
"""
from typing import Dict, List, Optional, Tuple

from src.graph import Grafo


def dfs(
    grafo: Grafo,
    origem: int,
    destino: int,
) -> Tuple[List[int], float, List[int]]:
    """
    Busca em profundidade do grafo a partir de origem até destino.

    Retorna:
        caminho    : primeiro caminho encontrado (pode ser subótimo)
        custo      : custo real acumulado do caminho retornado
        expandidos : IDs dos nós na ordem de visita (LIFO)
    """
    anterior: Dict[int, Optional[int]] = {origem: None}
    custo_acumulado: Dict[int, float]  = {origem: 0.0}
    expandidos: List[int] = []
    fechados: set = set()

    pilha: List[int] = [origem]

    while pilha:
        no = pilha.pop()

        if no in fechados:
            continue
        fechados.add(no)
        expandidos.append(no)

        if no == destino:
            break

        # Insere vizinhos em ordem reversa para manter comportamento
        # determinístico (primeiro vizinho da lista é explorado primeiro)
        for vizinho, peso, _ in reversed(grafo.vizinhos(no)):
            if vizinho not in fechados:
                if vizinho not in anterior:
                    anterior[vizinho] = no
                    custo_acumulado[vizinho] = custo_acumulado[no] + peso
                pilha.append(vizinho)

    caminho = _reconstruir_caminho(anterior, origem, destino)
    custo   = custo_acumulado.get(destino, float('inf'))
    return caminho, custo, expandidos


def _reconstruir_caminho(
    anterior: Dict[int, Optional[int]],
    origem: int,
    destino: int,
) -> List[int]:
    if destino not in anterior and destino != origem:
        return []
    caminho: List[int] = []
    atual: Optional[int] = destino
    while atual is not None:
        caminho.append(atual)
        atual = anterior.get(atual)
    caminho.reverse()
    return caminho if caminho and caminho[0] == origem else []
