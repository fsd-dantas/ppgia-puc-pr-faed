"""
Instrumentação para coleta de métricas de desempenho dos algoritmos.

Métricas coletadas por execução:
  tempo_ms          — tempo de execução em milissegundos (perf_counter)
  nos_expandidos    — quantidade de nós expandidos pelo algoritmo
  custo             — custo total do caminho encontrado (None se inexistente)
  comprimento       — número de arestas no caminho (saltos)
  memoria_pico_kb   — pico de memória alocada durante a execução (tracemalloc)

Uso como decorador:
    from src.metrics import medir
    from src.dijkstra import dijkstra

    dijkstra_medido = medir(dijkstra)
    resultado = dijkstra_medido(grafo, origem, destino)
    # resultado é um dict com todas as métricas acima + 'caminho'

Contrato do algoritmo decorado:
    O algoritmo deve retornar exatamente (caminho, custo, expandidos):
      caminho   : List[int]  — lista de IDs de nós
      custo     : float      — custo total acumulado
      expandidos: List[int]  — nós expandidos em ordem
"""
import time
import tracemalloc
from functools import wraps
from typing import Any, Callable, Dict


def medir(func: Callable) -> Callable:
    """
    Decorador que envolve um algoritmo de busca e coleta métricas de desempenho.

    Compatível com qualquer algoritmo que respeite o contrato:
        (grafo, origem, destino) → (caminho, custo, expandidos)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        tracemalloc.start()
        inicio = time.perf_counter()

        caminho, custo, expandidos = func(*args, **kwargs)

        fim = time.perf_counter()
        _, pico_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            'caminho':         caminho,
            'custo':           round(custo, 4) if custo != float('inf') else None,
            'comprimento':     len(caminho) - 1 if len(caminho) > 1 else 0,
            'nos_expandidos':  len(expandidos),
            'tempo_ms':        round((fim - inicio) * 1000, 4),
            'memoria_pico_kb': round(pico_bytes / 1024, 2),
        }

    return wrapper
