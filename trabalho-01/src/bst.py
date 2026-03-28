# Benchmark de Árvores de Busca Binária — BST simples e AVL (auto-balanceada).
#
# Carrega registros de CSV inserindo cada um como nó na árvore (indexado por matrícula)
# e mede o desempenho de inserção e busca:
#   - BST simples: inserção e busca em O(log n) médio, mas degrada para O(n) em dados ordenados.
#   - AVL: mantém balanceamento por rotações após cada inserção — garante O(log n) no pior caso.
#
# A busca utiliza comparação de matrículas descendo a árvore iterativamente,
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

# Classe para armazenar os dados dos testes ----------------------------------
class bruteData():
    def __init__(self, num_records):
        self.time = []
        self.step = []
        self.size = []
        self.rss_memory = []
        self.peak_python_memory = []
        for _ in range(len(num_records)):
            self.time.append([])
            self.step.append([])
            self.size.append([])
            self.rss_memory.append([])
            self.peak_python_memory.append([])

    def sizeMean(self, idx_of_num_records):
        temp = 0
        for x in self.size[idx_of_num_records]:
            temp+=x
        return (temp/len(self.size[idx_of_num_records]))

    def timeMean(self, idx_of_num_records):
        temp = 0
        for x in self.time[idx_of_num_records]:
            temp+=x
        return (temp/len(self.time[idx_of_num_records]))
    
    def stepMean(self, idx_of_num_records):
        temp = 0
        for x in self.step[idx_of_num_records]:
            temp+=x
        return (temp/len(self.step[idx_of_num_records]))
    
    def rssMemoryMean(self, idx_of_num_records):
        temp = 0
        for x in self.rss_memory[idx_of_num_records]:
            temp+=x
        return (temp/len(self.rss_memory[idx_of_num_records]))
    
    def peakPythonMemoryMean(self, idx_of_num_records):
        temp = 0
        for x in self.peak_python_memory[idx_of_num_records]:
            temp+=x
        return (temp/len(self.peak_python_memory[idx_of_num_records]))

    def sizesToPlot(self):
        temp = []
        for i in range(len(data.size)):
            temp.append(self.sizeMean(i))
        return temp

    def timesToPlot(self):
        temp = []
        for i in range(len(data.time)):
            temp.append(self.timeMean(i))
        return temp
    
    def stepsToPlot(self):
        temp = []
        for i in range(len(data.step)):
            temp.append(self.stepMean(i))
        return temp
    
    def rssMemoryToPlot(self):
        temp = []
        for i in range(len(data.rss_memory)):
            temp.append(self.rssMemoryMean(i))
        return temp
    
    def peakPythonMemoryToPlot(self):
        temp = []
        for i in range(len(data.peak_python_memory)):
            temp.append(self.peakPythonMemoryMean(i))
        return temp
        
    def __str__(self):
        temp = "\nData Aquired\n"
        temp+= "Time:\n"
        for i in range(len(self.time)):
            temp+=f"     {i}:"
            temp+=str(self.time[i])
            temp+="\n"
        temp+= "Steps:\n"
        for i in range(len(self.step)):
            temp+=f"     {i}:"
            temp+=str(self.step[i])
            temp+="\n"
        temp+= "Size:\n"
        for i in range(len(self.size)):
            temp+=f"     {i}:"
            temp+=str(self.size[i])
            temp+="\n"

        return temp

# Classe das Estruturas de Dados ---------------------------------------------
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

    def searchMat(self, value):
        return self._search(self.root, value)

    def _search(self, node, value):
        if node is None:
            return False
        if node.value["Mat"] == value:
            return True
        elif value < node.value["Mat"]:
            return self._search(node.left, value)
        else:
            return self._search(node.right, value)

    def in_order(self):
        self._in_order(self.root)

    def _in_order(self, node):
        if node:
            self._in_order(node.left)
            print(node.value)
            self._in_order(node.right)

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

        # Atualiza altura
        node.height = 1 + max(self._get_height(node.left),
                              self._get_height(node.right))

        # Fator de balanceamento
        balance = self._get_balance(node)

        # Casos de rotação

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
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self._get_height(z.left),
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left),
                           self._get_height(y.right))

        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self._get_height(z.left),
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left),
                           self._get_height(y.right))

        return y

    def _get_height(self, node):
        if not node:
            return 0
        return node.height

    def _get_balance(self, node):
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def in_order(self):
        self._in_order(self.root)

    def _in_order(self, node):
        if node:
            self._in_order(node.left)
            print(node.value)
            self._in_order(node.right)

    def searchMat(self, value):
        return self._search(self.root, value)

    def _search(self, node, value):
        if node is None:
            return False
        if node.value["Mat"] == value:
            return True
        elif value < node.value["Mat"]:
            return self._search(node.left, value)
        else:
            return self._search(node.right, value)

# Funções para ler os dados do CSV e realizar os testes ----------------------
def read_csv_to_bst(filename, steps):
    header = []
    bst = BinaryTree()
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "Mat":
                for x in row:
                    header.append(x)
                continue
            bst.insert({header[0]: int(row[0]), header[1]: row[1], header[2]: float(row[2]), header[3]: int(row[3])})
            steps+=1
    return bst, steps

def read_csv_to_avl(filename, steps):
    header = []
    avl = AVLTree()
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "Mat":
                for x in row:
                    header.append(x)
                continue
            avl.insert({header[0]: int(row[0]), header[1]: row[1], header[2]: float(row[2]), header[3]: int(row[3])})
            steps+=1
    return avl, steps

# Funçoes para busca em BST e AVL --------------------------------------------
def search_bst(bst, value, steps):
    current = bst.root
    while current:
        steps+=1
        if current.value["Mat"] == value:
            return True, steps
        elif value < current.value["Mat"]:
            current = current.left
        else:
            current = current.right
    return False, steps

def search_avl(avl, value, steps):
    current = avl.root
    while current:
        steps+=1
        if current.value["Mat"] == value:
            return True, steps
        elif value < current.value["Mat"]:
            current = current.left
        else:
            current = current.right
    return False, steps

# Funções para gerar dados de busca a partir dos CSVs --------------------------------------
def read_csv_to_array(filename):
    arr = []
    header = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "Mat":
                for x in row:
                    header.append(x)
                continue
            arr.append({header[0]: int(row[0]), header[1]: row[1], header[2]: float(row[2]), header[3]: int(row[3])})
    return arr

def getSearchArray(number_of_tests, total_records, dir):
    searchArr = []
    idx0 = 1/number_of_tests
    for j in range(number_of_tests):
        # print(j+1)
        # print((idx0 * (j+1)))
        # print(round(total_records * (idx0 * (j+1)))-1)
        arr = read_csv_to_array(f'{dir}/data_{total_records}_{j+1}.csv')
        searchArr.append(arr[round(total_records * (idx0 * (j+1)))-1]['Mat'])
    return searchArr
    
# Função para realizar os testes e coletar os dados
def funcTest(data, num_records, func, funcName, dir, type):
    number_of_tests = 5
    
    print(f"Starting Test {funcName}")
    # FOR EVERY NUM_RECORDS
    for i in range(len(num_records)):
        # TEST  DIFERENT DATASETS x TIMES TO GET A MEAN
        print(f"Starting Test with {num_records[i]} samples...")
        if "search" in type.lower():
            # Gerar um array de valores para busca, com base nos valores dos CSVs
            searchArr = getSearchArray(number_of_tests,num_records[i], dir)

        for j in range(number_of_tests):
            print(f"    Starting Test {j+1}...")

            # Deixa dados carregados para busca em BST e AVL
            if "search" in type.lower():
                if "bst" in type.lower():
                    tree,_ = read_csv_to_bst(f'{dir}/data_{num_records[i]}_{j+1}.csv', 0)
                elif "avl" in type.lower():
                    tree,_ = read_csv_to_avl(f'{dir}/data_{num_records[i]}_{j+1}.csv', 0)
            
            # MEASURES START -------------------------------
            tempSteps = 0
            process = psutil.Process(os.getpid())

            tracemalloc.start()

            rss_before = process.memory_info().rss
            t0 = time.perf_counter()
            # MEASURES START -------------------------------
            
            # Executa a função de teste de acordo com o tipo
            if type.lower() == "load":
                tree, tempSteps = func(f'{dir}/data_{num_records[i]}_{j+1}.csv', tempSteps)
            elif "search" in type.lower():
                response, tempSteps = func(tree, searchArr[j], tempSteps)
            else:
                tree = None
                tempSteps = -1

            # MEASURES END ---------------------------------
            t1 = time.perf_counter()
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            rss_after = process.memory_info().rss
            # MEASURES END ---------------------------------

            data.time[i].append(t1 - t0)
            data.step[i].append(tempSteps)
            data.size[i].append(num_records[i])
            data.rss_memory[i].append((rss_after - rss_before)/ 1024 / 1024) # Convertendo para MB
            data.peak_python_memory[i].append(peak/ 1024 / 1024) # Convertendo para MB

            print(f"    Test {j+1} Finished.")

# SAVE DATA FROM TEST TO CSV
def save_data_to_csv(data, test, sequence, num_records):
        os.makedirs('results', exist_ok=True)
        suffix = 'sorted-sequence' if sequence else 'random-sequence'
        filename = f'results/{test}_{suffix}_results.csv'

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Size', 'Time', 'Steps', 'RSS_Memory_MB', 'Peak_Python_Memory_MB'])
            for j in range(len(num_records)):
                for i in range(len(data.size[j])):
                    writer.writerow([
                        data.size[j][i],
                        data.time[j][i],
                        data.step[j][i],
                        data.rss_memory[j][i],
                        data.peak_python_memory[j][i]
                    ])

if __name__ == "__main__":
    num_records = [10_000, 50_000, 100_000]
    methods_to_test_name = ["Read-CSV-to-BST", "Read-CSV-to-AVL", "Search-BST", "Search-AVL"]
    methods_to_test = [read_csv_to_bst, read_csv_to_avl, search_bst, search_avl]
    type_of_test = ["load", "load", "bst-search", "avl-search"]
    skip = [0, 1]  # load tests skipped: benchmark foca em busca

    sequence = False
    dir = "data"

    for test_idx in range(len(methods_to_test)):
        if test_idx in skip:
            continue

        data = bruteData(num_records)

        test = methods_to_test[test_idx]
        test_name = methods_to_test_name[test_idx]
        test_type = type_of_test[test_idx]
        funcTest(data, num_records, test, test_name, dir, test_type)

        save_data_to_csv(data, test_name, sequence, num_records)


