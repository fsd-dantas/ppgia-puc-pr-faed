# Trabalho 01 — Guia de Execução

## Requisitos

- Python 3.10+
- Dependências: `pip install psutil matplotlib`

---

## Ordem de execução

Todos os comandos devem ser executados a partir deste diretório (`src/`).

### 1. Geração dos dados

```bash
python dataGen.py
```

Gera 15 arquivos CSV em `data/` — 5 rodadas independentes para cada volume N ∈ {10.000, 50.000, 100.000}.
Cada arquivo contém registros com: Matrícula (9 dígitos), Nome, Salário, Código do Setor.
A geração é determinística (seed fixo); executar novamente produz os mesmos arquivos.

**Saída:** `data/data_{N}_{rodada}.csv`

---

### 2. Benchmark — Array Linear

```bash
python linearArray.py
```

Executa busca sequencial e busca binária sobre os arrays carregados do CSV.
Para a busca binária, o array é ordenado via Quick Sort antes da busca.

**Saída:**
- `results/Search-values-in-CSV_random-sequence_results.csv`
- `results/Binary-Search-in-CSV_random-sequence_results.csv`
- `results/graphs/` — gráficos PNG (steps, tempo, memória)

---

### 3. Benchmark — Árvores BST e AVL

```bash
python bst.py
```

Carrega os registros em uma BST simples e em uma AVL (auto-balanceada), depois mede a busca por matrícula em cada estrutura.

**Saída:**
- `results/Search-BST_random-sequence_results.csv`
- `results/Search-AVL_random-sequence_results.csv`

---

### 4. Benchmark — Tabela Hash

```bash
python hashtable.py
```

Testa três funções de hash (Divisão, Multiplicação, Folding) com três tamanhos de tabela M ∈ {100, 1.000, 5.000}.
Colisões são resolvidas por encadeamento exterior. Os steps medem o número de elementos percorridos na cadeia do bucket.

**Saída:** `results/Search-Hash-({função})_size{M}_{sufixo}_results.csv` — 9 arquivos no total.

---

## Estrutura dos CSVs de resultado

Todos os arquivos de resultado seguem o mesmo formato:

| Coluna | Descrição |
|---|---|
| `Size` | Volume N do dataset |
| `Time` | Tempo de execução em segundos |
| `Steps` | Número de comparações realizadas |
| `RSS_Memory_MB` | Memória física incrementada (psutil), em MB |
| `Peak_Python_Memory_MB` | Pico de memória Python alocada (tracemalloc), em MB |

A tabela hash inclui também a coluna `Load_Factor` (N/M).

Cada linha é uma rodada individual. Os resultados reportados no artigo são médias das 5 rodadas por volume.

---

## Estrutura de diretórios após execução

```
src/
├── data/               → 15 CSVs de entrada (gerados por dataGen.py)
├── results/
│   ├── *.csv           → métricas por experimento
│   └── graphs/         → gráficos PNG
├── dataGen.py
├── linearArray.py
├── bst.py
├── hashtable.py
└── plotGraph.py
```
