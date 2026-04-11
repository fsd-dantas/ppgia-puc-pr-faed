"""
Visualização do grafo de backhaul com Pyvis.

Gera arquivos HTML interativos com:
  - Cor e forma dos nós por tipo (AP, SAF, Remote)
  - Espessura das arestas proporcional ao custo (custo maior = aresta mais grossa)
  - Caminho encontrado destacado em vermelho
  - Tooltip com atributos completos do nó e do enlace ao passar o mouse

Saída:
  results/graphs/grafo_base.html           — topologia completa sem caminho
  results/graphs/<algoritmo>_<par>.html    — topologia com caminho destacado

Uso:
    from src.visualization import renderizar
    renderizar(grafo, 'Dijkstra', caminho=[11, 4, 1], saida='results/graphs')
"""
import os
from typing import List, Optional

from pyvis.network import Network

from src.graph import Grafo

# ──────────────────────────────────────────────────────────────────────────────
# Configuração visual
# ──────────────────────────────────────────────────────────────────────────────

COR_NO = {
    'AP':     '#e74c3c',   # vermelho — nó raiz
    'SAF':    '#f39c12',   # laranja  — repetidor
    'Remote': '#2ecc71',   # verde    — folha
}

FORMA_NO = {
    'AP':     'star',
    'SAF':    'square',
    'Remote': 'dot',
}

COR_ARESTA_NORMAL   = '#555555'
COR_ARESTA_CAMINHO  = '#e74c3c'
LARGURA_MIN_ARESTA  = 1.0
LARGURA_MAX_ARESTA  = 8.0


def _calcular_largura(peso: float, peso_min: float, peso_max: float) -> float:
    """Normaliza o peso para a faixa de largura visual."""
    if peso_max == peso_min:
        return (LARGURA_MIN_ARESTA + LARGURA_MAX_ARESTA) / 2
    norm = (peso - peso_min) / (peso_max - peso_min)
    return LARGURA_MIN_ARESTA + norm * (LARGURA_MAX_ARESTA - LARGURA_MIN_ARESTA)


def renderizar(
    grafo: Grafo,
    algoritmo: str,
    caminho: Optional[List[int]] = None,
    saida: str = 'results/graphs',
) -> str:
    """
    Gera um HTML Pyvis do grafo com o caminho destacado.

    Parâmetros:
        grafo      : instância do Grafo carregado
        algoritmo  : nome do algoritmo (usado no nome do arquivo)
        caminho    : sequência de IDs de nós do caminho encontrado
        saida      : diretório de destino dos HTMLs

    Retorna o caminho do arquivo gerado.
    """
    os.makedirs(saida, exist_ok=True)

    net = Network(
        height='750px', width='100%',
        bgcolor='#1a1a2e', font_color='#eeeeee',
        directed=False,
    )
    net.toggle_physics(True)
    net.set_options("""
    {
      "physics": {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": { "gravitationalConstant": -80, "springLength": 120 }
      }
    }
    """)

    # Conjunto de arestas no caminho para destaque rápido
    arestas_caminho: set = set()
    if caminho and len(caminho) > 1:
        for i in range(len(caminho) - 1):
            arestas_caminho.add((caminho[i], caminho[i + 1]))
            arestas_caminho.add((caminho[i + 1], caminho[i]))

    # Pesos para normalização de espessura
    todos_pesos = [
        peso
        for no_id in grafo.nos
        for (_, peso, _) in grafo.vizinhos(no_id)
    ]
    peso_min = min(todos_pesos) if todos_pesos else 1.0
    peso_max = max(todos_pesos) if todos_pesos else 1.0

    # Nós
    for no_id, attrs in grafo.nos.items():
        tipo  = attrs.get('tipo', 'Remote')
        label = attrs['nome']
        title = (
            f"<b>{label}</b><br>"
            f"Tipo: {tipo}<br>"
            f"Coords: ({attrs['x']:.1f}, {attrs['y']:.1f})<br>"
            f"Tx: {attrs.get('potencia_tx_dbm', '—')} dBm"
        )
        cor = COR_NO.get(tipo, '#95a5a6')
        if caminho and no_id in caminho:
            cor = '#ffffff'

        net.add_node(
            no_id,
            label=label,
            title=title,
            color=cor,
            shape=FORMA_NO.get(tipo, 'dot'),
            size=20 if tipo == 'AP' else (14 if tipo == 'SAF' else 10),
            x=attrs['x'] * 10,
            y=-attrs['y'] * 10,  # Y invertido para orientação norte-sul
            physics=False,
        )

    # Arestas (percorre apenas src < dst para evitar duplicatas)
    adicionadas: set = set()
    for src_id in grafo.nos:
        for dst_id, peso, attrs in grafo.vizinhos(src_id):
            par = (min(src_id, dst_id), max(src_id, dst_id))
            if par in adicionadas:
                continue
            adicionadas.add(par)

            no_caminho  = (src_id, dst_id) in arestas_caminho
            cor         = COR_ARESTA_CAMINHO if no_caminho else COR_ARESTA_NORMAL
            largura     = _calcular_largura(peso, peso_min, peso_max)
            if no_caminho:
                largura = max(largura, 3.5)

            title = (
                f"<b>{grafo.nos[src_id]['nome']} → {grafo.nos[dst_id]['nome']}</b><br>"
                f"Peso: {peso:.4f}<br>"
                f"Dist: {attrs.get('distancia_km', '—')} km<br>"
                f"RSSI: {attrs.get('rssi_dbm', '—')} dBm<br>"
                f"SNR: {attrs.get('snr_db', '—')} dB<br>"
                f"Latência: {attrs.get('latencia_ms', '—')} ms<br>"
                f"Throughput: {attrs.get('throughput_kbps', '—')} kbps<br>"
                f"Perda: {attrs.get('perda_pacotes_pct', '—')} %"
            )

            net.add_edge(
                src_id, dst_id,
                title=title,
                color=cor,
                width=largura,
            )

    nome_alg_limpo = algoritmo.replace('*', 'star').replace(' ', '_').lower()
    nome_arquivo   = f"{nome_alg_limpo}_caminho.html"
    caminho_saida  = os.path.join(saida, nome_arquivo)
    net.save_graph(caminho_saida)
    return caminho_saida


def renderizar_base(grafo: Grafo, saida: str = 'results/graphs') -> str:
    """Gera visualização da topologia completa sem caminho destacado."""
    return renderizar(grafo, 'base', caminho=None, saida=saida)
