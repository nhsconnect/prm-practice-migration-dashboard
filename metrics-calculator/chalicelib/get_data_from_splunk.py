import csv
from http.client import HTTPSConnection


class SplunkQueryError(RuntimeError):
    pass


class SplunkParseError(Exception):
    pass


def get_baseline_threshold_from_splunk_data(
        splunk_base_url, asid, baseline_date_range):
    response = make_request_for_baseline_telemetry(
        splunk_base_url, asid, baseline_date_range)
    threshold = parse_threshold_from_splunk_response(response)
    return threshold


def get_telemetry_from_splunk(splunk_base_url, asid, date_range, baseline_threshold):
    search_text = f"""index="spine2vfmmonitor" messageSender={asid}
| timechart span=1d count
| fillnull
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| eval avgmin2std={baseline_threshold}
| fields - day_of_week"""
    response = make_splunk_request(splunk_base_url, date_range, search_text)
    return response


def make_request_for_baseline_telemetry(splunk_base_url, asid, baseline_date_range):
    search_text = f"""index="spine2vfmmonitor" messageSender={asid}
| bucket span=1d _time
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| stats count by _time
| outlier action=remove
| eventstats avg(count) as average stdev(count) as stdd
| eval avgmin2std=average-(stdd*2)
| fields - stdd"""
    response = make_splunk_request(
        splunk_base_url, baseline_date_range, search_text)
    return response


def make_splunk_request(splunk_base_url, date_range, search_text):
    connection = HTTPSConnection(splunk_base_url)
    connection.connect()
    request_body = {
        "output_mode": "csv",
        "earliest_time": date_range["start_date"],
        "latest_time": date_range["end_date"],
        "search": search_text
    }
    connection.request('POST', "/search/jobs/export", request_body)
    response = connection.getresponse()
    if response.status != 200:
        raise SplunkQueryError(
            f"Splunk request returned a {response.status} code")
    return response


def parse_threshold_from_splunk_response(response):
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
