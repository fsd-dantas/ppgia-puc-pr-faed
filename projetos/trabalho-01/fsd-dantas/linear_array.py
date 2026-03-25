"""
linear_array.py
---------------
Implementação de array linear com busca linear e busca binária.
Trabalho 01 – FAED/PPGIA-PUCPR.

Estrutura interna: lista Python (array dinâmico contíguo em memória).
Nenhuma biblioteca de estrutura de dados é utilizada — apenas stdlib
para medição de métricas (tracemalloc, psutil, time).

Complexidade esperada:
  - Inserção      : O(1) amortizado
  - Busca linear  : O(n)
  - Ordenação     : O(n log n) média (QuickSort)
  - Busca binária : O(log n)  [exige array ordenado]

Uso:
    arr = LinearArray()
    arr.inserir_todos(registros)
    resultado = arr.busca_linear(786579303)
    resultado = arr.busca_binaria(786579303)
"""

import os
import sys
import time
import tracemalloc
import psutil


# ---------------------------------------------------------------------------
# Estrutura principal
# ---------------------------------------------------------------------------

class LinearArray:
    """
    Array linear de registros indexado por 'matricula'.

    Atributos
    ---------
    _dados   : list — armazena os registros inseridos
    _ordenado: bool — True se o array foi ordenado após a última inserção
    """

    def __init__(self):
        self._dados:    list = []
        self._ordenado: bool = False

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------

    def inserir(self, registro: dict) -> int:
        """
        Insere um registro ao final do array.

        Parâmetros
        ----------
        registro : dict com chaves 'matricula', 'nome', 'salario', 'cod_setor'

        Retorno
        -------
        Número de operações realizadas (sempre 1 — append O(1) amortizado).
        """
        self._dados.append(registro)
        self._ordenado = False
        return 1

    def inserir_todos(self, registros: list[dict]) -> int:
        """
        Insere uma lista de registros. Retorna o total de operações.
        """
        ops = 0
        for r in registros:
            ops += self.inserir(r)
        return ops

    # ------------------------------------------------------------------
    # Ordenação interna (QuickSort iterativo — evita recursão profunda)
    # ------------------------------------------------------------------

    def _particionar(self, lo: int, hi: int) -> int:
        """
        Particiona self._dados[lo..hi] pelo pivô central.
        Retorna o índice final do pivô.
        """
        mid   = (lo + hi) // 2
        pivot = self._dados[mid]["matricula"]
        # Move pivô para o fim
        self._dados[mid], self._dados[hi] = self._dados[hi], self._dados[mid]
        i = lo
        for j in range(lo, hi):
            if self._dados[j]["matricula"] <= pivot:
                self._dados[i], self._dados[j] = self._dados[j], self._dados[i]
                i += 1
        self._dados[i], self._dados[hi] = self._dados[hi], self._dados[i]
        return i

    def ordenar(self) -> None:
        """
        Ordena o array por 'matricula' usando QuickSort iterativo.
        Necessário antes de qualquer busca binária.
        """
        if self._ordenado or len(self._dados) <= 1:
            self._ordenado = True
            return

        pilha = [(0, len(self._dados) - 1)]
        while pilha:
            lo, hi = pilha.pop()
            if lo < hi:
                p = self._particionar(lo, hi)
                pilha.append((lo, p - 1))
                pilha.append((p + 1, hi))

        self._ordenado = True

    # ------------------------------------------------------------------
    # Busca linear — O(n)
    # ------------------------------------------------------------------

    def busca_linear(self, matricula: int) -> dict:
        """
        Percorre o array do início ao fim procurando a matrícula.

        Retorno
        -------
        dict com:
          'indice'    : posição encontrada (-1 se não encontrado)
          'registro'  : dict do registro ou None
          'iteracoes' : número de comparações realizadas
        """
        iteracoes = 0
        for i, reg in enumerate(self._dados):
            iteracoes += 1
            if reg["matricula"] == matricula:
                return {"indice": i, "registro": reg, "iteracoes": iteracoes}
        return {"indice": -1, "registro": None, "iteracoes": iteracoes}

    # ------------------------------------------------------------------
    # Busca binária — O(log n)
    # ------------------------------------------------------------------

    def busca_binaria(self, matricula: int) -> dict:
        """
        Busca por divisão e conquista. Exige array ordenado.
        Chama self.ordenar() automaticamente se necessário.

        Retorno
        -------
        dict com:
          'indice'    : posição encontrada (-1 se não encontrado)
          'registro'  : dict do registro ou None
          'iteracoes' : número de comparações realizadas
        """
        if not self._ordenado:
            self.ordenar()

        lo, hi    = 0, len(self._dados) - 1
        iteracoes = 0

        while lo <= hi:
            mid = (lo + hi) // 2
            iteracoes += 1
            chave = self._dados[mid]["matricula"]
            if chave == matricula:
                return {"indice": mid, "registro": self._dados[mid], "iteracoes": iteracoes}
            elif chave < matricula:
                lo = mid + 1
            else:
                hi = mid - 1

        return {"indice": -1, "registro": None, "iteracoes": iteracoes}

    # ------------------------------------------------------------------
    # Propriedades utilitárias
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._dados)

    def esta_ordenado(self) -> bool:
        return self._ordenado


# ---------------------------------------------------------------------------
# Framework de benchmark
# ---------------------------------------------------------------------------

def _alvo_de_busca(registros: list[dict], fracao: float) -> int:
    """Retorna a matrícula do registro na posição fracao*n (0.0–1.0)."""
    idx = max(0, min(len(registros) - 1, int(fracao * len(registros))))
    return registros[idx]["matricula"]


def benchmark_insercao(registros: list[dict]) -> dict:
    """
    Mede o custo de inserção de todos os registros em um novo array.

    Métricas coletadas
    ------------------
    - tempo_s        : tempo total de inserção (perf_counter)
    - iteracoes      : total de operações de inserção (= n)
    - mem_pico_mb    : pico de memória Python (tracemalloc)
    - mem_rss_delta_mb: variação de memória RSS do processo (psutil)
    """
    proc = psutil.Process(os.getpid())

    tracemalloc.start()
    rss_antes = proc.memory_info().rss

    t0  = time.perf_counter()
    arr = LinearArray()
    ops = arr.inserir_todos(registros)
    t1  = time.perf_counter()

    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_depois = proc.memory_info().rss

    return {
        "n":               len(registros),
        "tempo_s":         t1 - t0,
        "iteracoes":       ops,
        "mem_pico_mb":     pico / 1_024 ** 2,
        "mem_rss_delta_mb":(rss_depois - rss_antes) / 1_024 ** 2,
    }


def benchmark_busca(registros: list[dict], metodo: str = "linear",
                    fracoes: list[float] = None) -> list[dict]:
    """
    Mede o custo de busca para alvos em diferentes posições do array.

    Parâmetros
    ----------
    registros : lista de registros (já carregada)
    metodo    : 'linear' ou 'binaria'
    fracoes   : posições relativas dos alvos (default: 20%, 40%, 60%, 80%, 100%)

    Retorno
    -------
    Lista de dicts, um por alvo buscado.
    """
    if fracoes is None:
        fracoes = [0.20, 0.40, 0.60, 0.80, 1.0]

    arr = LinearArray()
    arr.inserir_todos(registros)

    # Para busca binária, a ordenação é custo único — medido separadamente
    if metodo == "binaria":
        arr.ordenar()

    resultados = []
    proc = psutil.Process(os.getpid())
    fn   = arr.busca_binaria if metodo == "binaria" else arr.busca_linear

    for frac in fracoes:
        alvo = _alvo_de_busca(registros, frac)

        tracemalloc.start()
        rss_antes = proc.memory_info().rss

        t0  = time.perf_counter()
        res = fn(alvo)
        t1  = time.perf_counter()

        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rss_depois = proc.memory_info().rss

        resultados.append({
            "n":               len(registros),
            "metodo":          metodo,
            "fracao_alvo":     frac,
            "matricula_alvo":  alvo,
            "encontrado":      res["indice"] != -1,
            "iteracoes":       res["iteracoes"],
            "tempo_s":         t1 - t0,
            "mem_pico_mb":     pico / 1_024 ** 2,
            "mem_rss_delta_mb":(rss_depois - rss_antes) / 1_024 ** 2,
        })

    return resultados


def _estatisticas(valores: list[float]) -> dict:
    """Calcula média e desvio padrão de uma lista de floats."""
    n    = len(valores)
    med  = sum(valores) / n
    var  = sum((x - med) ** 2 for x in valores) / n
    return {"media": med, "desvio": var ** 0.5}


def executar_experimento(registros: list[dict], rodadas: int = 5) -> dict:
    """
    Executa *rodadas* independentes de inserção e busca (linear + binária).
    Retorna médias e desvios padrão de todas as métricas.

    Parâmetros
    ----------
    registros : lista de registros (mesma seed — dados idênticos por rodada)
    rodadas   : número de execuções independentes (mínimo recomendado: 5)
    """
    ins_tempo, ins_mem_pico, ins_mem_rss = [], [], []

    # Busca: coletamos por fração — usamos a fração 0.5 (meio) como resumo
    lin_iter, lin_tempo = [], []
    bin_iter, bin_tempo = [], []

    for rodada in range(1, rodadas + 1):
        print(f"  Rodada {rodada}/{rodadas}...", end=" ", flush=True)

        # Inserção
        r = benchmark_insercao(registros)
        ins_tempo.append(r["tempo_s"])
        ins_mem_pico.append(r["mem_pico_mb"])
        ins_mem_rss.append(r["mem_rss_delta_mb"])

        # Busca — alvo no meio do array (caso médio)
        rl = benchmark_busca(registros, metodo="linear",  fracoes=[0.5])
        rb = benchmark_busca(registros, metodo="binaria", fracoes=[0.5])
        lin_iter.append(rl[0]["iteracoes"])
        lin_tempo.append(rl[0]["tempo_s"])
        bin_iter.append(rb[0]["iteracoes"])
        bin_tempo.append(rb[0]["tempo_s"])

        print("ok")

    return {
        "n":       len(registros),
        "rodadas": rodadas,
        "insercao": {
            "tempo_s":         _estatisticas(ins_tempo),
            "mem_pico_mb":     _estatisticas(ins_mem_pico),
            "mem_rss_delta_mb":_estatisticas(ins_mem_rss),
        },
        "busca_linear": {
            "iteracoes": _estatisticas(lin_iter),
            "tempo_s":   _estatisticas(lin_tempo),
        },
        "busca_binaria": {
            "iteracoes": _estatisticas(bin_iter),
            "tempo_s":   _estatisticas(bin_tempo),
        },
    }


# ---------------------------------------------------------------------------
# Execução direta
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from datetime import datetime as _dt
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
    from data_generator import carregar_csv, gerar_registros

    from pathlib import Path

    VOLUMES  = [10_000, 50_000, 100_000]
    RODADAS  = 5
    PASTA    = Path(__file__).parent / "dados"

    _t0 = time.perf_counter()
    print("=" * 60)
    print("  Array Linear — Experimento completo")
    print(f"  Inicio : {_dt.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    for n in VOLUMES:
        csv_path = PASTA / f"registros_{n}.csv"

        # Carrega do CSV se existir, senão gera em memória
        if csv_path.exists():
            registros = carregar_csv(csv_path)
            fonte = f"CSV ({csv_path.name})"
        else:
            registros = gerar_registros(n)
            fonte = "gerado em memória (seed=42)"

        print(f"\nN = {n:,}  |  fonte: {fonte}")
        resultado = executar_experimento(registros, rodadas=RODADAS)

        r = resultado
        print(f"\n  {'Operação':<20} {'Métrica':<22} {'Média':>12}  {'Desvio':>12}")
        print(f"  {'-'*68}")

        def linha(op, metrica, stats):
            print(f"  {op:<20} {metrica:<22} {stats['media']:>12.6f}  {stats['desvio']:>12.6f}")

        linha("Inserção",      "tempo (s)",        r["insercao"]["tempo_s"])
        linha("Inserção",      "mem pico (MB)",     r["insercao"]["mem_pico_mb"])
        linha("Inserção",      "mem RSS delta (MB)",r["insercao"]["mem_rss_delta_mb"])
        linha("Busca linear",  "iterações",         r["busca_linear"]["iteracoes"])
        linha("Busca linear",  "tempo (s)",         r["busca_linear"]["tempo_s"])
        linha("Busca binária", "iterações",         r["busca_binaria"]["iteracoes"])
        linha("Busca binária", "tempo (s)",         r["busca_binaria"]["tempo_s"])

    print(f"\n{'-'*60}")
    print(f"  Fim    : {_dt.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Duracao: {time.perf_counter() - _t0:.2f}s")
    print(f"{'-'*60}")
