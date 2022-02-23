import csv
import gzip


def csv_rows(stream):
    with gzip.open(stream, mode="rt") as f:
        input_csv = csv.DictReader(f)
        yield from input_csv
