import csv


def get_rows(filename):
    with open(filename, 'r', encoding='ISO-8859-1') as csvfile:
        datareader = csv.DictReader(csvfile)
        for row in datareader:
            yield {key: value for key, value in row.items()}


