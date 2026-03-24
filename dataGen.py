# -- Dados
# Criar registros fictícios com diferentes volumes: N = {10.000, 50.000, 100.000, ...}
# Cada registro deve conter, por exemplo: Matrícula (9 dígitos), Nome, Salário, Código do Setor, Outros campos relevantes conforme necessidade do experimento

from random import SystemRandom
import csv
import time

# N = {10.000, 25.000, 50.000, 75.000, 100.000, 250.000, 500.000, 750.000, 1.000.000}
# N = {  0   ,   1   ,    2  ,    3   ,    4   ,    5  ,    6   ,    7   ,      8   }
N = [[],[],[],[],[],[],[],[],[]]

tempExclusion = [] # Excluir os 9 primeiros testes para não gerar os arquivos de dados
notSequence = False
for i in range(len(N)):
    # Select number of records
    if i in tempExclusion:
        continue
    if i == 0:
        num_records = 10_000
    elif i == 1:
        num_records = 25_000
    elif i == 2:
        num_records = 50_000
    elif i == 3:
        num_records = 75_000
    elif i == 4:
        num_records = 100_000
    elif i == 5:
        num_records = 250_000
    elif i == 6:
        num_records = 500_000
    elif i == 7:
        num_records = 750_000
    elif i == 8:
        num_records = 1_000_000

    for k in range(5):
        print(f"\nGenerating {num_records} records...")
        
        records = []
        random = SystemRandom()
        if notSequence:
            usedMat = []
            mat = random.randint(1, 999999999)
        else:
            mat = 1
        for j in range(num_records):
            # Select unique registration number
            if notSequence:
                while mat in usedMat:
                    mat = random.randint(1, 999999999)
            
                usedMat.append(mat)
            else:
                mat = j + 1

            # [Mat, Name, Sal, CodSec]
            x = [mat, 
                random.choice(["Roger Walters", "Freddie Mercury", "Brian May", "Tyler Joseph", "Josh Dun", "Hailey Williams", "Ozzy Osbourne"]), 
                round(random.uniform(1000, 5000),2), 
                random.randint(1, 10)]

            records.append(x)

        print(f"Generated random numbers and data for N={num_records}")

        # Import to CSV
        if notSequence:
            fileName = f"genData/data_{num_records}_{k+1}_notSequence.csv"
        else:
            random.seed(42) # Seed para garantir a mesma sequência de dados
            random.shuffle(records) # Embaralha os registros para criar uma sequência aleatória
            fileName = f"genDataSequence/data_{num_records}_{k+1}.csv"
        with open(fileName, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Mat", "Name", "Sal", "CodSec"])
            writer.writerows(records)

        print(f"Generated {num_records} records in genData/data_{num_records}_{k+1}.csv")

