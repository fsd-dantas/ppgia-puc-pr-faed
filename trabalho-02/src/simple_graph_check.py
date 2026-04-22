"""
Grafo didatico de 5 nos para verificar os algoritmos de busca.

Objetivo:
  - validar Dijkstra e A* em um caso pequeno com resultado esperado;
  - mostrar que BFS minimiza saltos, nao custo ponderado;
  - mostrar que busca gananciosa pode escolher um caminho subotimo.

Execute a partir de trabalho-02/:
    python -m src.simple_graph_check
"""
from __future__ import annotations

import heapq
from typing import Callable, Dict, List, Tuple

from src.astar import astar
from src.bfs import bfs
from src.dfs import dfs
from src.dijkstra import dijkstra
from src.graph import Grafo
from src.greedy import busca_gananciosa
from src.heuristic import heuristica


ORIGEM = 1
DESTINO = 5
ESPERADO_OTIMO = [1, 2, 4, 5]
ESPERADO_CUSTO = 3.0


def criar_grafo_5_nos() -> Grafo:
    """
    Cria o grafo:

        A --1-- B --1-- D --1-- E
        |       |       |
        4       2       |
        |       |       |
        C --1---+       |
        \\---------------/
              10

    Coordenadas:
      A=(0,0), B=(1,0), C=(0,1), D=(1,1), E=(2,1)

    Caminho otimo ponderado A->E: A-B-D-E, custo 3.
    Caminho com menos saltos: A-E, custo 10.
    """
    grafo = Grafo()
    grafo.adicionar_no(1, "A", "Teste", 0.0, 0.0)
    grafo.adicionar_no(2, "B", "Teste", 1.0, 0.0)
    grafo.adicionar_no(3, "C", "Teste", 0.0, 1.0)
    grafo.adicionar_no(4, "D", "Teste", 1.0, 1.0)
    grafo.adicionar_no(5, "E", "Teste", 2.0, 1.0)

    # Aresta direta curta em saltos, mas cara em custo.
    grafo.adicionar_aresta(1, 5, 10.0)

    # Rota barata: A -> B -> D -> E.
    grafo.adicionar_aresta(1, 2, 1.0)
    grafo.adicionar_aresta(2, 4, 1.0)
    grafo.adicionar_aresta(4, 5, 1.0)

    # Rota alternativa mais cara: A -> C -> D -> E.
    grafo.adicionar_aresta(1, 3, 4.0)
    grafo.adicionar_aresta(3, 4, 1.0)

    # Aresta extra para deixar a fronteira menos trivial.
    grafo.adicionar_aresta(2, 3, 2.0)
    return grafo


def _nomear(grafo: Grafo, caminho: List[int]) -> str:
    return " -> ".join(grafo.nos[no]["nome"] for no in caminho)


def _imprimir_heuristica(grafo: Grafo) -> None:
    print("Heuristica para destino E")
    print(f"  custo_minimo_por_distancia = {grafo.custo_minimo_por_distancia:.4f}")
    print("  no | distancia ate E | h(no)")
    for no_id in sorted(grafo.nos):
        dist = grafo.distancia_euclidiana(no_id, DESTINO)
        h = heuristica(grafo, no_id, DESTINO)
        print(f"  {grafo.nos[no_id]['nome']:>2s} | {dist:15.4f} | {h:5.4f}")
    print()


def _imprimir_algoritmos(grafo: Grafo) -> None:
    algoritmos: Dict[str, Callable[[Grafo, int, int], Tuple[List[int], float, List[int]]]] = {
        "Dijkstra": dijkstra,
        "A*": astar,
        "Gananciosa": busca_gananciosa,
        "BFS": bfs,
        "DFS": dfs,
    }

    print("Resultados dos algoritmos de A ate E")
    print("  algoritmo   | caminho       | custo | expandidos")
    for nome, algoritmo in algoritmos.items():
        caminho, custo, expandidos = algoritmo(grafo, ORIGEM, DESTINO)
        print(
            f"  {nome:11s} | {_nomear(grafo, caminho):13s} | "
            f"{custo:5.1f} | {_nomear(grafo, expandidos)}"
        )
    print()


def _imprimir_rastro_astar(grafo: Grafo) -> None:
    g: Dict[int, float] = {no: float("inf") for no in grafo.nos}
    g[ORIGEM] = 0.0
    fechados = set()
    contador = 0
    heap: List[Tuple[float, int, int]] = [
        (heuristica(grafo, ORIGEM, DESTINO), contador, ORIGEM)
    ]

    print("Rastro do A*")
    passo = 1
    while heap:
        _, _, no = heapq.heappop(heap)
        if no in fechados:
            continue

        h_no = heuristica(grafo, no, DESTINO)
        print(
            f"  passo {passo}: expande {grafo.nos[no]['nome']} "
            f"(g={g[no]:.4f}, h={h_no:.4f}, f={g[no] + h_no:.4f})"
        )
        fechados.add(no)

        if no == DESTINO:
            print("    destino alcancado")
            break

        for vizinho, peso, _ in grafo.vizinhos(no):
            if vizinho in fechados:
                continue

            novo_g = g[no] + peso
            if novo_g < g[vizinho]:
                g[vizinho] = novo_g
                h_vizinho = heuristica(grafo, vizinho, DESTINO)
                novo_f = novo_g + h_vizinho
                contador += 1
                heapq.heappush(heap, (novo_f, contador, vizinho))
                print(
                    f"    considera {grafo.nos[vizinho]['nome']}: "
                    f"peso={peso:.1f}, g={novo_g:.4f}, "
                    f"h={h_vizinho:.4f}, f={novo_f:.4f}"
                )
        passo += 1
    print()


def _validar(grafo: Grafo) -> None:
    caminho_d, custo_d, _ = dijkstra(grafo, ORIGEM, DESTINO)
    caminho_a, custo_a, _ = astar(grafo, ORIGEM, DESTINO)
    caminho_b, custo_b, _ = bfs(grafo, ORIGEM, DESTINO)
    caminho_g, custo_g, _ = busca_gananciosa(grafo, ORIGEM, DESTINO)

    assert caminho_d == ESPERADO_OTIMO
    assert custo_d == ESPERADO_CUSTO
    assert caminho_a == ESPERADO_OTIMO
    assert custo_a == ESPERADO_CUSTO

    # BFS esta correto para seu criterio: menor numero de saltos.
    assert caminho_b == [1, 5]
    assert custo_b == 10.0

    # Gananciosa escolhe o destino imediato porque h(E)=0, mas paga mais caro.
    assert caminho_g == [1, 5]
    assert custo_g == 10.0

    print("Validacao: OK")
    print("  Dijkstra e A* encontraram o caminho otimo ponderado.")
    print("  BFS encontrou o menor caminho em saltos, nao o menor custo.")
    print("  Gananciosa demonstrou comportamento subotimo esperado.")


def main() -> None:
    grafo = criar_grafo_5_nos()
    print("Grafo didatico: 5 nos, 7 arestas")
    print("Origem: A | Destino: E")
    print("Caminho otimo esperado: A -> B -> D -> E, custo 3")
    print("Aresta direta A -> E: custo 10")
    print()
    _imprimir_heuristica(grafo)
    _imprimir_rastro_astar(grafo)
    _imprimir_algoritmos(grafo)
    _validar(grafo)


if __name__ == "__main__":
    main()
