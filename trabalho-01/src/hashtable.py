# Benchmark de Tabela Hash com encadeamento exterior (chaining).
#
# Implementa uma hash table de tamanho fixo M onde colisões são resolvidas por
# lista encadeada em cada bucket. Testa três funções de hash:
#   - Divisão:       h(k) = k mod M
#   - Multiplicação: h(k) = floor(M * frac(k * A)),  A = (sqrt(5)-1)/2  (constante de Knuth)
#   - Folding:       h(k) = soma de grupos de 2 dígitos da chave, mod M
#
# Para cada combinação de (função hash × tamanho M × volume N), mede a busca
# contando steps como número de elementos percorridos na cadeia do bucket alvo.
# Registra também o load factor (N/M) e o número de colisões ocorridas na inserção.
#
# Métricas coletadas por rodada: tempo de execução, steps (comparações na cadeia),
# memória RSS (psutil), pico de memória Python (tracemalloc), load factor e colisões.
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
        self.load_factor = {n: [] for n in sizes}
        self.collisions = {n: [] for n in sizes}

    def record(self, n, t, steps, rss, peak, load_factor, collisions):
        self.time[n].append(t)
        self.steps[n].append(steps)
        self.rss[n].append(rss)
        self.peak[n].append(peak)
        self.load_factor[n].append(load_factor)
        self.collisions[n].append(collisions)

    def mean(self, metric, n):
        values = getattr(self, metric)[n]
        return sum(values) / len(values)


# =========================
# Hash Table
# =========================
class HashTable:
    def __init__(self, size, hash_fn):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.hash_fn = hash_fn
        self.count = 0
        self.collisions = 0

    def insert(self, record):
        index = self.hash_fn(record['Mat'], self.size)
        if len(self.table[index]) > 0:
            self.collisions += 1
        if record not in self.table[index]:
            self.table[index].append(record)
            self.count += 1

    def search(self, key):
        index = self.hash_fn(key, self.size)
        steps = 0
        for record in self.table[index]:
            steps += 1
            if record['Mat'] == key:
                return True, steps
        return False, steps

    def get_load_factor(self):
        return self.count / self.size


# =========================
# Hash Functions
# =========================
def hash_division(key, size):
    return key % size

def hash_multiplication(key, size):
    A = 0.6180339887  # constante de Knuth
    return int(size * ((key * A) % 1))

def hash_folding(key, size):
    key_str = str(key)
    parts = [int(key_str[i:i+2]) for i in range(0, len(key_str), 2)]
    return sum(parts) % size


# =========================
# CSV Loaders
# =========================
def load_hash_table(filename, hash_fn, size):
    ht = HashTable(size, hash_fn)
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ht.insert({
                "Mat": int(row["Mat"]),
                "Name": row["Name"],
                "Sal": float(row["Sal"]),
                "CodSec": int(row["CodSec"])
            })
    return ht


def load_targets(filename):
    """Loads only Mat values to pick search targets (lightweight pass)."""
    mats = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mats.append(int(row["Mat"]))
    return mats


# =========================
# Benchmark Engine
# =========================
def run_benchmark(sizes, base_dir, hash_fn, table_size):
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
            ht = load_hash_table(file, hash_fn, table_size)

            for target in targets:
                process = psutil.Process(os.getpid())
                tracemalloc.start()
                rss_before = process.memory_info().rss
                t0 = time.perf_counter()

                _, steps = ht.search(target)

                t1 = time.perf_counter()
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rss_after = process.memory_info().rss

                data.record(
                    n,
                    t1 - t0,
                    steps,
                    (rss_after - rss_before) / 1024 / 1024,
                    peak / 1024 / 1024,
                    ht.get_load_factor(),
                    ht.collisions
                )

    return data


# =========================
# Save Results
# =========================
def save_results(data, filename):
    os.makedirs("results", exist_ok=True)
    with open(f"results/{filename}", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Size", "Time", "Steps", "RSS_Memory_MB", "Peak_Python_Memory_MB", "Load_Factor", "Collisions"])
        for n in data.sizes:
            for i in range(len(data.time[n])):
                writer.writerow([
                    n,
                    data.time[n][i],
                    data.steps[n][i],
                    data.rss[n][i],
                    data.peak[n][i],
                    data.load_factor[n][i],
                    data.collisions[n][i]
                ])


# =========================
# Main
# =========================
if __name__ == "__main__":
    sizes = [10_000, 50_000, 100_000]
    base_dir = "data"
    # Tamanhos M da tabela hash (conforme enunciado: 100, 1.000, 5.000)
    table_sizes = [100, 1_000, 5_000]

    hash_functions = {
        "Divisao": hash_division,
        "Multiplicacao": hash_multiplication,
        "Folding": hash_folding,
    }

    for fn_name, fn in hash_functions.items():
        for m in table_sizes:
            data = run_benchmark(sizes, base_dir, fn, m)
            save_results(data, f"Search-Hash-({fn_name})_size{m}_random-sequence_results.csv")
