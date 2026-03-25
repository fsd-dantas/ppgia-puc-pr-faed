"""
bst.py
------
Implementação de Árvore de Busca Binária (BST) sem e com balanceamento AVL.
Trabalho 01 – FAED/PPGIA-PUCPR.

Complexidade esperada:
  BST (sem balanceamento):
    - Inserção : O(log n) médio  |  O(n) pior caso (dados ordenados)
    - Busca    : O(log n) médio  |  O(n) pior caso

  AVL (com balanceamento):
    - Inserção : O(log n) garantido
    - Busca    : O(log n) garantido
    - Fator de balanço mantido em {-1, 0, 1} por rotações

Uso:
    from bst import BST, AVL

    bst = BST()
    bst.inserir(registro)
    resultado = bst.buscar(786579303)

    avl = AVL()
    avl.inserir(registro)
    resultado = avl.buscar(786579303)
"""

import os
import sys
import time
import tracemalloc
import psutil


# ---------------------------------------------------------------------------
# BST — Árvore de Busca Binária (sem balanceamento)
# ---------------------------------------------------------------------------

class _NoBST:
    """Nó interno da BST."""
    __slots__ = ("chave", "registro", "esq", "dir")

    def __init__(self, registro: dict):
        self.chave    = registro["matricula"]
        self.registro = registro
        self.esq:  "_NoBST | None" = None
        self.dir:  "_NoBST | None" = None


class BST:
    """
    Árvore de Busca Binária sem balanceamento automático.

    A chave de ordenação é 'matricula' (inteiro de 9 dígitos).
    Inserções em ordem crescente ou decrescente degeneram a árvore
    em lista encadeada — pior caso O(n).
    """

    def __init__(self):
        self._raiz: "_NoBST | None" = None
        self._tamanho: int = 0

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------

    def inserir(self, registro: dict) -> int:
        """
        Insere um registro na BST.

        Retorno
        -------
        Número de comparações realizadas até encontrar a posição de inserção.
        """
        iteracoes = 0
        no_novo   = _NoBST(registro)

        if self._raiz is None:
            self._raiz = no_novo
            self._tamanho += 1
            return 1

        atual = self._raiz
        while True:
            iteracoes += 1
            if registro["matricula"] < atual.chave:
                if atual.esq is None:
                    atual.esq = no_novo
                    break
                atual = atual.esq
            elif registro["matricula"] > atual.chave:
                if atual.dir is None:
                    atual.dir = no_novo
                    break
                atual = atual.dir
            else:
                # Chave duplicada: atualiza registro
                atual.registro = registro
                return iteracoes

        self._tamanho += 1
        return iteracoes

    def inserir_todos(self, registros: list[dict]) -> int:
        """Insere uma lista de registros. Retorna total de comparações."""
        total = 0
        for r in registros:
            total += self.inserir(r)
        return total

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------

    def buscar(self, matricula: int) -> dict:
        """
        Busca por matrícula na BST.

        Retorno
        -------
        dict com 'registro' (ou None) e 'iteracoes'.
        """
        atual     = self._raiz
        iteracoes = 0

        while atual is not None:
            iteracoes += 1
            if matricula == atual.chave:
                return {"registro": atual.registro, "iteracoes": iteracoes}
            elif matricula < atual.chave:
                atual = atual.esq
            else:
                atual = atual.dir

        return {"registro": None, "iteracoes": iteracoes}

    # ------------------------------------------------------------------
    # Propriedades da árvore
    # ------------------------------------------------------------------

    def altura(self) -> int:
        """Altura da árvore (nó raiz = nível 0). O(n)."""
        def _h(no):
            if no is None:
                return -1
            return 1 + max(_h(no.esq), _h(no.dir))
        return _h(self._raiz)

    def __len__(self) -> int:
        return self._tamanho


# ---------------------------------------------------------------------------
# AVL — Árvore de Busca Binária com balanceamento AVL
# ---------------------------------------------------------------------------

class _NoAVL:
    """Nó interno da AVL — armazena a altura para cálculo do fator de balanço."""
    __slots__ = ("chave", "registro", "esq", "dir", "altura")

    def __init__(self, registro: dict):
        self.chave    = registro["matricula"]
        self.registro = registro
        self.esq:   "_NoAVL | None" = None
        self.dir:   "_NoAVL | None" = None
        self.altura = 0


def _altura_avl(no: "_NoAVL | None") -> int:
    return no.altura if no is not None else -1


def _atualizar_altura(no: "_NoAVL") -> None:
    no.altura = 1 + max(_altura_avl(no.esq), _altura_avl(no.dir))


def _fator_balanco(no: "_NoAVL | None") -> int:
    if no is None:
        return 0
    return _altura_avl(no.esq) - _altura_avl(no.dir)


# Rotações elementares -------------------------------------------------------

def _rotacao_direita(y: "_NoAVL") -> "_NoAVL":
    """Rotação simples à direita em torno de y."""
    x    = y.esq
    t2   = x.dir
    x.dir = y
    y.esq = t2
    _atualizar_altura(y)
    _atualizar_altura(x)
    return x


def _rotacao_esquerda(x: "_NoAVL") -> "_NoAVL":
    """Rotação simples à esquerda em torno de x."""
    y    = x.dir
    t2   = y.esq
    y.esq = x
    x.dir = t2
    _atualizar_altura(x)
    _atualizar_altura(y)
    return y


def _balancear(no: "_NoAVL") -> "_NoAVL":
    """
    Aplica a rotação adequada para restaurar a propriedade AVL após inserção.
    Retorna o novo nó raiz da subárvore.
    """
    _atualizar_altura(no)
    fb = _fator_balanco(no)

    # Caso Esquerda-Esquerda
    if fb > 1 and _fator_balanco(no.esq) >= 0:
        return _rotacao_direita(no)

    # Caso Esquerda-Direita
    if fb > 1 and _fator_balanco(no.esq) < 0:
        no.esq = _rotacao_esquerda(no.esq)
        return _rotacao_direita(no)

    # Caso Direita-Direita
    if fb < -1 and _fator_balanco(no.dir) <= 0:
        return _rotacao_esquerda(no)

    # Caso Direita-Esquerda
    if fb < -1 and _fator_balanco(no.dir) > 0:
        no.dir = _rotacao_direita(no.dir)
        return _rotacao_esquerda(no)

    return no  # já balanceado


class AVL:
    """
    Árvore AVL — BST com balanceamento automático.

    Garante que |fator_balanço| <= 1 em todo nó após cada inserção,
    mantendo altura O(log n) independentemente da ordem de inserção.
    """

    def __init__(self):
        self._raiz: "_NoAVL | None" = None
        self._tamanho: int = 0

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------

    def _inserir_no(self, no: "_NoAVL | None",
                    registro: dict,
                    contador: list) -> "_NoAVL":
        """Inserção recursiva com balanceamento. contador[0] acumula comparações."""
        if no is None:
            self._tamanho += 1
            return _NoAVL(registro)

        contador[0] += 1
        chave = registro["matricula"]

        if chave < no.chave:
            no.esq = self._inserir_no(no.esq, registro, contador)
        elif chave > no.chave:
            no.dir = self._inserir_no(no.dir, registro, contador)
        else:
            no.registro = registro  # atualiza duplicata
            return no

        return _balancear(no)

    def inserir(self, registro: dict) -> int:
        """
        Insere um registro na AVL com rebalanceamento automático.

        Retorno
        -------
        Número de comparações realizadas.
        """
        contador = [0]
        self._raiz = self._inserir_no(self._raiz, registro, contador)
        return contador[0]

    def inserir_todos(self, registros: list[dict]) -> int:
        """Insere uma lista de registros. Retorna total de comparações."""
        total = 0
        for r in registros:
            total += self.inserir(r)
        return total

    # ------------------------------------------------------------------
    # Busca (iterativa — idêntica à BST após balanceamento)
    # ------------------------------------------------------------------

    def buscar(self, matricula: int) -> dict:
        """
        Busca por matrícula na AVL.

        Retorno
        -------
        dict com 'registro' (ou None) e 'iteracoes'.
        """
        atual     = self._raiz
        iteracoes = 0

        while atual is not None:
            iteracoes += 1
            if matricula == atual.chave:
                return {"registro": atual.registro, "iteracoes": iteracoes}
            elif matricula < atual.chave:
                atual = atual.esq
            else:
                atual = atual.dir

        return {"registro": None, "iteracoes": iteracoes}

    # ------------------------------------------------------------------
    # Propriedades
    # ------------------------------------------------------------------

    def altura(self) -> int:
        return _altura_avl(self._raiz)

    def __len__(self) -> int:
        return self._tamanho


# ---------------------------------------------------------------------------
# Framework de benchmark (espelha linear_array.py)
# ---------------------------------------------------------------------------

def _alvo_de_busca(registros: list[dict], fracao: float) -> int:
    idx = max(0, min(len(registros) - 1, int(fracao * len(registros))))
    return registros[idx]["matricula"]


def benchmark_insercao(registros: list[dict], classe) -> dict:
    """
    Mede custo de inserção de todos os registros em uma árvore nova.

    Parâmetros
    ----------
    classe : BST ou AVL
    """
    proc = psutil.Process(os.getpid())

    tracemalloc.start()
    rss_antes = proc.memory_info().rss

    t0   = time.perf_counter()
    arv  = classe()
    ops  = arv.inserir_todos(registros)
    t1   = time.perf_counter()
    alt  = arv.altura()

    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_depois = proc.memory_info().rss

    return {
        "n":               len(registros),
        "tempo_s":         t1 - t0,
        "iteracoes":       ops,
        "altura":          alt,
        "mem_pico_mb":     pico / 1_024 ** 2,
        "mem_rss_delta_mb":(rss_depois - rss_antes) / 1_024 ** 2,
    }


def benchmark_busca(registros: list[dict], classe,
                    fracoes: list[float] = None) -> list[dict]:
    """
    Constrói a árvore uma vez e mede buscas em diferentes posições.
    """
    if fracoes is None:
        fracoes = [0.20, 0.40, 0.60, 0.80, 1.0]

    arv = classe()
    arv.inserir_todos(registros)

    resultados = []
    proc = psutil.Process(os.getpid())

    for frac in fracoes:
        alvo = _alvo_de_busca(registros, frac)

        tracemalloc.start()
        rss_antes = proc.memory_info().rss

        t0  = time.perf_counter()
        res = arv.buscar(alvo)
        t1  = time.perf_counter()

        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rss_depois = proc.memory_info().rss

        resultados.append({
            "n":               len(registros),
            "estrutura":       classe.__name__,
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


def executar_experimento(registros: list[dict],
                         classe,
                         rodadas: int = 5) -> dict:
    """
    Executa *rodadas* independentes de inserção e busca.
    """
    ins_tempo, ins_mem_pico, ins_altura = [], [], []
    bus_iter,  bus_tempo               = [], []

    for rodada in range(1, rodadas + 1):
        print(f"  [{classe.__name__}] Rodada {rodada}/{rodadas}...",
              end=" ", flush=True)

        ri = benchmark_insercao(registros, classe)
        ins_tempo.append(ri["tempo_s"])
        ins_mem_pico.append(ri["mem_pico_mb"])
        ins_altura.append(float(ri["altura"]))

        rb = benchmark_busca(registros, classe, fracoes=[0.5])
        bus_iter.append(rb[0]["iteracoes"])
        bus_tempo.append(rb[0]["tempo_s"])

        print("ok")

    return {
        "n":        len(registros),
        "estrutura": classe.__name__,
        "rodadas":  rodadas,
        "insercao": {
            "tempo_s":     _estatisticas(ins_tempo),
            "mem_pico_mb": _estatisticas(ins_mem_pico),
            "altura":      _estatisticas(ins_altura),
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
    from datetime import datetime as _dt
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
    from data_generator import carregar_csv, gerar_registros
    from pathlib import Path

    VOLUMES = [10_000, 50_000, 100_000]
    RODADAS = 5
    PASTA   = Path(__file__).parent / "dados"

    _t0 = time.perf_counter()
    print("=" * 65)
    print("  BST vs AVL — Experimento completo")
    print(f"  Inicio : {_dt.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 65)

    for n in VOLUMES:
        csv_path = PASTA / f"registros_{n}.csv"
        registros = (carregar_csv(csv_path) if csv_path.exists()
                     else gerar_registros(n))

        print(f"\nN = {n:,}")

        for classe in (BST, AVL):
            resultado = executar_experimento(registros, classe, RODADAS)
            r = resultado

            print(f"\n  {'Operação':<20} {'Métrica':<22} {'Média':>12}  {'Desvio':>12}")
            print(f"  {'-'*70}")

            def linha(op, metrica, stats):
                print(f"  {op:<20} {metrica:<22} "
                      f"{stats['media']:>12.6f}  {stats['desvio']:>12.6f}")

            linha(f"Inserção ({classe.__name__})", "tempo (s)",
                  r["insercao"]["tempo_s"])
            linha(f"Inserção ({classe.__name__})", "altura",
                  r["insercao"]["altura"])
            linha(f"Inserção ({classe.__name__})", "mem pico (MB)",
                  r["insercao"]["mem_pico_mb"])
            linha(f"Busca ({classe.__name__})",    "iterações",
                  r["busca"]["iteracoes"])
            linha(f"Busca ({classe.__name__})",    "tempo (s)",
                  r["busca"]["tempo_s"])

    print(f"\n{'-'*65}")
    print(f"  Fim    : {_dt.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Duracao: {time.perf_counter() - _t0:.2f}s")
    print(f"{'-'*65}")
