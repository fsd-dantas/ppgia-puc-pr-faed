"""
Carregamento do grafo de backhaul a partir do banco SQLite.

Conformidade LGPD:
  Os dados são inteiramente sintéticos — ver db/seed.py.

Caminho padrão do banco: db/backhaul_sim.db (relativo à raiz do projeto).
Sobrescreva com a variável de ambiente BACKHAUL_DB_PATH.
"""
import os
import sqlite3
from typing import List, Tuple

from src.graph import Grafo

_DB_PADRAO = os.getenv(
    'BACKHAUL_DB_PATH',
    os.path.join(os.path.dirname(__file__), '..', 'db', 'backhaul_sim.db'),
)


def carregar_grafo(db_path: str = _DB_PADRAO) -> Grafo:
    """Lê nós e enlaces do banco e retorna um Grafo pronto para uso."""
    grafo = Grafo()
    conn  = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("SELECT id, nome, tipo, x, y, potencia_tx_dbm FROM nos ORDER BY id")
    for row in cur.fetchall():
        grafo.adicionar_no(
            row['id'], nome=row['nome'], tipo=row['tipo'],
            x=row['x'], y=row['y'], potencia_tx_dbm=row['potencia_tx_dbm'],
        )

    cur.execute(
        "SELECT src_id, dst_id, distancia_km, rssi_dbm, snr_db, "
        "       latencia_ms, throughput_kbps, perda_pacotes_pct, peso "
        "FROM enlaces ORDER BY id"
    )
    for row in cur.fetchall():
        grafo.adicionar_aresta(
            row['src_id'], row['dst_id'], row['peso'],
            distancia_km=row['distancia_km'],
            rssi_dbm=row['rssi_dbm'],
            snr_db=row['snr_db'],
            latencia_ms=row['latencia_ms'],
            throughput_kbps=row['throughput_kbps'],
            perda_pacotes_pct=row['perda_pacotes_pct'],
        )

    conn.close()
    return grafo


def carregar_casos_teste(db_path: str = _DB_PADRAO) -> List[Tuple[int, int, str]]:
    """Retorna [(src_id, dst_id, rótulo), ...] dos casos de teste."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT src_id, dst_id, rotulo FROM casos_teste ORDER BY id"
    ).fetchall()
    conn.close()
    return rows
