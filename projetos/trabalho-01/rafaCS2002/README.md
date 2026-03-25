# RafaCS2002 — Implementação

Implementação individual de RafaCS2002 para o Trabalho 01.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `dataGen.py` | Gerador de registros com `SystemRandom`, exporta CSVs por rodada |
| `linearArray.py` | Array linear com busca linear e busca binária (QuickSort) |
| `bst.py` | Árvore de busca binária (BST) com e sem balanceamento |
| `hashtable.py` | Tabela hash com múltiplas funções e tratamento de colisões |
| `plotGraph.py` | Geração de gráficos a partir dos resultados coletados |

## Pré-requisitos

```bash
pip install psutil matplotlib
```

## Como executar

```bash
# 1. Gerar dados (cria genData/ ou genDataSequence/)
python dataGen.py

# 2. Executar benchmarks de array linear
python linearArray.py

# 3. Executar benchmarks de BST
python bst.py

# 4. Executar benchmarks de tabela hash
python hashtable.py

# 5. Gerar gráficos a partir dos resultados
python plotGraph.py
```

## Dados gerados

Os diretórios `genData/`, `genDataSequence/`, `genResults/` e `genGraph/`
são excluídos do git — reproduzíveis executando os scripts acima.
