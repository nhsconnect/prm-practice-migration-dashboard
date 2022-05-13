import csv
from http.client import HTTPSConnection
import urllib.parse


class SplunkQueryError(RuntimeError):
    pass


class SplunkParseError(Exception):
    pass


class SplunkTelemetryMissing(Exception):
    pass


def get_telemetry_from_splunk(splunk_host, token, asid, date_range, baseline_threshold):
    search_text = f"""search index="spine2vfmmonitor" messageSender={asid}
| timechart span=1d count
| fillnull
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| eval avgmin2std={baseline_threshold}
| fields - day_of_week
| convert timeformat="%Y-%m-%dT%H:%M:%S" ctime(_time)"""
    telemetry = make_splunk_request(
        splunk_host, token, date_range, search_text)
    return telemetry


def get_baseline_telemetry_from_splunk(splunk_host, token, asid, baseline_date_range):
    search_text = f"""search index="spine2vfmmonitor" messageSender={asid}
| bucket span=1d _time
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| stats count by _time
| outlier action=remove
| eventstats avg(count) as average stdev(count) as stdd
| eval avgmin2std=average-(stdd*2)
| fields - stdd
| convert timeformat="%Y-%m-%dT%H:%M:%S" ctime(_time)"""
    telemetry = make_splunk_request(
        splunk_host, token, baseline_date_range, search_text)
    return telemetry


def make_splunk_request(splunk_host, token, date_range, search_text):
    connection = HTTPSConnection(splunk_host)
    connection.connect()
    request_body = urllib.parse.urlencode({
        "output_mode": "csv",
        "earliest_time": date_range["start_date"].strftime("%Y-%m-%dT00:00:00"),
        "latest_time": date_range["end_date"].strftime("%Y-%m-%dT24:00:00"),
        "search": search_text
    })
    headers = {"Authorization": f"Bearer {token}"}
    connection.request(
        'POST', "/services/search/jobs/export", request_body, headers)

    response = connection.getresponse()
    if response.status != 200:
        raise SplunkQueryError(
            f"Splunk request returned a {response.status} code with body {response.read()}")
    return response.read()


def parse_threshold_from_telemetry(telemetry):
    lines = convert_to_lines(telemetry)
    if len(lines) == 0 or len(lines) == 1:
        raise SplunkTelemetryMissing(f"Telemetry received: \"{lines}\"")
    threshold = extract_threshold(lines)
    if float(threshold) <= 0:
        raise ValueError("Threshold is not a positive value")
    return threshold


def extract_threshold(lines):
    try:
        csv_reader = csv.DictReader(lines)
        first_row = next(csv_reader)
        threshold = first_row["avgmin2std"]
        return threshold
    except Exception as exception:
        raise SplunkParseError from exception


def convert_to_lines(telemetry):
    try:
        lines = telemetry.decode().splitlines()
        return lines
    except (UnicodeError, AttributeError) as exception:
        raise SplunkParseError from exception
