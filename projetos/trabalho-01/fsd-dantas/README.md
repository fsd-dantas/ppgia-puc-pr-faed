# fsd-dantas — Implementação

 Contribuição de fsd-dantas para o Trabalho 01.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `data_generator.py` | Gerador de registros fictícios com seed fixo (reprodutível) |

## Pré-requisitos

- Python 3.13+
- Sem dependências externas (stdlib apenas: `csv`, `random`, `tracemalloc`, `sys`)

## Como executar

```bash
# Gerar datasets e exportar CSVs
python data_generator.py --csv

# Análise de memória
python data_generator.py --memoria

# Volumes customizados
python data_generator.py --csv --memoria --volumes 10000 50000 100000
```

## Dados gerados

Os CSVs são salvos em `dados/` (excluído do git — reproduzível via script).
Cada arquivo: `registros_<N>.csv` com campos `matricula, nome, salario, cod_setor`.

## Design

- `seed=42` fixo garante os mesmos registros em qualquer máquina/versão
- `carregar_csv()` permite que todos os benchmarks usem dados byte-a-byte idênticos
- `medir_memoria()` usa `tracemalloc` para medir alocação real
