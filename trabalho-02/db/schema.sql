-- =============================================================================
-- Schema SQLite — Simulação de Rede de Backhaul Sem Fio
-- Disciplina: FAED / PPGIA / PUC-PR
-- =============================================================================
--
-- Conformidade LGPD:
--   Todos os dados são inteiramente sintéticos. Nenhum identificador real
--   da infraestrutura COPEL está presente. Parâmetros derivados das
--   especificações públicas do GE MDS Orbit MCR (900 MHz) e do modelo
--   Friis com sombreamento log-normal (ver seed.py).
--
-- Uso:
--   sqlite3 db/backhaul_sim.db < db/schema.sql
-- =============================================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nos (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nome             TEXT    UNIQUE NOT NULL,
    tipo             TEXT    NOT NULL CHECK (tipo IN ('AP', 'SAF', 'Remote')),
    x                REAL    NOT NULL,
    y                REAL    NOT NULL,
    potencia_tx_dbm  REAL    NOT NULL DEFAULT 27.0
);

CREATE TABLE IF NOT EXISTS enlaces (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id              INTEGER NOT NULL REFERENCES nos(id),
    dst_id              INTEGER NOT NULL REFERENCES nos(id),
    distancia_km        REAL    NOT NULL,
    rssi_dbm            REAL    NOT NULL,
    snr_db              REAL    NOT NULL,
    latencia_ms         REAL    NOT NULL,
    throughput_kbps     REAL    NOT NULL,
    perda_pacotes_pct   REAL    NOT NULL,
    peso                REAL    NOT NULL,
    CONSTRAINT ck_distancia  CHECK (distancia_km > 0),
    CONSTRAINT ck_perda      CHECK (perda_pacotes_pct BETWEEN 0 AND 100),
    CONSTRAINT ck_sem_laco   CHECK (src_id <> dst_id),
    CONSTRAINT ck_peso       CHECK (peso > 0)
);

CREATE INDEX IF NOT EXISTS idx_enlaces_src ON enlaces(src_id);
CREATE INDEX IF NOT EXISTS idx_enlaces_dst ON enlaces(dst_id);

CREATE TABLE IF NOT EXISTS casos_teste (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id   INTEGER NOT NULL REFERENCES nos(id),
    dst_id   INTEGER NOT NULL REFERENCES nos(id),
    rotulo   TEXT    NOT NULL,
    CONSTRAINT ck_caso_distinto CHECK (src_id <> dst_id)
);
