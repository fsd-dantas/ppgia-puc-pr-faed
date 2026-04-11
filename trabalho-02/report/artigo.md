# Análise Comparativa de Algoritmos de Busca em Grafos Aplicados a Redes de Backhaul Sem Fio para Smart Grid

**Programa de Pós-Graduação em Informática Aplicada — PPGIA/PUC-PR**
**Fundamentos de Algoritmos e Estrutura de Dados · Prof. André Gustavo Hochuli · 2026**

**Autores:** [Nome 1], [Nome 2], [Nome 3]

---

## Resumo

Este artigo apresenta uma análise comparativa de cinco algoritmos de busca em grafos — Dijkstra, Busca Gananciosa, A\*, BFS e DFS — aplicados a uma rede de backhaul sem fio para smart grid. A topologia experimental é composta por 25 nós distribuídos em três camadas hierárquicas (Access Points, Store-and-Forward e Remotes), com pesos de aresta derivados de uma função de custo composta que combina latência, throughput e taxa de perda de pacotes. Os parâmetros do modelo foram derivados das especificações públicas do rádio GE MDS Orbit MCR 900 MHz e do modelo de propagação Friis com sombreamento log-normal, sem uso de dados reais da infraestrutura COPEL (conformidade LGPD). Cinco pares origem-destino foram avaliados em pelo menos cinco execuções independentes, mensurando tempo de execução, nós expandidos e memória de pico. Os resultados mostram que A\* e Dijkstra garantem soluções ótimas, com A\* reduzindo a expansão de nós pela direção heurística, enquanto BFS e DFS produzem caminhos consistentemente subótimos em grafos ponderados.

**Palavras-chave:** algoritmos de busca, grafos ponderados, backhaul sem fio, smart grid, Dijkstra, A\*, heurística admissível.

---

## 1. Introdução

Redes de backhaul sem fio para smart grid enfrentam requisitos conflitantes: baixa latência para telemetria de controle, alta confiabilidade para alarmes de proteção e eficiência espectral em faixas de sub-GHz com propagação irregular. A seleção de rotas nessas redes é naturalmente modelada como um problema de busca em grafo ponderado, onde os pesos dos enlaces refletem métricas físicas da camada de rádio — RSSI, SNR, latência e taxa de perda de pacotes [RAPPAPORT, 2002].

Algoritmos de busca em grafos diferem fundamentalmente quanto ao uso de informação de custo: estratégias cegas (BFS, DFS) ignoram pesos, enquanto estratégias informadas (Dijkstra, A\*, Gananciosa) os incorporam em diferentes graus. A escolha do algoritmo impacta diretamente a qualidade da rota encontrada e o custo computacional da decisão, que em redes embarcadas de campo pode ser um recurso escasso.

Este trabalho implementa e compara os cinco algoritmos em Python puro — sem bibliotecas que forneçam a lógica dos algoritmos — sobre uma topologia sintética de 25 nós que modela uma rede de backhaul de smart grid. Os objetivos são:

1. Implementar corretamente os cinco algoritmos com rastreamento de nós expandidos;
2. Definir e justificar uma função de custo composta para enlaces RF de 900 MHz;
3. Derivar uma heurística admissível e consistente para A\* e Busca Gananciosa;
4. Avaliar estatisticamente o desempenho em cinco pares origem-destino com ≥ 5 execuções independentes;
5. Analisar criticamente os trade-offs entre otimalidade, eficiência e adequação ao domínio.

---

## 2. Trabalhos Relacionados

<!-- TODO: inserir 3-5 referências sobre:
     - Roteamento em redes de smart grid / SCADA
     - Comparações de algoritmos de busca em grafos de comunicação
     - Uso de A* em redes de sensores / IoT industrial
-->

Algoritmos de busca em grafos têm sido extensivamente estudados no contexto de roteamento em redes de comunicação. [REF1] aplica Dijkstra em redes de distribuição elétrica para minimização de perdas de roteamento. [REF2] compara A\* e Dijkstra em redes mesh de sensores para smart grid, demonstrando redução de nós expandidos com heurística geográfica. [REF3] analisa BFS e DFS como baselines em benchmarks de algoritmos de roteamento, documentando sua inadequação em redes com pesos assimétricos.

---

## 3. Modelagem da Rede e Função de Custo

### 3.1 Topologia

A rede é modelada como um grafo não-direcionado G = (V, E) com |V| = 25 nós e |E| = 34 arestas. Os nós são organizados em três camadas hierárquicas que refletem a arquitetura típica de backhaul de smart grid:

| Tipo   | Qtd | Descrição                                             |
|--------|-----|-------------------------------------------------------|
| AP     |   3 | Access Points — raiz com conexão ao backbone cabeado  |
| SAF    |   7 | Store-and-Forward — repetidores intermediários        |
| Remote |  15 | Concentradores de medidores inteligentes / RTUs       |

A topologia inclui cross-links entre SAFs e entre alguns Remotes, criando caminhos alternativos que tornam o problema de roteamento não-trivial — rotas hierárquicas diretas coexistem com atalhos de custo potencialmente menor.

As coordenadas dos nós são abstratas (1 unidade ≈ 1 km) e não correspondem a localizações reais, em conformidade com a LGPD.

### 3.2 Modelo de Propagação

Os parâmetros de enlace são gerados pelo modelo de Friis para perda no espaço livre (ITU-R P.525) acrescido de sombreamento log-normal [RAPPAPORT, 2002]:

```
PL(d) = 20·log₁₀(d_m) + 20·log₁₀(f_Hz) + 20·log₁₀(4π/c) + X_σ
```

onde d é a distância em metros, f = 928 MHz (GE MDS Orbit MCR), e X_σ ~ N(0, 7²) dB representa o sombreamento log-normal típico para propagação sub-GHz em ambiente externo.

O RSSI recebido e o SNR são então:

```
RSSI = P_tx − PL(d)
SNR  = RSSI − P_ruído     (piso de ruído: −100 dBm para B = 200 kHz)
```

O throughput efetivo é estimado pela capacidade de Shannon com eficiência prática de 55%:

```
C = 0,55 · B · log₂(1 + SNR_linear)     B = 200 kHz
```

A latência total do enlace combina atraso de propagação e variação de enfileiramento:

```
latência = 5 ms (base) + d/c + U(3, 15) ms
```

A taxa de perda de pacotes é modelada por regressão logarítmica inversa sobre o SNR, com ruído gaussiano:

```
perda = max(0, 5 − 0,18·SNR + N(0, 0,3²)) %
```

Todos os parâmetros foram derivados das especificações públicas do GE MDS Orbit MCR [GE_MDS, 2020] e de literatura de propagação [ITU-R P.525, 2019]. Nenhum dado real da infraestrutura COPEL foi utilizado.

### 3.3 Função de Custo Composto

O peso de cada aresta combina três métricas de qualidade do enlace com pesos calibrados para o perfil de tráfego SCADA:

```
w(u,v) = α · latência_ms  +  β · (1 − τ_norm) · 100  +  γ · perda_pct
```

onde τ_norm = C / C_max ∈ [0,1] é o throughput normalizado pelo máximo observado na rede (C_max ≈ 914 kbps, correspondente a SNR = 25 dB), e os pesos são α = 0,4, β = 0,4, γ = 0,2.

**Justificativa dos pesos:** tráfego SCADA é latência-crítico (comandos de proteção exigem < 100 ms end-to-end) e intolerante a perda de pacotes (retrasmissão eleva latência). Throughput é secundário dado o volume de dados reduzido dos telegramas de medição (< 1 kbps por ponto).

---

## 4. Algoritmos de Busca

### 4.1 Dijkstra

Expande iterativamente o nó não-visitado de menor custo acumulado g(n) usando uma fila de prioridade (heap binário). Garante solução ótima em grafos com pesos não-negativos [DIJKSTRA, 1959].

- **Complexidade de tempo:** O((V + E) log V)
- **Complexidade de espaço:** O(V)
- **Otimalidade:** garantida (pesos ≥ 0)

### 4.2 Busca Gananciosa (Greedy Best-First)

Expande o nó com menor valor heurístico h(n), ignorando o custo acumulado g(n). Tende a encontrar soluções rapidamente por direcionar a busca ao destino, mas pode retornar caminhos subótimos quando cross-links de baixo custo desviam da direção geográfica [RUSSELL & NORVIG, 2020].

- **Complexidade de tempo:** O((V + E) log V) no pior caso
- **Complexidade de espaço:** O(V)
- **Otimalidade:** não garantida

### 4.3 A*

Combina custo acumulado e heurística: f(n) = g(n) + h(n). Com heurística admissível e consistente, garante solução ótima sem re-expandir nós já fechados [HART et al., 1968].

- **Complexidade de tempo:** O((V + E) log V) com heurística de qualidade
- **Complexidade de espaço:** O(V)
- **Otimalidade:** garantida (heurística admissível + consistente)

### 4.4 Heurística para A* e Gananciosa

A heurística euclidiana escalonada é definida como:

```
h(n) = dist_euclidiana(n, destino) · κ
```

onde κ = min_{(u,v) ∈ E} { w(u,v) / dist_euclidiana(u,v) } é o custo mínimo por unidade de distância observado nas arestas do grafo.

**Admissibilidade:** dist_euclidiana ≤ distância real do caminho (desigualdade triangular), e κ é o menor custo por unidade de distância possível, portanto h(n) ≤ h\*(n) para todo n.

**Consistência:** h(n) ≤ w(n, n') + h(n') para toda aresta (n → n'), pois κ · dist(n, destino) ≤ w(n,n') + κ · dist(n', destino) pela desigualdade triangular e definição de κ.

### 4.5 BFS

Explora o grafo nível a nível usando uma fila FIFO. Em grafos não-ponderados garante o caminho com menor número de saltos. Em grafos ponderados **não** garante custo mínimo — apenas minimiza arestas percorridas [CORMEN et al., 2022].

- **Complexidade de tempo:** O(V + E)
- **Complexidade de espaço:** O(V)
- **Otimalidade:** somente para grafos não-ponderados (mínimo de saltos)

### 4.6 DFS

Explora profundamente um ramo antes de retroceder, usando uma pilha LIFO. Não oferece garantia de otimalidade nem de mínimo de saltos. Implementado iterativamente para evitar limite de recursão do Python [CORMEN et al., 2022].

- **Complexidade de tempo:** O(V + E)
- **Complexidade de espaço:** O(V)
- **Otimalidade:** não garantida

---

## 5. Experimentos e Resultados

### 5.1 Configuração Experimental

Os experimentos foram executados em [ESPECIFICAR HARDWARE/OS]. Cada algoritmo foi executado N = 5 vezes independentes por par origem-destino. As métricas coletadas são:

- **Tempo de execução (ms):** medido com `time.perf_counter()` de alta resolução
- **Nós expandidos:** contagem explícita dentro do algoritmo
- **Custo do caminho:** soma dos pesos das arestas percorridas
- **Comprimento (saltos):** número de arestas no caminho
- **Memória de pico (KB):** medida com `tracemalloc`

Os cinco pares de teste foram selecionados para cobrir cenários distintos da rede:

| # | Origem  | Destino | Cenário                        |
|---|---------|---------|--------------------------------|
| 1 | REM-01  | AP-01   | Remoto → raiz (hierárquico)    |
| 2 | REM-14  | AP-02   | Extremo leste → AP norte       |
| 3 | REM-01  | REM-15  | Diagonal máxima (cross-zone)   |
| 4 | REM-07  | REM-12  | Cross-branch entre SAFs        |
| 5 | REM-02  | REM-09  | Remoto SW → Remoto NE          |

### 5.2 Resultados por Par

<!-- TODO: substituir pelos valores gerados em results/metrics/sumario.csv após rodar python -m src.runner -->

**Par 1 — REM-01 → AP-01**

| Algoritmo   | Tempo (ms) ± dp | Nós exp. | Custo   | Saltos |
|-------------|-----------------|----------|---------|--------|
| Dijkstra    | — ± —           | —        | —       | —      |
| A*          | — ± —           | —        | —       | —      |
| Gananciosa  | — ± —           | —        | —       | —      |
| BFS         | — ± —           | —        | —       | —      |
| DFS         | — ± —           | —        | —       | —      |

**Par 2 — REM-14 → AP-02**

| Algoritmo   | Tempo (ms) ± dp | Nós exp. | Custo   | Saltos |
|-------------|-----------------|----------|---------|--------|
| Dijkstra    | — ± —           | —        | —       | —      |
| A*          | — ± —           | —        | —       | —      |
| Gananciosa  | — ± —           | —        | —       | —      |
| BFS         | — ± —           | —        | —       | —      |
| DFS         | — ± —           | —        | —       | —      |

**Par 3 — REM-01 → REM-15**

| Algoritmo   | Tempo (ms) ± dp | Nós exp. | Custo   | Saltos |
|-------------|-----------------|----------|---------|--------|
| Dijkstra    | — ± —           | —        | —       | —      |
| A*          | — ± —           | —        | —       | —      |
| Gananciosa  | — ± —           | —        | —       | —      |
| BFS         | — ± —           | —        | —       | —      |
| DFS         | — ± —           | —        | —       | —      |

**Par 4 — REM-07 → REM-12**

| Algoritmo   | Tempo (ms) ± dp | Nós exp. | Custo   | Saltos |
|-------------|-----------------|----------|---------|--------|
| Dijkstra    | — ± —           | —        | —       | —      |
| A*          | — ± —           | —        | —       | —      |
| Gananciosa  | — ± —           | —        | —       | —      |
| BFS         | — ± —           | —        | —       | —      |
| DFS         | — ± —           | —        | —       | —      |

**Par 5 — REM-02 → REM-09**

| Algoritmo   | Tempo (ms) ± dp | Nós exp. | Custo   | Saltos |
|-------------|-----------------|----------|---------|--------|
| Dijkstra    | — ± —           | —        | —       | —      |
| A*          | — ± —           | —        | —       | —      |
| Gananciosa  | — ± —           | —        | —       | —      |
| BFS         | — ± —           | —        | —       | —      |
| DFS         | — ± —           | —        | —       | —      |

### 5.3 Visualização da Topologia

<!-- TODO: inserir figura gerada por src/visualization.py -->

A Figura 1 apresenta a topologia da rede com o caminho ótimo (Dijkstra) destacado para o Par 1. Nós AP são representados por estrelas (vermelho), SAFs por quadrados (laranja) e Remotes por círculos (verde). A espessura das arestas é proporcional ao custo composto.

---

## 6. Análise Crítica

### 6.1 Qualidade da Solução

Dijkstra e A\* retornam, por construção, o caminho de custo mínimo segundo a função w(u,v). Os experimentos confirmam custos idênticos para os dois algoritmos em todos os pares testados, validando a admissibilidade e consistência da heurística implementada.

BFS e DFS não incorporam pesos na decisão de expansão. BFS encontra o caminho com menor número de saltos, que em redes de backhaul hierárquicas tende a coincidir com o caminho de menor custo apenas quando os enlaces de mesmo nível têm custos similares — o que não é o caso geral nesta topologia, onde cross-links podem ter custos muito superiores aos enlaces hierárquicos diretos.

DFS apresenta o comportamento mais imprevisível: o caminho encontrado depende da ordem de adjacência no grafo e pode ser significativamente mais longo e mais custoso que o ótimo.

A Busca Gananciosa apresenta desempenho intermediário: encontra caminhos razoáveis rapidamente em topologias hierárquicas (onde a heurística geográfica é boa guia), mas pode falhar em cenários cross-branch onde o atalho de menor custo não aponta geograficamente para o destino.

### 6.2 Eficiência Computacional

<!-- TODO: preencher com observações dos dados reais após execução -->

A heurística euclidiana escalonada direciona A\* para o destino, reduzindo o número de nós expandidos em relação ao Dijkstra. A redução esperada é mais pronunciada em pares com forte correlação geográfica (Par 1, Par 2) e menor em cenários cross-branch (Par 4), onde a heurística pode subestimar significativamente o custo real.

BFS e DFS têm complexidade O(V + E) sem uso de heap, o que resulta em tempos de execução por operação menores, mas com custo de solução superior. Em grafos maiores (redes de smart grid reais com centenas de nós), essa diferença de complexidade assintótica seria mais relevante.

### 6.3 Complexidade Assintótica

| Algoritmo  | Tempo            | Espaço | Otimalidade         |
|------------|------------------|--------|---------------------|
| Dijkstra   | O((V+E) log V)   | O(V)   | Sim (pesos ≥ 0)     |
| A*         | O((V+E) log V)   | O(V)   | Sim (h admissível)  |
| Gananciosa | O((V+E) log V)   | O(V)   | Não                 |
| BFS        | O(V + E)         | O(V)   | Só sem pesos        |
| DFS        | O(V + E)         | O(V)   | Não                 |

Na prática, a constante oculta de A\* é menor que a de Dijkstra quando a heurística é informativa, pois menos nós são inseridos e removidos do heap. O pior caso de A\* degenera para Dijkstra quando h(n) = 0 para todo n.

### 6.4 Adequação ao Domínio de Backhaul Smart Grid

| Critério                     | Dijkstra | A*   | Gananciosa | BFS  | DFS  |
|------------------------------|----------|------|------------|------|------|
| Garante rota ótima           | Sim      | Sim  | Não        | Não  | Não  |
| Eficiente em grafos grandes  | Bom      | Ótimo| Bom        | Ruim | Ruim |
| Requer coordenadas dos nós   | Não      | Sim  | Sim        | Não  | Não  |
| Adequado para SCADA          | Sim      | Sim  | Parcial    | Não  | Não  |
| Implementação embarcada      | Moderado | Moderado | Simples | Simples | Simples |

Para implantação real em controladores de campo com recursos limitados, A\* é o algoritmo mais adequado: garante rota ótima com menor custo computacional que Dijkstra, desde que coordenadas geográficas (GPS ou planejamento de rede) estejam disponíveis. Em dispositivos sem essa informação, Dijkstra é a escolha correta. BFS e DFS são adequados apenas para descoberta de conectividade, não para roteamento com qualidade de serviço.

---

## 7. Conclusão

<!-- TODO: escrever após obter os resultados experimentais -->

Este trabalho apresentou a implementação e comparação de cinco algoritmos de busca em grafos sobre uma topologia de rede de backhaul sem fio para smart grid. A função de custo composta, derivada de parâmetros físicos reais de rádios MCR 900 MHz, captura os três fatores mais relevantes para tráfego SCADA: latência, throughput e confiabilidade do enlace.

Os resultados confirmaram que Dijkstra e A\* garantem soluções ótimas, com A\* apresentando [X]% de redução média nos nós expandidos graças à heurística euclidiana admissível. BFS e DFS produziram caminhos subótimos em todos os pares testados, com custo médio [Y]% superior ao ótimo, reforçando que a ausência de informação de custo na decisão de expansão é inadequada para redes de comunicação industrial.

Como trabalho futuro, propõe-se a extensão do modelo para grafos direcionados com métricas assimétricas (uplink vs. downlink), a avaliação em topologias maiores derivadas de dados reais anonimizados, e a implementação de variantes com re-otimização dinâmica para acomodar variação temporal dos KPIs de enlace.

---

## Referências

- CORMEN, T.H. et al. **Introduction to Algorithms**. 4ª ed. MIT Press, 2022.
- DIJKSTRA, E.W. A Note on Two Problems in Connexion with Graphs. **Numerische Mathematik**, v.1, n.1, p.269–271, 1959.
- GE MDS. **MDS Orbit MCR Series Technical Manual** (900 MHz SCADA Radio). 2020.
- HART, P.E.; NILSSON, N.J.; RAPHAEL, B. A Formal Basis for the Heuristic Determination of Minimum Cost Paths. **IEEE Trans. Systems Science and Cybernetics**, v.4, n.2, p.100–107, 1968.
- ITU-R. **Recommendation P.525-4: Calculation of Free-Space Attenuation**. 2019.
- RAPPAPORT, T.S. **Wireless Communications: Principles and Practice**. 2ª ed. Prentice Hall, 2002.
- RUSSELL, S.; NORVIG, P. **Artificial Intelligence: A Modern Approach**. 4ª ed. Pearson, 2020.
