"""
Heurística geográfica euclidiana para A* e Busca Gananciosa.

Fundamento teórico:
  A distância euclidiana entre dois pontos no plano 2D é sempre menor ou
  igual ao comprimento do caminho real em um grafo com coordenadas coerentes,
  garantindo a propriedade de admissibilidade. O fator de escala
  (custo_minimo_por_distancia) preserva a monotonicidade (consistência).

Admissibilidade:
  h(n) ≤ h*(n)  para todo n
  onde h*(n) é o custo real ótimo de n até o destino.

Consistência (monotonicidade):
  h(n) ≤ w(n, n') + h(n')  para toda aresta (n → n')
  Consequência: A* com heurística consistente não re-expande nós.

Referências:
  Russell, S.; Norvig, P. — Artificial Intelligence: A Modern Approach,
  4ª ed., Cap. 3 (Informed Search). Pearson, 2020.
"""
from src.graph import Grafo


def heuristica(grafo: Grafo, no_id: int, destino_id: int) -> float:
    """
    Estima o custo mínimo entre no_id e destino_id.

    h(n) = dist_euclidiana(n, destino) × custo_mínimo_por_unidade_de_distância

    O fator de escala é calculado a partir dos dados reais do grafo
    (ver Grafo.custo_minimo_por_distancia), tornando a heurística
    automaticamente ajustada à escala dos pesos dos enlaces.
    """
    dist = grafo.distancia_euclidiana(no_id, destino_id)
    return dist * grafo.custo_minimo_por_distancia
