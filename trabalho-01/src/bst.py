# Benchmark de Árvores de Busca Binária — BST simples e AVL (auto-balanceada).
#
# Carrega registros de CSV inserindo cada um como nó na árvore (indexado por matrícula)
# e mede o desempenho de busca em cada estrutura:
#   - BST simples: inserção e busca em O(log n) médio, mas degrada para O(n) em dados ordenados.
#   - AVL: mantém balanceamento por rotações após cada inserção — garante O(log n) no pior caso.
#
# A busca percorre a árvore iterativamente comparando matrículas,
# contando um step por nó visitado.
#
# Métricas coletadas por rodada: tempo de execução, número de comparações (steps),
# memória RSS (psutil) e pico de memória Python (tracemalloc).
# Cada cenário executa 5 rodadas independentes; resultados salvos com média por volume.

import time
import psutil
import tracemalloc
import csv
import os


# =========================
# Data Container
# =========================
class BenchmarkData:
    def __init__(self, sizes):
        self.sizes = sizes
        self.time = {n: [] for n in sizes}
        self.steps = {n: [] for n in sizes}
        self.rss = {n: [] for n in sizes}
        self.peak = {n: [] for n in sizes}

    def record(self, n, t, steps, rss, peak):
        self.time[n].append(t)
        self.steps[n].append(steps)
        self.rss[n].append(rss)
        self.peak[n].append(peak)

    def mean(self, metric, n):
        values = getattr(self, metric)[n]
        return sum(values) / len(values)


# =========================
# Tree Data Structures
# =========================
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
            return
        self._insert(self.root, value)

    def _insert(self, node, value):
        if value["Mat"] < node.value["Mat"]:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert(node.right, value)


class AVLNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if not node:
            return AVLNode(value)
        if value["Mat"] < node.value["Mat"]:
            node.left = self._insert(node.left, value)
        else:
            node.right = self._insert(node.right, value)

        node.height = 1 + max(self._height(node.left), self._height(node.right))
        balance = self._height(node.left) - self._height(node.right)

        # LL
        if balance > 1 and value["Mat"] < node.left.value["Mat"]:
            return self._rotate_right(node)
        # RR
        if balance < -1 and value["Mat"] > node.right.value["Mat"]:
            return self._rotate_left(node)
        # LR
        if balance > 1 and value["Mat"] > node.left.value["Mat"]:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # RL
        if balance < -1 and value["Mat"] < node.right.value["Mat"]:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, z):
        y = z.right
        z.right = y.left
        y.left = z
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

    def _rotate_right(self, z):
        y = z.left
        z.left = y.right
        y.right = z
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

    def _height(self, node):
        return node.height if node else 0


# =========================
# CSV Loaders
# =========================
def load_tree(filename, tree_class):
    tree = tree_class()
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tree.insert({
                "Mat": int(row["Mat"]),
                "Name": row["Name"],
                "Sal": float(row["Sal"]),
                "CodSec": int(row["CodSec"])
            })
    return tree


def load_targets(filename):
    """Loads only Mat values to pick search targets (lightweight pass)."""
    mats = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mats.append(int(row["Mat"]))
    return mats


# =========================
# Search
# =========================
def search_tree(tree, target):
    steps = 0
    current = tree.root
    while current:
        steps += 1
        if current.value["Mat"] == target:
            return True, steps
        elif target < current.value["Mat"]:
            current = current.left
        else:
            current = current.right
    return False, steps


# =========================
# Benchmark Engine
# =========================
def run_benchmark(sizes, base_dir, tree_class):
    runs = 5
    data = BenchmarkData(sizes)

    for n in sizes:
        for k in range(1, runs + 1):
            file = f"{base_dir}/data_{n}_{k}.csv"

            # --- Preparation (NOT measured) ---
            mats = load_targets(file)
            targets = [
                mats[int(len(mats) * 0.2)],
                mats[int(len(mats) * 0.4)],
                mats[int(len(mats) * 0.6)],
                mats[int(len(mats) * 0.8)],
                mats[-1]
            ]
            tree = load_tree(file, tree_class)

            for target in targets:
                process = psutil.Process(os.getpid())
                tracemalloc.start()
                rss_before = process.memory_info().rss
                t0 = time.perf_counter()

                _, steps = search_tree(tree, target)

                t1 = time.perf_counter()
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rss_after = process.memory_info().rss

                data.record(
                    n,
                    t1 - t0,
                    steps,
                    (rss_after - rss_before) / 1024 / 1024,
                    peak / 1024 / 1024
                )

    return data


# =========================
# Save Results
# =========================
def save_results(data, filename):
    os.makedirs("results", exist_ok=True)
    with open(f"results/{filename}", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Size", "Time", "Steps", "RSS_Memory_MB", "Peak_Python_Memory_MB"])
        for n in data.sizes:
            for i in range(len(data.time[n])):
                writer.writerow([
                    n,
                    data.time[n][i],
                    data.steps[n][i],
                    data.rss[n][i],
                    data.peak[n][i]
                ])


# =========================
# Main
# =========================
if __name__ == "__main__":
    sizes = [10_000, 50_000, 100_000]
    base_dir = "data"

    bst_data = run_benchmark(sizes, base_dir, BinaryTree)
    save_results(bst_data, "Search-BST_random-sequence_results.csv")

    avl_data = run_benchmark(sizes, base_dir, AVLTree)
    save_results(avl_data, "Search-AVL_random-sequence_results.csv")
