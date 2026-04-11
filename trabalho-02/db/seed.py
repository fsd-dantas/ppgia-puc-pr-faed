"""
Geração do banco de dados sintético para simulação de backhaul sem fio.

Banco: SQLite (db/backhaul_sim.db) — arquivo único, sem servidor.
Modelo: Friis (espaço livre) + sombreamento log-normal.
Parâmetros: especificações públicas do GE MDS Orbit MCR 900 MHz.

Conformidade LGPD:
  Nenhum dado real da infraestrutura COPEL está presente.
  Fontes: GE MDS MCR Datasheet · ITU-R P.525 · Rappaport (2002).

Uso:
    python -m db.seed
    python -m db.seed --db db/backhaul_sim.db --seed 42
"""
import argparse
import math
import os
import random
import sqlite3

# ──────────────────────────────────────────────────────────────────────────────
# Parâmetros físicos — GE MDS Orbit MCR 900 MHz
# ──────────────────────────────────────────────────────────────────────────────
FREQUENCIA_HZ    = 928e6    # frequência central (Hz)
LARGURA_BANDA_HZ = 200e3    # modo narrow-band SCADA (Hz)
PISO_RUIDO_DBM   = -100.0   # piso de ruído para 200 kHz @ 25 °C (dBm)
SIGMA_SOMBRA_DB  = 7.0      # desvio padrão do sombreamento log-normal
EFICIENCIA_SPEC  = 0.55     # eficiência espectral prática (~55% de Shannon)
LATENCIA_BASE_MS = 5.0      # latência base de processamento + fila (ms)

# Pesos do custo composto (somam 1.0)
ALPHA = 0.4   # latência
BETA  = 0.4   # inverso do throughput normalizado
GAMMA = 0.2   # taxa de perda de pacotes

# Throughput máximo de referência (SNR de pico = 25 dB)
_TP_MAX_KBPS = (LARGURA_BANDA_HZ * math.log2(1 + 10 ** (25 / 10)) * EFICIENCIA_SPEC) / 1000

# ──────────────────────────────────────────────────────────────────────────────
# Topologia fictícia — 25 nós, 3 camadas
# (id, nome, tipo, x_km, y_km, potencia_tx_dbm)
# ──────────────────────────────────────────────────────────────────────────────
NOS = [
    ( 1, 'AP-01',   'AP',      0.0,  50.0, 30.0),
    ( 2, 'AP-02',   'AP',     50.0,  80.0, 30.0),
    ( 3, 'AP-03',   'AP',     80.0,  20.0, 30.0),
    ( 4, 'SAF-01',  'SAF',   -20.0,  30.0, 27.0),
    ( 5, 'SAF-02',  'SAF',    10.0,  20.0, 27.0),
    ( 6, 'SAF-03',  'SAF',    25.0,  65.0, 27.0),
    ( 7, 'SAF-04',  'SAF',    40.0,  90.0, 27.0),
    ( 8, 'SAF-05',  'SAF',    65.0,  65.0, 27.0),
    ( 9, 'SAF-06',  'SAF',    70.0,  40.0, 27.0),
    (10, 'SAF-07',  'SAF',    90.0,  10.0, 27.0),
    (11, 'REM-01',  'Remote', -35.0,  40.0, 24.0),
    (12, 'REM-02',  'Remote', -30.0,  20.0, 24.0),
    (13, 'REM-03',  'Remote', -10.0,  10.0, 24.0),
    (14, 'REM-04',  'Remote',   5.0,   5.0, 24.0),
    (15, 'REM-05',  'Remote',  15.0,  35.0, 24.0),
    (16, 'REM-06',  'Remote',  30.0,  48.0, 24.0),
    (17, 'REM-07',  'Remote',  35.0,  75.0, 24.0),
    (18, 'REM-08',  'Remote',  50.0,  72.0, 24.0),
    (19, 'REM-09',  'Remote',  60.0,  88.0, 24.0),
    (20, 'REM-10',  'Remote',  75.0,  60.0, 24.0),
    (21, 'REM-11',  'Remote',  85.0,  50.0, 24.0),
    (22, 'REM-12',  'Remote',  92.0,  35.0, 24.0),
    (23, 'REM-13',  'Remote',  95.0,  20.0, 24.0),
    (24, 'REM-14',  'Remote', 100.0,   5.0, 24.0),
    (25, 'REM-15',  'Remote',  80.0,   0.0, 24.0),
]

ARESTAS = [
    (1, 2), (2, 3),                          # backbone AP-AP
    (1, 4), (1, 5), (1, 6),                  # AP-01 → SAFs
    (2, 6), (2, 7), (2, 8),                  # AP-02 → SAFs
    (3, 9), (3, 10),                         # AP-03 → SAFs
    (6, 8), (8, 9), (5, 15),                 # cross-links SAF
    (4, 11), (4, 12),                        # SAF-01 → Remotes
    (5, 12), (5, 13), (5, 14),               # SAF-02 → Remotes
    (6, 15), (6, 16),                        # SAF-03 → Remotes
    (7, 17), (7, 18),                        # SAF-04 → Remotes
    (8, 18), (8, 19), (8, 20),               # SAF-05 → Remotes
    (9, 20), (9, 21), (9, 22),               # SAF-06 → Remotes
    (10, 22), (10, 23), (10, 24), (10, 25),  # SAF-07 → Remotes
    (19, 20), (21, 22),                      # cross-links Remote
]

CASOS_TESTE = [
    (11,  1, 'remoto-para-AP-raiz'),
    (24,  2, 'extremo-leste-para-AP-norte'),
    (11, 25, 'extremo-oeste-para-extremo-sul'),
    (17, 22, 'cross-branch-SAF4-para-SAF7'),
    (12, 19, 'remoto-SW-para-remoto-NE'),
]

DB_PADRAO = os.path.join(os.path.dirname(__file__), 'backhaul_sim.db')


# ──────────────────────────────────────────────────────────────────────────────
# Modelo de propagação
# ──────────────────────────────────────────────────────────────────────────────

def friis_perda_db(distancia_km: float) -> float:
    """Perda no espaço livre — Friis / ITU-R P.525 (dB)."""
    if distancia_km <= 0:
        return 0.0
    d_m = distancia_km * 1000.0
    return (
        20.0 * math.log10(d_m)
        + 20.0 * math.log10(FREQUENCIA_HZ)
        + 20.0 * math.log10(4.0 * math.pi / 3e8)
    )


def gerar_kpis(potencia_tx_dbm: float, distancia_km: float, rng: random.Random) -> dict:
    """KPIs sintéticos via Friis + sombreamento log-normal."""
    pl      = friis_perda_db(distancia_km) + rng.gauss(0.0, SIGMA_SOMBRA_DB)
    rssi    = potencia_tx_dbm - pl
    snr     = rssi - PISO_RUIDO_DBM
    snr_lin = 10.0 ** (max(snr, 0.0) / 10.0)
    tp      = (LARGURA_BANDA_HZ * math.log2(1.0 + snr_lin) * EFICIENCIA_SPEC) / 1000.0
    lat     = LATENCIA_BASE_MS + (distancia_km / 3e5) * 1e6 + rng.uniform(3.0, 15.0)
    perda   = min(max(5.0 - 0.18 * snr + rng.gauss(0.0, 0.3), 0.0), 15.0)
    return {
        'rssi_dbm':          round(rssi,  2),
        'snr_db':            round(snr,   2),
        'latencia_ms':       round(lat,   3),
        'throughput_kbps':   round(tp,    2),
        'perda_pacotes_pct': round(perda, 4),
    }


def calcular_peso(kpis: dict) -> float:
    tp_norm = min(kpis['throughput_kbps'] / _TP_MAX_KBPS, 1.0)
    return round(
        ALPHA * kpis['latencia_ms']
        + BETA  * (1.0 - tp_norm) * 100.0
        + GAMMA * kpis['perda_pacotes_pct'],
        4,
    )


def _dist(nos_dict: dict, a: int, b: int) -> float:
    na, nb = nos_dict[a], nos_dict[b]
    return math.sqrt((na[3] - nb[3]) ** 2 + (na[4] - nb[4]) ** 2)


# ──────────────────────────────────────────────────────────────────────────────
# Carga no banco
# ──────────────────────────────────────────────────────────────────────────────

def semear(db_path: str = DB_PADRAO, seed: int = 42) -> None:
    rng      = random.Random(seed)
    nos_dict = {n[0]: n for n in NOS}

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Recria as tabelas a partir do schema
    schema = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema, encoding='utf-8') as f:
        conn.executescript(f.read())

    # Limpa dados anteriores (idempotente)
    conn.execute("DELETE FROM casos_teste")
    conn.execute("DELETE FROM enlaces")
    conn.execute("DELETE FROM nos")

    # Nós
    conn.executemany(
        "INSERT INTO nos (id, nome, tipo, x, y, potencia_tx_dbm) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        NOS,
    )

    # Arestas com KPIs sintéticos
    for src_id, dst_id in ARESTAS:
        potencia = min(nos_dict[src_id][5], nos_dict[dst_id][5])
        dist_km  = _dist(nos_dict, src_id, dst_id)
        kpis     = gerar_kpis(potencia, dist_km, rng)
        peso     = calcular_peso(kpis)
        conn.execute(
            "INSERT INTO enlaces "
            "(src_id, dst_id, distancia_km, rssi_dbm, snr_db, "
            " latencia_ms, throughput_kbps, perda_pacotes_pct, peso) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (src_id, dst_id, round(dist_km, 3),
             kpis['rssi_dbm'], kpis['snr_db'], kpis['latencia_ms'],
             kpis['throughput_kbps'], kpis['perda_pacotes_pct'], peso),
        )

    # Casos de teste
    conn.executemany(
        "INSERT INTO casos_teste (src_id, dst_id, rotulo) VALUES (?, ?, ?)",
        CASOS_TESTE,
    )

    conn.commit()
    conn.close()

    tamanho_kb = os.path.getsize(db_path) / 1024
    print(f"Banco gerado: {db_path}  ({tamanho_kb:.1f} KB)")
    print(f"  {len(NOS)} nós  |  {len(ARESTAS)} enlaces  |  {len(CASOS_TESTE)} casos de teste")
    print(f"  TP_MAX ref.: {_TP_MAX_KBPS:.1f} kbps  |  semente RNG: {seed}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Gera o banco SQLite de simulação de backhaul.'
    )
    parser.add_argument('--db',   default=DB_PADRAO, help='Caminho do arquivo .db')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    semear(args.db, args.seed)
