import csv

from Evaluation import rows, cols

def load_layout(filename = 'Plate_Layouts/MPCD.csv', delimiter=","):
    layout = {}
    content = []
    with open(filename, newline='') as csvfile:

        plate_layout = csv.reader(csvfile, delimiter=delimiter, quotechar='"')

        for row in plate_layout:
            content.append(row)

    for row_idx, row in enumerate(content): 
        for col_idx, value in enumerate(row):
            layout[rows[row_idx]+cols[col_idx]] = value

    return layout

