# fsd-dantas — Implementação

Contribuição de fsd-dantas para o Trabalho 01 – FAED/PPGIA-PUCPR.

Implementação do zero em Python 3.13 (stdlib apenas) das três estruturas
avaliadas: array linear, BST/AVL e tabela hash, com framework de benchmark
e geração de gráficos para o artigo IEEE.

---

## Arquivos

| Arquivo | Descrição |
|---|---|
| `data_generator.py` | Gerador de registros fictícios com seed fixo (reprodutível) |
| `linear_array.py` | Array linear com busca linear O(n) e busca binária O(log n) |
| `bst.py` | Árvore BST (sem balanceamento) e AVL (balanceamento automático) |
| `hash_table.py` | Tabela hash com encadeamento externo e 3 funções hash |
| `benchmark.py` | Framework unificado de benchmark (todas as estruturas) |
| `plot.py` | Geração de gráficos para o artigo (5 figuras IEEE) |
| `artigo/artigo.tex` | Artigo IEEE em LaTeX |

---

## Pré-requisitos

```bash
Python 3.13+
pip install matplotlib psutil   # única dependência externa (métricas e gráficos)
```

---

## Como executar

### 1. Gerar os datasets

```bash
# Gera registros para N = 10.000, 50.000, 100.000 e salva em dados/
python data_generator.py --csv

# Com análise de uso de memória
python data_generator.py --csv --memoria

# Volumes customizados
python data_generator.py --csv --volumes 10000 50000 100000
```

### 2. Array Linear

```bash
# Executa inserção + busca linear + busca binária para todos os volumes
python linear_array.py
```

Estrutura interna: lista Python (array dinâmico contíguo).
- **Inserção**: `O(1)` amortizado
- **Busca linear**: `O(n)` — percorre do início ao fim
- **Busca binária**: `O(log n)` — exige ordenação via QuickSort iterativo próprio

```python
from linear_array import LinearArray

arr = LinearArray()
arr.inserir_todos(registros)

resultado = arr.busca_linear(786579303)
# {'indice': 42, 'registro': {...}, 'iteracoes': 4301}

resultado = arr.busca_binaria(786579303)
# {'indice': 42, 'registro': {...}, 'iteracoes': 14}
```

### 3. BST e AVL

```bash
# Compara BST (sem balanceamento) vs AVL (balanceamento automático)
python bst.py
```

- **BST**: `O(log n)` médio, degrada para `O(n)` com dados ordenados
- **AVL**: `O(log n)` garantido — rotações LL, RR, LR, RL após cada inserção

```python
from bst import BST, AVL

bst = BST()
bst.inserir_todos(registros)
resultado = bst.buscar(786579303)
# {'registro': {...}, 'iteracoes': 18}

print(f"Altura BST: {bst.altura()}")   # ex: 38 para N=100.000
print(f"Altura AVL: {AVL().altura()}")  # ex: 19 para N=100.000
```

### 4. Tabela Hash

```bash
# Testa todas as combinações de M × função hash
python hash_table.py
```

Parâmetros avaliados:
- **M** (tamanho da tabela): `100`, `1.000`, `5.000`
- **Funções hash**: `divisao` · `multiplicacao` (Knuth) · `dobramento`
- Tratamento de colisões: encadeamento externo (lista encadeada por balde)
- Fator de carga: `α = n / M` — impacto direto em `O(1 + α)` por busca

```python
from hash_table import HashTable

ht = HashTable(m=5000, funcao="divisao")
ht.inserir_todos(registros)

resultado = ht.buscar(786579303)
# {'registro': {...}, 'iteracoes': 1}

stats = ht.estatisticas_cadeias()
# {'max_cadeia': 7, 'media_cadeia': 20.0, 'baldes_vazios': 0,
#  'load_factor': 20.0, 'colisoes': 94832}
```

### 5. Benchmark completo

```bash
# Roda todos os cenários (Array, BST, AVL, Hash) para N = 10k, 50k, 100k
python benchmark.py

# Volumes customizados
python benchmark.py --volumes 10000 100000

# Mais rodadas (default: 5)
python benchmark.py --rodadas 10
```

Saídas salvas em `resultados/`:
- `resultados_brutos_<timestamp>.csv` — uma linha por (estrutura, N, rodada)
- `resumo_<timestamp>.csv` — médias e desvios por cenário

### 6. Gráficos

```bash
# Gera as 5 figuras do artigo a partir do resumo mais recente
python plot.py

# Arquivo específico
python plot.py --resumo resultados/resumo_20260324_224349.csv

# Pasta de saída customizada
python plot.py --saida graficos/
```

Figuras geradas em `graficos/`:

| Figura | Conteúdo |
|---|---|
| `fig1_busca_iteracoes.png` | Iterações de busca vs N (escala log) — todas as estruturas |
| `fig2_insercao_tempo.png` | Tempo de inserção vs N |
| `fig3_hash_impacto_m.png` | Impacto do tamanho M nas iterações de busca (N=100k) |
| `fig4_hash_funcoes.png` | Comparação das funções hash por M (N=100k) |
| `fig5_bst_avl_altura.png` | Altura BST vs AVL vs log₂(N) |

---

## Design

- `seed=42` fixo garante os mesmos registros em qualquer máquina e versão
- `carregar_csv()` permite que todos os módulos usem dados byte-a-byte idênticos
- `medir_memoria()` usa `tracemalloc` para medir alocação real + `psutil` para RSS
- Nenhuma biblioteca de estrutura de dados utilizada — implementação do zero
- QuickSort iterativo (pilha explícita) evita *stack overflow* para N = 100.000
