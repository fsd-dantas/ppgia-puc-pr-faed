"""
Representação do grafo de backhaul sem fio.

Estrutura: lista de adjacência para grafo não-direcionado ponderado.
Cada nó é um equipamento de rádio (AP, SAF ou Remote).
Cada aresta é um enlace sem fio descrito por custo composto e atributos de KPI.
"""
import math
from typing import Any, Dict, List, Optional, Tuple


class Grafo:
    """
    Grafo não-direcionado ponderado para modelagem da rede de backhaul.

    Atributos dos nós: id, nome, tipo, x, y, potencia_tx_dbm
    Atributos das arestas: peso (custo composto), distancia_km, rssi_dbm,
                           snr_db, latencia_ms, throughput_kbps, perda_pacotes_pct
    """

    def __init__(self) -> None:
        # id → dict de atributos do nó
        self.nos: Dict[int, Dict[str, Any]] = {}
        # id → lista de (vizinho_id, peso, dict_atributos)
        self._adj: Dict[int, List[Tuple[int, float, Dict[str, Any]]]] = {}
        # cache do fator de escala para a heurística
        self._custo_min_por_dist: Optional[float] = None

    # ──────────────────────────────────────────────────────────────────────────
    # Construção
    # ──────────────────────────────────────────────────────────────────────────

    def adicionar_no(self, id: int, nome: str, tipo: str,
                     x: float, y: float, **kwargs: Any) -> None:
        """Registra um nó com seus atributos."""
        self.nos[id] = {'id': id, 'nome': nome, 'tipo': tipo,
                        'x': x, 'y': y, **kwargs}
        self._adj.setdefault(id, [])

    def adicionar_aresta(self, src: int, dst: int,
                         peso: float, **atributos: Any) -> None:
        """
        Adiciona aresta bidirecional entre src e dst com o dado peso.
        Invalida o cache do custo mínimo por distância.
        """
        self._adj[src].append((dst, peso, atributos))
        self._adj[dst].append((src, peso, atributos))
        self._custo_min_por_dist = None  # invalida cache

    # ──────────────────────────────────────────────────────────────────────────
    # Consulta
    # ──────────────────────────────────────────────────────────────────────────

    def vizinhos(self, no_id: int) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Retorna [(vizinho_id, peso, atributos), ...] para o nó dado."""
        return self._adj.get(no_id, [])

    def peso_aresta(self, src: int, dst: int) -> float:
        """Retorna o peso da aresta (src, dst). Levanta KeyError se não existe."""
        for viz, peso, _ in self._adj.get(src, []):
            if viz == dst:
                return peso
        raise KeyError(f"Aresta ({src}, {dst}) não encontrada no grafo")

    def distancia_euclidiana(self, no_a: int, no_b: int) -> float:
        """Distância euclidiana entre dois nós pelas coordenadas abstratas (x, y)."""
        a = self.nos[no_a]
        b = self.nos[no_b]
        return math.sqrt((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2)

    # ──────────────────────────────────────────────────────────────────────────
    # Propriedades derivadas
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def custo_minimo_por_distancia(self) -> float:
        """
        Fator de escala usado pela heurística euclidiana.

        Define o custo mínimo observado por unidade de distância euclidiana
        entre todos os pares de nós adjacentes. Garante que h(n) seja
        admissível: h(n) ≤ custo_real(n, destino) para todo n.
        """
        if self._custo_min_por_dist is not None:
            return self._custo_min_por_dist

        minimo = float('inf')
        for src_id, vizinhos in self._adj.items():
            for dst_id, peso, _ in vizinhos:
                dist = self.distancia_euclidiana(src_id, dst_id)
                if dist > 0:
                    minimo = min(minimo, peso / dist)

        self._custo_min_por_dist = minimo if minimo < float('inf') else 0.0
        return self._custo_min_por_dist

    # ──────────────────────────────────────────────────────────────────────────
    # Utilitários
    # ──────────────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self.nos)

    def __repr__(self) -> str:
        n_arestas = sum(len(v) for v in self._adj.values()) // 2
        return f"Grafo(nós={len(self.nos)}, arestas={n_arestas})"
