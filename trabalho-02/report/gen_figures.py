"""
Gera figuras para o artigo IEEE — Trabalho 02 FAED/PPGIA/PUC-PR.

Uso:
    python report/gen_figures.py
    python report/gen_figures.py --both   # gera fig 1 e fig 2

Saída: report/figures/fig_nos_expandidos.pdf
                      fig_custo_caminho.pdf
"""
import argparse
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    ax.yaxis.set_tick_params(labelsize=7)
    ax.legend(fontsize=5.5, ncol=5, loc='upper left',
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
    n     = len(ALGORITMOS)
    w     = 0.14
    offsets = np.linspace(-(n - 1) / 2 * w, (n - 1) / 2 * w, n)

    fig, ax = plt.subplots(figsize=(3.4, 2.5))

    for i, (alg, cor, hach) in enumerate(zip(ALGORITMOS, CORES, HACHS)):
        valores = [dados[(p, alg)]['custo'] for p in pares]
        ax.bar(x + offsets[i], valores, w, label=alg,
               color=cor, hatch=hach, edgecolor='black', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([PAR_LABELS[p] for p in pares], fontsize=6.5)
    ax.set_ylabel('Custo do caminho', fontsize=7)
    ax.yaxis.set_tick_params(labelsize=7)
    ax.legend(fontsize=5.5, ncol=5, loc='upper left',
              columnspacing=0.5, handlelength=1.2, handletextpad=0.4)
    ax.grid(axis='y', linestyle=':', linewidth=0.5, alpha=0.7)
    ax.spines[['top', 'right']].set_visible(False)

    fig.tight_layout(pad=0.4)
    path = os.path.join(OUT_DIR, 'fig_custo_caminho.pdf')
    fig.savefig(path, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'Gerado: {path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--both', action='store_true')
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    dados = _ler_csv()
    _fig_nos_expandidos(dados)
    if args.both:
        _fig_custo_caminho(dados)
