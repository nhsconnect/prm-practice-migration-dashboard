import pytest as pytest
import urllib.parse

from datetime import date
from unittest.mock import Mock, MagicMock

from chalicelib.get_data_from_splunk import SplunkQueryError, SplunkParseError, \
    get_telemetry_from_splunk, parse_threshold_from_telemetry, get_baseline_telemetry_from_splunk, make_splunk_request


@pytest.fixture(scope="function")
def splunk_response(monkeypatch):
    response_mock = Mock()
    connection_mock = Mock(return_value=MagicMock(getresponse=response_mock))
    monkeypatch.setattr(
        "chalicelib.get_data_from_splunk.HTTPSConnection", connection_mock)
    yield response_mock


@pytest.fixture(scope="function")
def splunk_request(monkeypatch):
    request_mock = Mock()
    response_mock = Mock(read=lambda: b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307""", status=200)
    connection_mock = Mock(return_value=MagicMock(
        request=request_mock, getresponse=Mock(return_value=response_mock)))
    monkeypatch.setattr(
        "chalicelib.get_data_from_splunk.HTTPSConnection", connection_mock)
    yield {
        "connection": connection_mock,
        "request": request_mock
    }


def test_parse_threshold_from_telemetry_extracts_threshold_from_splunk_telemetry():
    telemetry = b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307"""

    baseline_threshold = parse_threshold_from_telemetry(telemetry)

    assert baseline_threshold == "4537.33933970307"


def test_parse_threshold_from_telemetry_handles_no_results():
    telemetry = b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"0"""

    with pytest.raises(ValueError, match="Threshold is not a positive value"):
        parse_threshold_from_telemetry(telemetry)


def test_parse_threshold_from_telemetry_handles_parse_failure():
    telemetry = "this-is-not-a-byte-string"

    with pytest.raises(SplunkParseError):
        parse_threshold_from_telemetry(telemetry)


def test_get_baseline_telemetry_from_splunk_makes_correct_request(splunk_request):
    asid = anAsid()
    baseline_date_range = aDateRange()
    splunk_host = "test-splunk"
    token = anApiToken()

    get_baseline_telemetry_from_splunk(
        splunk_host, token, asid, baseline_date_range)

    expected_request_body = urllib.parse.urlencode({
        "output_mode": "csv",
        "earliest_time": "2021-04-06T00:00:00",
        "latest_time": "2021-06-28T24:00:00",
        "search": f"""search index="spine2vfmmonitor" messageSender={asid}
| bucket span=1d _time
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| stats count by _time
| outlier action=remove
| eventstats avg(count) as average stdev(count) as stdd
| eval avgmin2std=average-(stdd*2)
| fields - stdd
| convert timeformat="%Y-%m-%dT%H:%M:%S" ctime(_time)"""
    })
    expected_headers = {"Authorization": f"Bearer {token}"}
    splunk_request["connection"].assert_called_once_with(splunk_host)
    splunk_request["request"].assert_called_once_with(
        "POST", "/services/search/jobs/export", expected_request_body, expected_headers)


def test_get_telemetry_from_splunk_get_cutover_telemetry(splunk_response):
    threshold = "4537.33933970307"
    expected_telemetry = b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307"""
    splunk_response.return_value = Mock(
        read=lambda: expected_telemetry, status=200)

    telemetry = get_telemetry_from_splunk(
        "", anApiToken(), anAsid(), aDateRange(), threshold)

    assert telemetry == expected_telemetry


def test_get_telemetry_from_splunk_makes_correct_request(splunk_request):
    asid = anAsid()
    date_range = aDateRange()
    threshold = "4537.33933970307"
    splunk_host = "test-splunk"
    token = anApiToken()

    get_telemetry_from_splunk(splunk_host, token, asid, date_range, threshold)

    expected_request_body = urllib.parse.urlencode({
        "output_mode": "csv",
        "earliest_time": "2021-04-06T00:00:00",
        "latest_time": "2021-06-28T24:00:00",
        "search": f"""search index="spine2vfmmonitor" messageSender={asid}
| timechart span=1d count
| fillnull
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| eval avgmin2std={threshold}
| fields - day_of_week
| convert timeformat="%Y-%m-%dT%H:%M:%S" ctime(_time)"""
    })
    expected_headers = {"Authorization": f"Bearer {token}"}
    splunk_request["connection"].assert_called_once_with(splunk_host)
    splunk_request["request"].assert_called_once_with(
        "POST", "/services/search/jobs/export", expected_request_body, expected_headers)


def test_make_splunk_request_handles_http_response_failure(splunk_response):
    splunk_response.return_value = Mock(status=404)

    with pytest.raises(SplunkQueryError, match="Splunk request returned a 404 code"):
        make_splunk_request("", anApiToken(), aDateRange(), "")


def anAsid():
    return "12345"


def aDateRange():
    return {
        "start_date": date(2021, 4, 6),
        "end_date": date(2021, 6, 28)
    }


def anApiToken():
    return "this-is-a-token"
