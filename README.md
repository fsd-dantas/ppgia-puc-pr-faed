# Fundamentos de Algoritmos e Estrutura de Dados

**Programa de Pós-Graduação em Informática Aplicada — PPGIA/PUC-PR**
Prof. André Gustavo Hochuli

---

## Trabalho 01 — Análise Comparativa de Estruturas de Dados

Comparação experimental entre arrays lineares, árvores de busca binária (BST) e tabelas hash, avaliando desempenho em operações de inserção e busca com múltiplas métricas.

### Estruturas implementadas

| Estrutura | Variações |
|---|---|
| Array Linear | Busca sequencial |
| Árvore de Busca Binária (BST) | Com e sem balanceamento |
| Tabela Hash | 3 funções hash; tratamento de colisões; M = {100, 1000, 5000} |

### Volumes de dados

N = {10.000, 50.000, 100.000, …}

Cada registro contém: Matrícula (9 dígitos), Nome, Salário, Código do Setor e campos auxiliares.

### Métricas coletadas

- Número de iterações
- Consumo de memória (`tracemalloc`)
- Utilização de CPU (`psutil`)
- Colisões e load factor (tabelas hash)

Cada cenário é executado em **mínimo 5 rodadas independentes**; resultados reportados com média e desvio padrão.

---

## Estrutura do Repositório

```
ppgia-puc-pr-faed/
├── aulas/              # materiais organizados por aula
├── exercicios/         # listas e soluções
├── projetos/
│   └── trabalho-01/    # implementações e experimentos
│       ├── src/        # código-fonte (.py ou .c)
│       ├── data/       # datasets gerados
│       └── results/    # métricas e gráficos
└── docs/               # relatório IEEE e documentação
```

---

## Artefatos de Entrega

- [ ] Código-fonte (`.py` ou `.c`) — sem bibliotecas que já implementem as estruturas
- [ ] Relatório técnico no padrão IEEE (duas colunas, máx. 6 páginas)
- [ ] Pacote `.zip` entregue na atividade do Canvas

> **Atenção:** a não entrega do código-fonte **ou** do relatório invalida automaticamente todos os demais critérios da avaliação.

---

## Rúbricas (resumo)

| Critério | Peso |
|---|---|
| Implementação e funcionamento das estruturas | 35 pts |
| Análise de desempenho e métricas | 30 pts |
| Relatório científico (formatação, argumentação, análise comparativa) | 35 pts |

---

## Execução

> Instruções de execução serão adicionadas conforme a implementação avançar.

---

## Links

| Recurso | Link |
|---|---|
| Artigo (Overleaf) | https://www.overleaf.com/2469815365qdgwcmktybkw#0a9d97 |

---

*PPGIA/PUC-PR · 2026*
