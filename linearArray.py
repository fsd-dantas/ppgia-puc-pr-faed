import time
import psutil
import tracemalloc
import csv
import os
import matplotlib.pyplot as plt

# DATA CLASS
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
        

# FUNÇÃO PARA LER CSV E TRANSFORMAR EM ARRAY
def read_csv_to_array(filename, steps):
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
            steps+=1
    return arr, steps

# FUNÇÃO DE BUSCAS
def searchFunc(arr, target, steps):
    for i in range(len(arr)):
        steps+=1
        if arr[i]['Mat'] == target:
            return i, steps
    return -1, steps
# FUNÇÃO DE BUSCA BINARIA E SORT
def binarySearchFunc(arr, target, steps):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        steps+=1
        if arr[mid]['Mat'] == target:
            return mid, steps
        elif arr[mid]['Mat'] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, steps
# Quick Sort
def partition(arr, lo, hi):
    mid = (lo+hi)//2
    pivot = arr[mid]['Mat']
    arr[mid], arr[hi] = arr[hi], arr[mid]

    i = lo
    for j in range(lo,hi):
        if arr[j]['Mat']<=pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i+=1
        
    arr[i], arr[hi] = arr[hi], arr[i]

    return i

def quick_sort(arr, lo, hi):
    if lo<hi:
        pivot_index = partition(arr, lo, hi)
        quick_sort(arr, lo, pivot_index-1)
        quick_sort(arr, pivot_index+1, hi)


# SAVE/READ DATA TO/FROM CSV
def save_data_to_csv(data, test, sequence):
        if sequence:
            filename = f'genResults/{test}_sorted-sequence_results.csv'
        else:
            filename = f'genResults/{test}_random-sequence_results.csv'

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Size', 'Time', 'Steps', 'RSS_Memory_MB', 'Peak_Python_Memory_MB'])
            for j in range(len(num_records)):
                for i in range(len(data.size[0])):
                    writer.writerow([
                        data.size[j][i],
                        data.time[j][i],
                        data.step[j][i],
                        data.rss_memory[j][i],
                        data.peak_python_memory[j][i]
                    ])

def read_data_from_csv(filename, num_records):
    data = bruteData(num_records)
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            size = int(row[0])
            time = float(row[1])
            steps = int(row[2])
            rss_memory = float(row[3])
            peak_python_memory = float(row[4])
            
            # Assuming the order of num_records is consistent with the data
            for i in range(len(num_records)):
                if size == num_records[i]:
                    data.size[i].append(size)
                    data.time[i].append(time)
                    data.step[i].append(steps)
                    data.rss_memory[i].append(rss_memory)
                    data.peak_python_memory[i].append(peak_python_memory)
                    break
    return data


# Testes de Funções -------------------
def funcTest(data, num_records, func, funcName, dir, type):
    number_of_tests = 5
    
    print(f"Starting Test {funcName}")
    # FOR EVERY NUM_RECORDS
    for i in range(len(num_records)):
        # TEST  DIFERENT DATASETS x TIMES TO GET A MEAN
        print(f"Starting Test with {num_records[i]} samples...")
        if "search" in type.lower():
            searchArr = [round(num_records[i]*0.20), round(num_records[i]*0.40), round(num_records[i]*0.60), round(num_records[i]*0.80), num_records[i]]
            
            
        for j in range(number_of_tests):
            print(f"    Starting Test {j+1}...")

            if "search" in type.lower():
                arr,_ = read_csv_to_array(f'{dir}/data_{num_records[i]}_{j+1}.csv', 0)
                if not sequence and "binary" in type.lower():
                    quick_sort(arr, 0, len(arr)-1)
            
            tempSteps = 0
            # MEASURES
            process = psutil.Process(os.getpid())

            tracemalloc.start()

            rss_before = process.memory_info().rss
            t0 = time.perf_counter()
            if type.lower() == "load":
                arr, tempSteps = func(f'{dir}/data_{num_records[i]}_{j+1}.csv', tempSteps)
            elif "search" in type.lower():
                idx, tempSteps = func(arr, searchArr[j], tempSteps)
            else:
                arr = []
                tempSteps = -1
            t1 = time.perf_counter()
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            rss_after = process.memory_info().rss

            data.time[i].append(t1 - t0)
            data.step[i].append(tempSteps)
            data.size[i].append(len(arr))
            data.rss_memory[i].append((rss_after - rss_before)/ 1024 / 1024) # Convertendo para MB
            data.peak_python_memory[i].append(peak/ 1024 / 1024) # Convertendo para MB

            print(f"    Test {j+1} Finished.")

# GRAFICOS --------------------------
def graphSizeXStep(data, test, sequence):
    if sequence:
        sequenceTitle = "Sorted Sequence Data"
    else:
        sequenceTitle = "Random Sequence Data"
    plt.figure()
    plt.plot(data.sizesToPlot(), data.stepsToPlot(), marker='o', linestyle='--')
    plt.xlabel("Vector Size")
    plt.ylabel("Number of Steps")
    plt.title(f"{test}: Steps vs Vector Size ({sequenceTitle})")
    plt.tight_layout()
    plt.savefig(f'genGraph/{test}_SIZE-X-STEP.png', dpi=300, bbox_inches='tight', transparent=False)
    plt.close()

def graphSizeXTime(data, test, sequence):
    if sequence:
        sequenceTitle = "Sorted Sequence Data"
    else:
        sequenceTitle = "Random Sequence Data"
    plt.figure()
    plt.plot(data.sizesToPlot(), data.timesToPlot(), marker='o', linestyle='--')
    plt.xlabel("Vector Size")
    plt.ylabel("Execution Time (seconds)")
    plt.title(f"{test}: Time vs Vector Size ({sequenceTitle})")
    plt.tight_layout()
    plt.savefig(f'genGraph/{test}_SIZE-X-TIME.png', dpi=300, bbox_inches='tight', transparent=False)
    plt.close()

def graphSizeXMemory(data, test, sequence):
    if sequence:
        sequenceTitle = "Sorted Sequence Data"
    else:
        sequenceTitle = "Random Sequence Data"
    plt.figure()
    plt.plot(data.sizesToPlot(), data.rssMemoryToPlot(), marker='o', linestyle='--')
    plt.xlabel("Size")
    plt.ylabel("Memory (MB)")
    plt.title(f"{test}: Physical Memory used vs Vector Size ({sequenceTitle})")
    plt.tight_layout()
    plt.savefig(f'genGraph/{test}_SIZE-X-MEMORY.png', dpi=300, bbox_inches='tight', transparent=False)
    plt.close()

def graphSizeXMemoryPeak(data, test, sequence):
    if sequence:
        sequenceTitle = "Sorted Sequence Data"
    else:
        sequenceTitle = "Random Sequence Data"
    plt.figure()
    plt.plot(data.sizesToPlot(), data.peakPythonMemoryToPlot(), marker='o', linestyle='--')
    plt.xlabel("Vector size")
    plt.ylabel("Peak Python memory (MB)")
    plt.title(f"{test}: Peak Python memory used vs Vector Size ({sequenceTitle})")
    plt.tight_layout()
    plt.savefig(f'genGraph/{test}_SIZE-X-MEMORY-PEAK.png', dpi=300, bbox_inches='tight', transparent=False)
    plt.close()


if __name__ == "__main__":
    num_records = [10_000, 25_000, 50_000, 75_000, 100_000, 250_000, 500_000, 750_000, 1_000_000]
    # num_records = [10_000, 25_000, 50_000, 75_000, 100_000]
    methods_to_test_name = ["Load-values-from-CSV", "Search-values-in-CSV", "Binary-Search-in-CSV"]
    methods_to_test = [read_csv_to_array, searchFunc, binarySearchFunc]
    sequence = True
    type_of_test = ["load", "search", "binary-search"]
    skip = [0,1]

    if sequence:
        dir = "genDataSequence"
    else:
        dir = "genData"

    for test_idx in range(len(methods_to_test)):
        if test_idx in skip:
            continue
        # METRICS
        # DATA
        #   - TIME
        #   - STEPS
        #   - SIZE
        data = bruteData(num_records)

        test = methods_to_test[test_idx]
        test_name = methods_to_test_name[test_idx]
        test_type = type_of_test[test_idx]
        funcTest(data, num_records, test, test_name, dir, test_type)
        
        save_data_to_csv(data, test_name, sequence)

        # GRAPHS
        # Plot 1: steps vs vector size
        graphSizeXStep(data, test_name, sequence)

        # Plot 2: time vs vector size
        graphSizeXTime(data,test_name, sequence)
     
        graphSizeXMemory(data,test_name, sequence)
        graphSizeXMemoryPeak(data,test_name, sequence)