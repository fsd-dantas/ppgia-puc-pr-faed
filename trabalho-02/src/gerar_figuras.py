"""
Gera as figuras para o relatório LaTeX.

Lê results/metrics/sumario.csv e escreve PDFs em report/figures/:

  fig_nos_expandidos.pdf  — barras agrupadas + linha de referência |V|=25
  fig_custo_caminho.pdf   — barras agrupadas + linha de custo ótimo por par
  fig_tradeoff.pdf        — dispersão eficiência–qualidade (figura nova)

Uso:
    python -m src.gerar_figuras
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SUMARIO_CSV = Path('results/metrics/sumario.csv')
FIGURAS_DIR = Path('report/figures')

ALGORITMOS = ['Dijkstra', 'A*', 'Gananciosa', 'BFS', 'DFS']

_PAR_LABEL = {
    'remoto-para-AP-raiz':            'P1',
    'extremo-leste-para-AP-norte':    'P2',
    'extremo-oeste-para-extremo-sul': 'P3',
    'cross-branch-SAF4-para-SAF7':    'P4',
    'remoto-SW-para-remoto-NE':       'P5',
}

_COR = {
    'Dijkstra':   '#1f77b4',
    'A*':         '#2ca02c',
    'Gananciosa': '#d62728',
    'BFS':        '#ff9896',
    'DFS':        '#aec7e8',
}

_HATCH = {
    'Dijkstra':   '\\\\',
    'A*':         '//',
    'Gananciosa': 'xx',
    'BFS':        '..',
    'DFS':        '--',
}

_FIG_W, _FIG_H = 5.0, 3.2


def _ler_sumario():
    dados = {}
    with open(SUMARIO_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            alg = row['algoritmo']
            par = _PAR_LABEL[row['par']]
            dados.setdefault(alg, {})[par] = {
                'nos':   float(row['nos_expandidos_media']),
                'custo': float(row['custo_media']),
                'mem':   float(row['memoria_pico_kb_media']),
            }
    return dados


def _bar_setup(n_algs=5):
    width  = 0.14
    x      = np.arange(5)
    offset = np.linspace(-(n_algs - 1) / 2 * width,
                          (n_algs - 1) / 2 * width, n_algs)
    return x, width, offset


def fig_nos_expandidos(dados):
    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    x, width, offset = _bar_setup()

    for i, alg in enumerate(ALGORITMOS):
        vals = [dados[alg][f'P{j+1}']['nos'] for j in range(5)]
        ax.bar(x + offset[i], vals, width,
               label=alg,
               color=_COR[alg], hatch=_HATCH[alg],
               edgecolor='black', linewidth=0.6)

    ax.axhline(25, color='black', linestyle='--', linewidth=1.0,
               label='$|V|=25$')

    ax.set_xticks(x)
    ax.set_xticklabels([f'P{i+1}' for i in range(5)])
    ax.set_ylabel('Nós expandidos')
    ax.set_ylim(0, 30)
    ax.yaxis.grid(True, linestyle=':', color='gray', alpha=0.5)
    ax.set_axisbelow(True)
    ax.legend(loc='upper left', fontsize=7, ncol=3, framealpha=0.9)
    fig.tight_layout()

    out = FIGURAS_DIR / 'fig_nos_expandidos.pdf'
    fig.savefig(out, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'  -> {out}')


def fig_custo_caminho(dados):
    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    x, width, offset = _bar_setup()

    custos_otimos = [dados['Dijkstra'][f'P{j+1}']['custo'] for j in range(5)]

    for i, alg in enumerate(ALGORITMOS):
        vals = [dados[alg][f'P{j+1}']['custo'] for j in range(5)]
        ax.bar(x + offset[i], vals, width,
               label=alg,
               color=_COR[alg], hatch=_HATCH[alg],
               edgecolor='black', linewidth=0.6)

    for j, custo_opt in enumerate(custos_otimos):
        ax.hlines(custo_opt, j - 0.42, j + 0.42,
                  colors='black', linestyles='--', linewidth=1.0)

    ax.set_xticks(x)
    ax.set_xticklabels([f'P{i+1}' for i in range(5)])
    ax.set_ylabel('Custo do caminho')
    ax.yaxis.grid(True, linestyle=':', color='gray', alpha=0.5)
    ax.set_axisbelow(True)
    ax.legend(loc='upper left', fontsize=7, ncol=3, framealpha=0.9)
    fig.tight_layout()

    out = FIGURAS_DIR / 'fig_custo_caminho.pdf'
    fig.savefig(out, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'  -> {out}')


def fig_tradeoff(dados):
    custos_otimo = [dados['Dijkstra'][f'P{j+1}']['custo'] for j in range(5)]

    totais_nos, sobrecusto_med = {}, {}
    for alg in ALGORITMOS:
        totais_nos[alg] = sum(dados[alg][f'P{j+1}']['nos'] for j in range(5))
        overheads = [
            (dados[alg][f'P{j+1}']['custo'] - custos_otimo[j]) / custos_otimo[j] * 100
            for j in range(5)
        ]
        sobrecusto_med[alg] = sum(overheads) / len(overheads)

    # (dx, dy) text offset in data units
    _label_offset = {
        'Dijkstra':   ( 1.2, -2.2),
        'A*':         ( 1.2,  0.7),
        'Gananciosa': ( 0.0,  1.0),
        'BFS':        (-13.0, 1.2),
        'DFS':        ( 1.2, -2.2),
    }

    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))

    for alg in ALGORITMOS:
        xv = totais_nos[alg]
        yv = sobrecusto_med[alg]
        ax.scatter(xv, yv,
                   color=_COR[alg], s=70,
                   edgecolors='black', linewidths=0.6,
                   zorder=3, label=alg)
        dx, dy = _label_offset[alg]
        ax.annotate(alg, (xv, yv),
                    xytext=(xv + dx, yv + dy),
                    fontsize=7.5)

    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.4)
    ax.set_xlabel('Total de Nós Expandidos (5 pares)')
    ax.set_ylabel('Sobrecusto Médio (%)')
    ax.set_xlim(25, 90)
    ax.set_ylim(-4, 26)
    ax.yaxis.grid(True, linestyle=':', color='gray', alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()

    out = FIGURAS_DIR / 'fig_tradeoff.pdf'
    fig.savefig(out, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f'  -> {out}')


def gerar_todas():
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    dados = _ler_sumario()
    fig_nos_expandidos(dados)
    fig_custo_caminho(dados)
    fig_tradeoff(dados)
    print('Figuras geradas com sucesso.')


if __name__ == '__main__':
    gerar_todas()
