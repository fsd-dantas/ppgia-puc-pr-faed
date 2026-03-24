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
        self.load_factor = []
        for _ in range(len(num_records)):
            self.time.append([])
            self.step.append([])
            self.size.append([])
            self.rss_memory.append([])
            self.peak_python_memory.append([])
            self.load_factor.append([])

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


# Classe para a Hash Table e funções de hash ----------------------------------
class HashTable:
    def __init__(self, size, hash_function):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.hash_function = hash_function
        self.count = 0  # número de elementos inseridos
        self.collisions = 0

    def insert(self, key):
        index = self.hash_function(key['Mat'], self.size)

        # Verifica colisão
        if len(self.table[index]) > 0:
            self.collisions += 1

        # Evita duplicatas
        if key not in self.table[index]:
            self.table[index].append(key)
            self.count += 1

    def searchMat(self, key):
        index = self.hash_function(key, self.size)
        return key in self.table[index]

    def load_factor(self):
        return self.count / self.size
    

# 1 - Divisão simples
def hash_division(key, size):
    return key % size

# 2 - Multiplicação (Knuth)
def hash_multiplication(key, size):
    A = 0.6180339887  # constante de ouro
    return int(size * ((key * A) % 1))

# 3 - Método folding (grandes inteiros)
def hash_folding(key, size):
    key_str = str(key)
    parts = [int(key_str[i:i+2]) for i in range(0, len(key_str), 2)]
    return sum(parts) % size

# Funções a serem Testadas ----------------------------------------------------
def read_csv_to_hash(filename, steps, ht): # ******Inserir HT já instanciada
    header = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "Mat":
                for x in row:
                    header.append(x)
                continue
            ht.insert({header[0]: int(row[0]), header[1]: row[1], header[2]: float(row[2]), header[3]: int(row[3])})
            steps+=1
    return ht, steps

def search_hash(ht, key, steps):
    found = ht.searchMat(key)
    steps+=1
    return found, steps

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
        arr = read_csv_to_array(f'{dir}/data_{total_records}_{j+1}.csv')
        searchArr.append(arr[round(total_records * (idx0 * (j+1)))-1]['Mat'])
    return searchArr
    
def instantiateHashTable(size, hash_type):
    if "div" in hash_type.lower():
        return HashTable(size, hash_division)
    elif "mul" in hash_type.lower():
        return HashTable(size, hash_multiplication)
    elif "fld" in hash_type.lower():
        return HashTable(size, hash_folding)
    else:
        raise ValueError("Invalid hash type. Use 'div', 'mul', or 'fld'.")

# Função para realizar os testes e coletar os dados
def funcTest(data, num_records, func, funcName, dir, type, size):
    number_of_tests = 5
    
    print(f"Starting Test {funcName} with size {size}...")
    # FOR EVERY NUM_RECORDS
    for i in range(len(num_records)):
        # TEST  DIFERENT DATASETS {number_of_tests} TIMES TO GET A MEAN
        print(f"Starting Test with {num_records[i]} samples...")
        
        # Gerar um array de valores para busca, com base nos valores dos CSVs
        if "search" in type.lower():
            searchArr = getSearchArray(number_of_tests,num_records[i], dir)

        for j in range(number_of_tests):
            print(f"    Starting Test {j+1}...")

            # Deixa dados carregados para busca em diferentes tipos de teste de busca em HTs
            if "search" in type.lower():
                ht = instantiateHashTable(size, type)
                ht,_ = read_csv_to_hash(f'{dir}/data_{num_records[i]}_{j+1}.csv', 0, ht)
                
            # MEASURES START -------------------------------
            tempSteps = 0
            process = psutil.Process(os.getpid())

            tracemalloc.start()

            rss_before = process.memory_info().rss
            t0 = time.perf_counter()
            # MEASURES START -------------------------------
            
            # Executa a função de teste de acordo com o tipo
            if "load" in type.lower():
                ht = instantiateHashTable(size, type)
                ht, tempSteps = func(f'{dir}/data_{num_records[i]}_{j+1}.csv', tempSteps, ht)
            elif "search" in type.lower():
                response, tempSteps = func(ht, searchArr[j], tempSteps)
            else:
                ht = None
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
            data.load_factor[i].append(ht.load_factor() if ht else None)

            print(f"    Test {j+1} Finished.")


# SAVE DATA FROM TEST TO CSV
def save_data_to_csv(data, test, sequence):
        if sequence:
            filename = f'genResults/{test}_sorted-sequence_results.csv'
        else:
            filename = f'genResults/{test}_random-sequence_results.csv'

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Size', 'Time', 'Steps', 'RSS_Memory_MB', 'Peak_Python_Memory_MB', 'Load_Factor'])
            for j in range(len(num_records)):
                for i in range(len(data.size[0])):
                    writer.writerow([
                        data.size[j][i],
                        data.time[j][i],
                        data.step[j][i],
                        data.rss_memory[j][i],
                        data.peak_python_memory[j][i],
                        data.load_factor[j][i]
                    ])

if __name__ == "__main__":
    #num_records = [10_000, 25_000, 50_000, 75_000, 100_000, 250_000, 500_000, 750_000, 1_000_000]
    num_records = [10_000, 25_000, 50_000, 75_000, 100_000]
    methods_to_test_name = ["Read-CSV-to-Hash-(Divisao)", "Read-CSV-to-Hash-(Multiplicacao)", "Read-CSV-to-Hash-(Folding)", "Search-Hash-(Divisao)", "Search-Hash-(Multiplicacao)", "Search-Hash-(Folding)"]
    methods_to_test = [read_csv_to_hash, read_csv_to_hash, read_csv_to_hash, search_hash, search_hash, search_hash]
    type_of_test = ["hash-load-div", "hash-load-mul", "hash-load-fld", "hash-search-div", "hash-search-mul", "hash-search-fld"]
    # Tamanhos para tratamento de colisões
    sizes = [10,50,100,1000,5000,10000]
    skip = [0,1,2]

    sequence = True
    dir = "genDataSequence"

    for i in range(len(methods_to_test_name)):
        if i in skip:
            continue
        
        for size in sizes:
            data = bruteData(num_records)

            test_name = methods_to_test_name[i]
            func = methods_to_test[i]
            type = type_of_test[i]

            funcTest(data, num_records, func, test_name, dir, type, size)

            test_name += f"_size{size}_{type[-3:]}"

            save_data_to_csv(data, test_name, sequence)

    


