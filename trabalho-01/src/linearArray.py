# Benchmark de Array Linear — busca sequencial e busca binária.
#
# Carrega registros de CSV em um array Python (lista de dicts) e mede o desempenho
# de dois algoritmos de busca por matrícula:
#   - Busca sequencial: percorre o array elemento a elemento — O(n) no pior caso.
#   - Busca binária: requer array ordenado; divide o espaço de busca pela metade a cada passo — O(log n).
#     Para dados não ordenados, aplica Quick Sort antes da busca.
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
# CSV Loader
# =========================
def load_array(filename):
    arr = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            arr.append({
                "Mat": int(row["Mat"]),
                "Name": row["Name"],
                "Sal": float(row["Sal"]),
                "CodSec": int(row["CodSec"])
            })
    return arr


# =========================
# Algorithms
# =========================
def linear_search(arr, target):
    steps = 0
    for i, item in enumerate(arr):
        steps += 1
        if item['Mat'] == target:
            return i, steps
    return -1, steps


def binary_search(arr, target):
    steps = 0
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        steps += 1
        if arr[mid]['Mat'] == target:
            return mid, steps
        elif arr[mid]['Mat'] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, steps


# =========================
# Sorting (Preparation Only)
# =========================
def quick_sort(arr):
    def _sort(a, lo, hi):
        if lo >= hi:
            return
        pivot = a[(lo + hi) // 2]['Mat']
        i, j = lo, hi
        while i <= j:
            while a[i]['Mat'] < pivot:
                i += 1
            while a[j]['Mat'] > pivot:
                j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                i += 1
                j -= 1
        _sort(a, lo, j)
        _sort(a, i, hi)

    _sort(arr, 0, len(arr) - 1)


# =========================
# Benchmark Engine
# =========================
def run_benchmark(sizes, base_dir, search_type):
    runs = 5
    data = BenchmarkData(sizes)

    for n in sizes:
        for k in range(1, runs + 1):
            file = f"{base_dir}/data_{n}_{k}.csv"

            # --- Preparation (NOT measured) ---
            arr = load_array(file)

            if search_type == "binary":
                quick_sort(arr)

            # pick realistic targets
            targets = [
                arr[int(len(arr)*0.2)]['Mat'],
                arr[int(len(arr)*0.4)]['Mat'],
                arr[int(len(arr)*0.6)]['Mat'],
                arr[int(len(arr)*0.8)]['Mat'],
                arr[-1]['Mat']
            ]

            for target in targets:
                process = psutil.Process(os.getpid())

                tracemalloc.start()
                rss_before = process.memory_info().rss
                t0 = time.perf_counter()

                if search_type == "linear":
                    _, steps = linear_search(arr, target)
                else:
                    _, steps = binary_search(arr, target)

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

    linear_data = run_benchmark(sizes, base_dir, "linear")
    save_results(linear_data, "Search-values-in-CSV_random-sequence_results.csv")

    binary_data = run_benchmark(sizes, base_dir, "binary")
    save_results(binary_data, "Binary-Search-in-CSV_random-sequence_results.csv")
