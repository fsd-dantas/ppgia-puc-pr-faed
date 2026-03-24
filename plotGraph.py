import csv
import matplotlib.pyplot as plt

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
    methods_to_test_name = ["Load-values-from-CSV", 
                            "Search-values-in-CSV", "Binary-Search-in-CSV",
                            "Read-CSV-to-BST", "Read-CSV-to-AVL", 
                            "Search-BST", "Search-AVL",
                            "Read-CSV-to-Hash-(Divisao)", "Read-CSV-to-Hash-(Multiplicacao)", "Read-CSV-to-Hash-(Folding)",
                            "Search-Hash-(Divisao)", "Search-Hash-(Multiplicacao)", "Search-Hash-(Folding)"
    ]
    sequence = True
    skip = [0,1,2,3,4,5,6]

    if sequence:
        seq_string = "sorted-sequence"
    else:
        seq_string = "random-sequence"
    

    for i in range(len(methods_to_test_name)):
        if i in skip:
            continue
        print(f"Runing through {methods_to_test_name[i]}")
        test_name = methods_to_test_name[i]
        data = read_data_from_csv(f'genResults/{test_name}_{seq_string}_results.csv', num_records)

        graphSizeXMemory(data, test_name, sequence)
        graphSizeXMemoryPeak(data, test_name, sequence)
        graphSizeXStep(data, test_name, sequence)
        graphSizeXTime(data, test_name, sequence)