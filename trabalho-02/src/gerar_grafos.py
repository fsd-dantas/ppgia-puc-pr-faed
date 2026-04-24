"""
Gera visualizações HTML Pyvis para todos os pares de teste × algoritmos.

Executa cada algoritmo uma vez por par (sem repetições) apenas para obter
o caminho. Não reescreve os CSVs de métricas.

Saída:
  results/graphs/grafo_base.html
  results/graphs/<alg>_<par>.html   (25 arquivos)

Uso:
    python -m src.gerar_grafos
"""
from src.graph_data import carregar_grafo
from src.runner import PARES_TESTE, ALGORITMOS
from src.visualization import renderizar, renderizar_base

DIR_GRAFOS = 'results/graphs'


def gerar_todos() -> None:
    grafo = carregar_grafo()

    topo = renderizar_base(grafo, saida=DIR_GRAFOS)
    print(f'  -> {topo}')

    for src, dst, descricao in PARES_TESTE:
        nome_src = grafo.nos[src]['nome']
        nome_dst = grafo.nos[dst]['nome']
        print(f"\n  Par: {nome_src} -> {nome_dst}  [{descricao}]")

        for nome_alg, func_alg in ALGORITMOS.items():
            resultado   = func_alg(grafo, src, dst)
            caminho_nos = resultado.get('caminho')
            html = renderizar(
                grafo, nome_alg, caminho_nos,
                saida=DIR_GRAFOS, par=descricao,
            )
            print(f'    -> {html}')

    print(f'\nConcluído. Arquivos em {DIR_GRAFOS}/')


if __name__ == '__main__':
    gerar_todos()
