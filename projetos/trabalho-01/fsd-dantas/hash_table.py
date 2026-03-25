"""
hash_table.py
-------------
Implementação de Tabela Hash com encadeamento externo (chaining).
Trabalho 01 – FAED/PPGIA-PUCPR.

Três funções hash avaliadas:
  1. Divisão     : h(k) = k mod M
  2. Multiplicação: h(k) = floor(M * frac(k * A)), A = (√5-1)/2  (Knuth)
  3. Dobramento   : soma blocos de 3 dígitos da chave, depois mod M

Tratamento de colisões: encadeamento externo (lista encadeada por balde).

Parâmetros de tamanho: M = {100, 1.000, 5.000}

Métricas coletadas:
  - Iterações de inserção e busca (comparações na cadeia)
  - Colisões (inserções em balde já ocupado)
  - Load factor: α = n / M
  - Comprimento máximo e médio das cadeias
  - Memória (tracemalloc) e tempo (perf_counter)

Complexidade:
  - Caso médio : O(1 + α)  para inserção e busca
  - Pior caso  : O(n)      (todas as chaves no mesmo balde)

Uso:
    ht = HashTable(m=1000, funcao="divisao")
    ht.inserir(registro)
    resultado = ht.buscar(786579303)
"""

import math
import os
import sys
import time
import tracemalloc
import psutil


# ---------------------------------------------------------------------------
# Constante de Knuth para função hash de multiplicação
# ---------------------------------------------------------------------------
_A_KNUTH = (math.sqrt(5) - 1) / 2   # ≈ 0.6180339887


# ---------------------------------------------------------------------------
# Nó da lista encadeada (cadeia de colisões)
# ---------------------------------------------------------------------------

class _No:
    __slots__ = ("chave", "registro", "prox")

    def __init__(self, registro: dict):
        self.chave    = registro["matricula"]
        self.registro = registro
        self.prox: "_No | None" = None


# ---------------------------------------------------------------------------
# Funções hash
# ---------------------------------------------------------------------------

def _hash_divisao(chave: int, m: int) -> int:
    """
    Método da divisão: h(k) = k mod m.
    Simples e eficiente. Sensível à escolha de m — evitar potências de 2.
    """
    return chave % m


def _hash_multiplicacao(chave: int, m: int) -> int:
    """
    Método da multiplicação (Knuth): h(k) = floor(m * frac(k * A)).
    Menos sensível ao valor de m; distribui bem em qualquer tamanho.
    """
    return int(m * ((chave * _A_KNUTH) % 1))


def _hash_dobramento(chave: int, m: int) -> int:
    """
    Método do dobramento: divide os dígitos da chave em blocos de 3,
    soma os blocos e aplica mod m.
    Indicado quando a chave tem muitos dígitos (e.g., matrícula de 9 dígitos).
    """
    s = str(chave)
    # Divide em grupos de 3 dígitos da direita para a esquerda
    total = 0
    while s:
        total += int(s[-3:])
        s = s[:-3]
    return total % m


_FUNCOES = {
    "divisao":       _hash_divisao,
    "multiplicacao": _hash_multiplicacao,
    "dobramento":    _hash_dobramento,
}


# ---------------------------------------------------------------------------
# Tabela Hash com encadeamento externo
# ---------------------------------------------------------------------------

class HashTable:
    """
    Tabela Hash com encadeamento externo (chaining).

    Parâmetros
    ----------
    m      : número de baldes (tamanho da tabela)
    funcao : 'divisao' | 'multiplicacao' | 'dobramento'
    """

    def __init__(self, m: int, funcao: str = "divisao"):
        if funcao not in _FUNCOES:
            raise ValueError(f"funcao deve ser uma de: {list(_FUNCOES)}")
        self._m:       int   = m
        self._fn_nome: str   = funcao
        self._fn             = _FUNCOES[funcao]
        self._tabela: list["_No | None"] = [None] * m
        self._n:       int   = 0   # total de elementos inseridos
        self._colisoes: int  = 0   # total de colisões acumuladas

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------

    def inserir(self, registro: dict) -> dict:
        """
        Insere um registro na tabela.

        Retorno
        -------
        dict com 'iteracoes' (comparações na cadeia) e 'colisao' (bool).
        """
        chave  = registro["matricula"]
        idx    = self._fn(chave, self._m)
        colisao    = self._tabela[idx] is not None
        iteracoes  = 0

        # Percorre a cadeia: atualiza se chave já existe
        atual = self._tabela[idx]
        while atual is not None:
            iteracoes += 1
            if atual.chave == chave:
                atual.registro = registro
                return {"iteracoes": iteracoes, "colisao": False}
            atual = atual.prox

        # Insere no início da cadeia (O(1))
        no_novo         = _No(registro)
        no_novo.prox    = self._tabela[idx]
        self._tabela[idx] = no_novo
        self._n += 1

        if colisao:
            self._colisoes += 1

        return {"iteracoes": iteracoes, "colisao": colisao}

    def inserir_todos(self, registros: list[dict]) -> dict:
        """
        Insere uma lista de registros.

        Retorno
        -------
        dict com 'total_iteracoes' e 'total_colisoes'.
        """
        total_iter = 0
        for r in registros:
            res = self.inserir(r)
            total_iter += res["iteracoes"]
        return {"total_iteracoes": total_iter, "total_colisoes": self._colisoes}

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------

    def buscar(self, matricula: int) -> dict:
        """
        Busca por matrícula na tabela.

        Retorno
        -------
        dict com 'registro' (ou None) e 'iteracoes'.
        """
        idx       = self._fn(matricula, self._m)
        atual     = self._tabela[idx]
        iteracoes = 0

        while atual is not None:
            iteracoes += 1
            if atual.chave == matricula:
                return {"registro": atual.registro, "iteracoes": iteracoes}
            atual = atual.prox

        return {"registro": None, "iteracoes": iteracoes}

    # ------------------------------------------------------------------
    # Métricas da tabela
    # ------------------------------------------------------------------

    def load_factor(self) -> float:
        """α = n / m  (fator de carga)."""
        return self._n / self._m

    def estatisticas_cadeias(self) -> dict:
        """
        Retorna comprimento máximo, médio e número de baldes vazios.
        Essencial para avaliar a qualidade da função hash.
        """
        comprimentos  = [0] * self._m
        for i, no in enumerate(self._tabela):
            c = 0
            while no is not None:
                c  += 1
                no  = no.prox
            comprimentos[i] = c

        vazios = sum(1 for c in comprimentos if c == 0)
        n_bal  = self._m - vazios or 1  # baldes não-vazios

        return {
            "max_cadeia":    max(comprimentos),
            "media_cadeia":  sum(comprimentos) / self._m,
            "baldes_vazios": vazios,
            "load_factor":   self.load_factor(),
            "colisoes":      self._colisoes,
        }

    def __len__(self) -> int:
        return self._n


# ---------------------------------------------------------------------------
# Framework de benchmark
# ---------------------------------------------------------------------------

def _alvo_de_busca(registros: list[dict], fracao: float) -> int:
    idx = max(0, min(len(registros) - 1, int(fracao * len(registros))))
    return registros[idx]["matricula"]


def benchmark_insercao(registros: list[dict], m: int, funcao: str) -> dict:
    """Mede custo de inserção de todos os registros em uma tabela nova."""
    proc = psutil.Process(os.getpid())

    tracemalloc.start()
    rss_antes = proc.memory_info().rss

    t0  = time.perf_counter()
    ht  = HashTable(m=m, funcao=funcao)
    res = ht.inserir_todos(registros)
    t1  = time.perf_counter()

    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_depois = proc.memory_info().rss

    stats = ht.estatisticas_cadeias()

    return {
        "n":                len(registros),
        "m":                m,
        "funcao":           funcao,
        "tempo_s":          t1 - t0,
        "total_iteracoes":  res["total_iteracoes"],
        "colisoes":         stats["colisoes"],
        "load_factor":      stats["load_factor"],
        "max_cadeia":       stats["max_cadeia"],
        "media_cadeia":     stats["media_cadeia"],
        "baldes_vazios":    stats["baldes_vazios"],
        "mem_pico_mb":      pico / 1_024 ** 2,
        "mem_rss_delta_mb": (rss_depois - rss_antes) / 1_024 ** 2,
    }


def benchmark_busca(registros: list[dict], m: int, funcao: str,
                    fracoes: list[float] = None) -> list[dict]:
    """Constrói a tabela uma vez e mede buscas em diferentes posições."""
    if fracoes is None:
        fracoes = [0.20, 0.40, 0.60, 0.80, 1.0]

    ht = HashTable(m=m, funcao=funcao)
    ht.inserir_todos(registros)

    resultados = []
    proc = psutil.Process(os.getpid())

    for frac in fracoes:
        alvo = _alvo_de_busca(registros, frac)

        tracemalloc.start()
        rss_antes = proc.memory_info().rss

        t0  = time.perf_counter()
        res = ht.buscar(alvo)
        t1  = time.perf_counter()

        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rss_depois = proc.memory_info().rss

        resultados.append({
            "n":               len(registros),
            "m":               m,
            "funcao":          funcao,
            "fracao_alvo":     frac,
            "encontrado":      res["registro"] is not None,
            "iteracoes":       res["iteracoes"],
            "tempo_s":         t1 - t0,
            "mem_pico_mb":     pico / 1_024 ** 2,
            "mem_rss_delta_mb":(rss_depois - rss_antes) / 1_024 ** 2,
        })

    return resultados


def _estatisticas(valores: list[float]) -> dict:
    n   = len(valores)
    med = sum(valores) / n
    var = sum((x - med) ** 2 for x in valores) / n
    return {"media": med, "desvio": var ** 0.5}


def executar_experimento(registros: list[dict], m: int, funcao: str,
                         rodadas: int = 5) -> dict:
    """Executa *rodadas* independentes e retorna médias e desvios."""
    ins_tempo, ins_col, ins_lf, ins_max_cad = [], [], [], []
    bus_iter,  bus_tempo                    = [], []

    for rodada in range(1, rodadas + 1):
        print(f"  [M={m:<5} fn={funcao:<14}] Rodada {rodada}/{rodadas}...",
              end=" ", flush=True)

        ri = benchmark_insercao(registros, m, funcao)
        ins_tempo.append(ri["tempo_s"])
        ins_col.append(float(ri["colisoes"]))
        ins_lf.append(ri["load_factor"])
        ins_max_cad.append(float(ri["max_cadeia"]))

        rb = benchmark_busca(registros, m, funcao, fracoes=[0.5])
        bus_iter.append(rb[0]["iteracoes"])
        bus_tempo.append(rb[0]["tempo_s"])

        print("ok")

    return {
        "n":       len(registros),
        "m":       m,
        "funcao":  funcao,
        "rodadas": rodadas,
        "insercao": {
            "tempo_s":    _estatisticas(ins_tempo),
            "colisoes":   _estatisticas(ins_col),
            "load_factor":_estatisticas(ins_lf),
            "max_cadeia": _estatisticas(ins_max_cad),
        },
        "busca": {
            "iteracoes": _estatisticas(bus_iter),
            "tempo_s":   _estatisticas(bus_tempo),
        },
    }


# ---------------------------------------------------------------------------
# Execução direta
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
    from data_generator import carregar_csv, gerar_registros
    from pathlib import Path

    VOLUMES = [10_000, 50_000, 100_000]
    TAMANHOS_M = [100, 1_000, 5_000]
    FUNCOES    = ["divisao", "multiplicacao", "dobramento"]
    RODADAS    = 5
    PASTA      = Path(__file__).parent / "dados"

    print("=" * 70)
    print("  Tabela Hash — Experimento completo")
    print("=" * 70)

    for n in VOLUMES:
        csv_path  = PASTA / f"registros_{n}.csv"
        registros = (carregar_csv(csv_path) if csv_path.exists()
                     else gerar_registros(n))

        print(f"\n{'-'*70}")
        print(f"  N = {n:,}")
        print(f"{'-'*70}")

        # Cabeçalho da tabela de resultados
        print(f"\n  {'M':<6} {'Funcao':<15} {'Load(a)':<10} "
              f"{'Colisoes':<10} {'Max cad.':<10} "
              f"{'Iter. busca':<13} {'Tempo ins.(s)':<15}")
        print(f"  {'-'*79}")

        for m in TAMANHOS_M:
            for funcao in FUNCOES:
                r = executar_experimento(registros, m, funcao, RODADAS)
                print(
                    f"  {m:<6} {funcao:<15} "
                    f"{r['insercao']['load_factor']['media']:<10.2f}"
                    f"{r['insercao']['colisoes']['media']:<10.0f}"
                    f"{r['insercao']['max_cadeia']['media']:<10.0f}"
                    f"{r['busca']['iteracoes']['media']:<13.2f}"
                    f"{r['insercao']['tempo_s']['media']:.6f}"
                )
