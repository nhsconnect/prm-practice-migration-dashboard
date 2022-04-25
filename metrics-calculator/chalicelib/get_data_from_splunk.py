import csv
from http.client import HTTPSConnection


def get_baseline_threshold_from_splunk_data(asid, baseline_date_range):
    connection = HTTPSConnection("splunk-url")
    connection.request('GET', "/?activationRegion=eu-west-2")
    response = connection.getresponse()
    response_lines = response.read().decode().splitlines()
    csv_reader = csv.DictReader(response_lines)
    first_row = next(csv_reader)
    threshold = first_row["avgmin2std"]
    if float(threshold) <= 0:
        raise ValueError("Threshold is not a positive value")
    return threshold
