import random
import csv

def generate_parking_row(rows_number: int):
    rows = [['empty_count', 'longitude', 'latitude']]

    for _ in range(rows_number):
        row = [int(random.uniform(10, 50)), random.uniform(10, 50), random.uniform(10, 50)]
        rows.append(row)

    return rows

file_path = "./parking.csv"
rows_number = 1500
rows = generate_parking_row(rows_number)


with open(file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows)
