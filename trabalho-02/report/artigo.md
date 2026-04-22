# Artigo — Nota de Sincronização

A versão canônica do artigo está em `main.tex`.

Este arquivo Markdown foi reduzido a uma nota de sincronização para evitar
divergência com o texto IEEE em Overleaf. Use `main.tex`, `references.bib`,
`results/metrics/sumario.csv` e as figuras em `report/figures/` como fontes
de verdade.

Resumo atual:

- Modelo: backhaul sintético de smart grid com 25 nós e 34 enlaces.
- Custo: latência normalizada, throughput normalizado e perda de pacotes
  normalizada.
- Experimento: 5 pares origem-destino, 5 repetições de medição por
  algoritmo/par.
- Resultado principal: A* manteve o custo ótimo de Dijkstra e reduziu nós
  expandidos de 77 para 58, uma redução de 24,7%.
- Busca gananciosa: menor expansão média, mas sobrecusto máximo de 51,3%.
- BFS/DFS: linhas de base didáticas sem garantia de otimalidade em grafos
  ponderados.
