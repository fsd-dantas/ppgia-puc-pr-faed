# Trabalho 01 — Análise Comparativa de Estruturas de Dados


## Objetivo

Comparação experimental entre arrays lineares, árvores de busca binária (BST) e tabelas hash, avaliando desempenho em operações de inserção e busca com múltiplas métricas.

## Estruturas implementadas

| Estrutura | Variações |
|---|---|
| Array Linear | Busca sequencial e binária |
| Árvore de Busca Binária (BST) | Com e sem balanceamento (AVL) |
| Tabela Hash | 3 funções hash; tratamento de colisões; M = {100, 1.000, 5.000} |

## Volumes de dados

N = {10.000, 50.000, 100.000}

Cada registro contém: Matrícula (9 dígitos), Nome, Salário, Código do Setor.

## Métricas coletadas

- Número de iterações
- Tempo de execução
- Consumo de memória (`tracemalloc`)
- Colisões e load factor (tabelas hash)

Cada cenário executado em mínimo 5 rodadas independentes; resultados reportados com média e desvio padrão.

## Estrutura

```
trabalho-01/
├── src/        → código-fonte das implementações
├── data/       → datasets gerados (gitignored — reproduzível via script)
├── results/    → métricas e gráficos (gitignored — reproduzível via script)
└── article/    → artigo IEEE em LaTeX
```

## Como reproduzir

```bash
# Gerar dados
cd src/
python dataGen.py

# Executar benchmarks
python linearArray.py
python bst.py
python hashtable.py

# Gerar gráficos
python plotGraph.py
```

## Entregáveis

| Artefato | Descrição |
|---|---|
| Código-fonte `.py` | `src/` — sem bibliotecas que implementem as estruturas |
| Artigo IEEE | `article/artigo.tex` — duas colunas, máx. 6 páginas |
| Pacote `.zip` | Entregue na atividade do Canvas |

> **Atenção:** a não entrega do código-fonte **ou** do artigo invalida automaticamente todos os demais critérios da avaliação.

## Rúbricas

| Critério | Peso |
|---|---|
| Implementação e funcionamento das estruturas | 35 pts |
| Análise de desempenho e métricas | 30 pts |
| Artigo científico (formatação, argumentação, análise comparativa) | 35 pts |

## Integrantes

| GitHub |
|---|
| [fsd-dantas](https://github.com/fsd-dantas) |
| [RafaCS2002](https://github.com/RafaCS2002) |
| [guilherme-campagnoli](https://github.com/guilherme-campagnoli) |

## Links

| Recurso | Link |
|---|---|
| Artigo (Overleaf) | https://www.overleaf.com/2469815365qdgwcmktybkw#0a9d97 |
