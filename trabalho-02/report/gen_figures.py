"""
Gera figuras para o artigo IEEE — Trabalho 02 FAED/PPGIA/PUC-PR.

Uso:
    python report/gen_figures.py             # fig 1 (nós expandidos)
    python report/gen_figures.py --both      # fig 1 e fig 2 (custo)
    python report/gen_figures.py --topo      # topologia da rede

Saída: report/figures/fig_nos_expandidos.pdf
                      fig_custo_caminho.pdf
                      fig_topologia.pdf
"""
import argparse
import csv
import os
import sys

# permite importar src.* a partir da raiz do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

# ─── dados ───────────────────────────────────────────────────────────────────

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'metrics', 'sumario.csv')
OUT_DIR  = os.path.join(os.path.dirname(__file__), 'figures')

PAR_LABELS = {
    'remoto-para-AP-raiz':              'P1',
    'extremo-leste-para-AP-norte':      'P2',
    'extremo-oeste-para-extremo-sul':   'P3',
    'cross-branch-SAF4-para-SAF7':      'P4',
    'remoto-SW-para-remoto-NE':         'P5',
}

ALGORITMOS = ['Dijkstra', 'A*', 'Gananciosa', 'BFS', 'DFS']

# Paleta IEEE-friendly: sem saturação excessiva, distinguível em P&B
CORES  = ['#2166ac', '#4dac26', '#d01c8b', '#f1b6da', '#b8b8b8']
HACHS  = ['',        '///',     'xxx',     '...',     '---']


def _ler_csv():
    dados = {}
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            par = row['par']
            alg = row['algoritmo']
            dados[(par, alg)] = {
                'nos':   float(row['nos_expandidos_media']),
                'custo': float(row['custo_media']),
            }
    return dados


def _fig_nos_expandidos(dados):
    pares = list(PAR_LABELS.keys())
    x     = np.arange(len(pares))
    n     = len(ALGORITMOS)
    w     = 0.14
    offsets = np.linspace(-(n - 1) / 2 * w, (n - 1) / 2 * w, n)

    fig, ax = plt.subplots(figsize=(3.4, 2.5))

    for i, (alg, cor, hach) in enumerate(zip(ALGORITMOS, CORES, HACHS)):
        valores = [dados[(p, alg)]['nos'] for p in pares]
        ax.bar(x + offsets[i], valores, w, label=alg,
               color=cor, hatch=hach, edgecolor='black', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([PAR_LABELS[p] for p in pares], fontsize=6.5)
    ax.set_ylabel('Nós expandidos', fontsize=7)
    ax.set_ylim(0, 30)
    ax.axhline(25, color='black', linestyle='--', linewidth=0.8, label='$|V|{=}25$')
    ax.yaxis.set_tick_params(labelsize=7)
    ax.legend(fontsize=5.5, ncol=6, loc='upper left',
              columnspacing=0.5, handlelength=1.2, handletextpad=0.4)
    ax.grid(axis='y', linestyle=':', linewidth=0.5, alpha=0.7)
    ax.spines[['top', 'right']].set_visible(False)

    fig.tight_layout(pad=0.4)
    path = os.path.join(OUT_DIR, 'fig_nos_expandidos.pdf')
    fig.savefig(path, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'Gerado: {path}')


def _fig_custo_caminho(dados):
    pares = list(PAR_LABELS.keys())
    x     = np.arange(len(pares))

    fig, ax = plt.subplots(figsize=(3.4, 2.5))

    estilos = {
        'Dijkstra':   ('o', '-'),
        'A*':         ('s', '--'),
        'Gananciosa': ('^', '-.'),
        'BFS':        ('D', ':'),
        'DFS':        ('x', '-'),
    }

    for alg, cor in zip(ALGORITMOS, CORES):
        valores = [dados[(p, alg)]['custo'] for p in pares]
        marker, linestyle = estilos[alg]
        ax.plot(x, valores, linestyle=linestyle, marker=marker, label=alg,
                color=cor, linewidth=1.0, markersize=3.5,
                markeredgewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels([PAR_LABELS[p] for p in pares], fontsize=6.5)
    ax.set_ylabel('Custo do caminho', fontsize=7)
    ax.yaxis.set_tick_params(labelsize=7)
    ax.legend(fontsize=5.5, ncol=3, loc='upper left',
              columnspacing=0.7, handlelength=1.6, handletextpad=0.4)
    ax.grid(axis='y', linestyle=':', linewidth=0.5, alpha=0.7)
    ax.spines[['top', 'right']].set_visible(False)

    fig.tight_layout(pad=0.4)
    path = os.path.join(OUT_DIR, 'fig_custo_caminho.pdf')
    fig.savefig(path, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'Gerado: {path}')


def _fig_topologia():
    from src.graph_data import carregar_grafo
    from src.dijkstra import dijkstra
    from src.metrics import medir

    grafo = carregar_grafo()

    # Caminho Dijkstra Par 3: REM-01 (11) → REM-15 (25) — diagonal máxima, 6 saltos
    resultado = medir(dijkstra)(grafo, 11, 25)
    caminho_ids = set()
    path = resultado.get('caminho', [])
    for i in range(len(path) - 1):
        caminho_ids.add((min(path[i], path[i+1]), max(path[i], path[i+1])))

    # Estilo por tipo
    COR_NO   = {'AP': '#d62728', 'SAF': '#ff7f0e', 'Remote': '#2ca02c'}
    FORMA_NO = {'AP': '*',       'SAF': 's',        'Remote': 'o'}
    TAM_NO   = {'AP': 180,       'SAF': 60,         'Remote': 40}

    fig, ax = plt.subplots(figsize=(3.4, 3.0))

    xs = [attrs['x'] for attrs in grafo.nos.values()]
    ys = [attrs['y'] for attrs in grafo.nos.values()]
    x0, y0 = min(xs), min(ys)

    # Arestas
    visitados = set()
    for u, vizinhos in grafo._adj.items():
        for v, _, _ in vizinhos:
            par = (min(u, v), max(u, v))
            if par in visitados:
                continue
            visitados.add(par)
            xu, yu = grafo.nos[u]['x'] - x0, grafo.nos[u]['y'] - y0
            xv, yv = grafo.nos[v]['x'] - x0, grafo.nos[v]['y'] - y0
            if par in caminho_ids:
                ax.plot([xu, xv], [yu, yv], '-', color='#1f77b4',
                        linewidth=2.0, zorder=2)
            else:
                ax.plot([xu, xv], [yu, yv], '-', color='#cccccc',
                        linewidth=0.6, zorder=1)

    # Nós
    for nid, attrs in grafo.nos.items():
        tipo = attrs['tipo']
        ax.scatter(attrs['x'] - x0, attrs['y'] - y0,
                   c=COR_NO[tipo], marker=FORMA_NO[tipo],
                   s=TAM_NO[tipo], zorder=3,
                   edgecolors='black', linewidths=0.4)

    # Legenda de tipos
    handles = [
        mlines.Line2D([], [], marker='*', color='w', markerfacecolor='#d62728',
                      markeredgecolor='black', markeredgewidth=0.4,
                      markersize=9, label='AP'),
        mlines.Line2D([], [], marker='s', color='w', markerfacecolor='#ff7f0e',
                      markeredgecolor='black', markeredgewidth=0.4,
                      markersize=6, label='SAF'),
        mlines.Line2D([], [], marker='o', color='w', markerfacecolor='#2ca02c',
                      markeredgecolor='black', markeredgewidth=0.4,
                      markersize=5, label='Remote'),
        mlines.Line2D([], [], color='#1f77b4', linewidth=2,
                      label='Dijkstra P3'),
    ]
    ax.legend(handles=handles, fontsize=6, loc='upper left',
              framealpha=0.8, handlelength=1.2)

    ax.set_xlabel('x relativo (km)', fontsize=7)
    ax.set_ylabel('y relativo (km)', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_aspect('equal')

    fig.tight_layout(pad=0.4)
    path_out = os.path.join(OUT_DIR, 'fig_topologia.pdf')
    fig.savefig(path_out, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'Gerado: {path_out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--both', action='store_true')
    parser.add_argument('--topo', action='store_true')
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    dados = _ler_csv()
    _fig_nos_expandidos(dados)
    if args.both:
        _fig_custo_caminho(dados)
    if args.topo:
        _fig_topologia()
