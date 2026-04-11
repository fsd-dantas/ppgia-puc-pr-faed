# Trabalho 02 — Análise de Algoritmos de Busca em Grafos

**Disciplina:** Fundamentos de Algoritmos e Estrutura de Dados (FAED)
**Programa:** PPGIA — PUC-PR
**Prof.:** André Gustavo Hochuli

---

## Domínio

Rede de backhaul sem fio para smart grid, modelada a partir das características
do rádio **GE MDS Orbit MCR 900 MHz**. A topologia é **inteiramente sintética**
e não contém nenhum dado real da infraestrutura da COPEL (conformidade LGPD).

Os parâmetros de enlace (RSSI, SNR, latência, throughput, perda de pacotes)
foram gerados pelo modelo Friis + sombreamento log-normal com semente RNG fixa
(`seed=42`), garantindo **reprodutibilidade total**.

---

## Topologia

| Tipo     | Qtd | Descrição                                          |
|----------|-----|----------------------------------------------------|
| AP       |   3 | Access Points — nós raiz com backbone cabeado      |
| SAF      |   7 | Store-and-Forward — repetidores intermediários     |
| Remote   |  15 | Concentradores de medidores inteligentes / RTUs    |
| **Total**| **25** | **32 enlaces não-direcionados**               |

### Peso do enlace (custo composto)

```
peso = 0.4 × latência_ms  +  0.4 × (1 − tp_norm) × 100  +  0.2 × perda_pct
```

### Heurística A\* / Gananciosa (admissível e consistente)

```
h(n) = dist_euclidiana(n, destino) × custo_mínimo_por_km
```

---

## Algoritmos Implementados

| Arquivo             | Algoritmo         | Otimalidade |
|---------------------|-------------------|-------------|
| `src/dijkstra.py`   | Dijkstra          | Sim         |
| `src/astar.py`      | A\*               | Sim         |
| `src/greedy.py`     | Busca Gananciosa  | Não         |
| `src/bfs.py`        | BFS               | Saltos mín. |
| `src/dfs.py`        | DFS               | Não         |

---

## Pré-requisitos

- Python 3.10+
- PostgreSQL 14+
- Dependências Python: `pip install -r requirements.txt`

---

## Configuração

### 1. Banco de dados

```bash
# Criar banco e usuário
psql -U postgres -c "CREATE USER backhaul WITH PASSWORD 'backhaul';"
psql -U postgres -c "CREATE DATABASE backhaul_sim OWNER backhaul;"

# Aplicar schema
psql -U backhaul -d backhaul_sim -f db/schema.sql

# Popular dados sintéticos
python -m db.seed
```

Variável de ambiente opcional (substitui o DSN padrão):
```bash
export BACKHAUL_DB_DSN="postgresql://backhaul:backhaul@localhost:5432/backhaul_sim"
```

### 2. Executar experimentos

```bash
python -m src.runner
```

Saída gerada:

```
results/
├── metrics/
│   ├── rodadas_brutas.csv   # uma linha por algoritmo × par × rodada
│   └── sumario.csv          # média ± desvio padrão por algoritmo × par
└── graphs/
    ├── dijkstra_caminho.html
    ├── astar_caminho.html
    ├── gananciosa_caminho.html
    ├── bfs_caminho.html
    └── dfs_caminho.html
```

---

## Estrutura do Projeto

```
trabalho-02/
├── db/
│   ├── schema.sql          # DDL PostgreSQL
│   └── seed.py             # Gerador de dados sintéticos
├── src/
│   ├── graph.py            # Classe Grafo (lista de adjacência)
│   ├── graph_data.py       # Carregamento do grafo a partir do banco
│   ├── heuristic.py        # Heurística euclidiana admissível
│   ├── dijkstra.py
│   ├── greedy.py
│   ├── astar.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── metrics.py          # Decorador de instrumentação
│   ├── runner.py           # Executor de experimentos e exportação CSV
│   └── visualization.py   # Renderização Pyvis → HTML
├── results/
│   ├── graphs/
│   └── metrics/
├── report/
│   ├── main.tex            # Artigo IEEE (duas colunas, máx. 6 páginas)
│   ├── references.bib
│   └── figures/
└── requirements.txt
```

---

## Conformidade LGPD

Todos os dados são sintéticos. Os parâmetros de enlace são derivados
exclusivamente de fontes públicas:

- GE MDS Orbit MCR Datasheet (900 MHz, narrow-band SCADA)
- ITU-R P.525 — Free-Space Path Loss
- Rappaport, T.S. — *Wireless Communications*, 2ª ed. Prentice Hall, 2002.
