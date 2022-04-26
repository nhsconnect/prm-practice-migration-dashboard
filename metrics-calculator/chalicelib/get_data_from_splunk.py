import csv
from http.client import HTTPSConnection


class SplunkQueryError(RuntimeError):
    pass


class SplunkParseError(Exception):
    pass


def get_baseline_threshold_from_splunk_data(asid, baseline_date_range):
    connection = HTTPSConnection("splunk-url")
    request_body = {
        "output_mode": "csv",
        "earliest_time": baseline_date_range["start_date"],
        "latest_time": baseline_date_range["end_date"],
        "search": f"""index="spine2vfmmonitor" messageSender={asid}
| bucket span=1d _time
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| stats count by _time
| outlier action=remove
| eventstats avg(count) as average stdev(count) as stdd
| eval avgmin2std=average-(stdd*2)
| fields - stdd"""
    }
    connection.request('POST', "/?activationRegion=eu-west-2", request_body)
    response = connection.getresponse()
    if response.status != 200:
        raise SplunkQueryError(f"Splunk request returned a {response.status} code")
    try:
        response_lines = response.read().decode().splitlines()
        csv_reader = csv.DictReader(response_lines)
        first_row = next(csv_reader)
        threshold = first_row["avgmin2std"]
    except Exception as exception:
        raise SplunkParseError from exception
    if float(threshold) <= 0:
        raise ValueError("Threshold is not a positive value")
    return threshold


def get_telemetry_from_splunk(asid, baseline_threshold, date_range):
    connection = HTTPSConnection("splunk-url")
    connection.request('POST', "/?activationRegion=eu-west-2")
    response = connection.getresponse()
    if response.status != 200:
        raise SplunkQueryError(f"Splunk request returned a {response.status} code")
    return response


