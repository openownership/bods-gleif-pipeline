import csv
from pathlib import Path

scheme_dir = Path(__file__).parent.resolve()

def load_data(filename):
    data = []
    with open(scheme_dir / filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            data.append(row)
    return data

def search_data(data, col, val):
    match = [d for d in data if d[col] == val]
    if match:
        return match[0]
    else:
        return None
