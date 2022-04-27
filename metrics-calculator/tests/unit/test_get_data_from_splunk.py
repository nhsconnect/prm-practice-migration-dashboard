from datetime import date
from unittest.mock import Mock, MagicMock, ANY

import pytest as pytest

from chalicelib.get_data_from_splunk import get_baseline_threshold_from_splunk_data, SplunkQueryError, SplunkParseError, \
    get_telemetry_from_splunk


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
    yield request_mock


def test_get_baseline_threshold_from_splunk_data_extracts_threshold_from_splunk_telemetry(splunk_response):
    splunk_response.return_value = Mock(read=lambda: b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307""", status=200)

    baseline_threshold = get_baseline_threshold_from_splunk_data(
        "", anAsid(), aDateRange())

    assert baseline_threshold == "4537.33933970307"


def test_get_baseline_threshold_from_splunk_data_handles_no_results(splunk_response):
    splunk_response.return_value = Mock(read=lambda: b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",0,""0""", status=200)

    with pytest.raises(ValueError, match="Threshold is not a positive value"):
        get_baseline_threshold_from_splunk_data("", anAsid(), aDateRange())


def test_get_baseline_threshold_from_splunk_data_handles_http_response_failure(splunk_response):
    splunk_response.return_value = Mock(status=404)

    with pytest.raises(SplunkQueryError, match="Splunk request returned a 404 code"):
        get_baseline_threshold_from_splunk_data("", anAsid(), aDateRange())


def test_get_baseline_threshold_from_splunk_data_handles_parse_failure(splunk_response):
    splunk_response.return_value = Mock(
        read=lambda: "this-is-not-a-byte-string", status=200)

    with pytest.raises(SplunkParseError):
        get_baseline_threshold_from_splunk_data(
            "", anAsid(), aDateRange())


def test_get_baseline_threshold_from_splunk_data_makes_correct_request(splunk_request):
    asid = anAsid()
    baseline_date_range = aDateRange()
    splunk_base_url = "https://test-splunk"

    get_baseline_threshold_from_splunk_data(
        splunk_base_url, asid, baseline_date_range)

    expected_request_body = {
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
    splunk_request.assert_called_once_with(
        "POST", f"{splunk_base_url}/search/jobs/export", expected_request_body)


def test_get_telemetry_from_splunk_get_cutover_telemetry(splunk_response):
    threshold = "4537.33933970307"

    splunk_response.return_value = Mock(read=lambda: b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307""", status=200)

    telemetry = get_telemetry_from_splunk(
        "", anAsid(), aDateRange(), threshold)

    assert telemetry == splunk_response.return_value


def test_get_telemetry_from_splunk_handles_http_response_failure(splunk_response):
    threshold = "4537.33933970307"

    splunk_response.return_value = Mock(status=404)

    with pytest.raises(SplunkQueryError, match="Splunk request returned a 404 code"):
        get_telemetry_from_splunk("", anAsid(), aDateRange(), threshold)


def test_get_telemetry_from_splunk_has_correct_request_body(splunk_request):
    asid = anAsid()
    date_range = aDateRange()
    threshold = "4537.33933970307"
    splunk_base_url = "https://test-splunk"

    get_telemetry_from_splunk(splunk_base_url, asid, date_range, threshold)

    expected_request_body = {
        "output_mode": "csv",
        "earliest_time": date_range["start_date"],
        "latest_time": date_range["end_date"],
        "search": f"""index="spine2vfmmonitor" messageSender={asid}
| timechart span=1d count
| fillnull
| eval day_of_week = strftime(_time,"%A")
| where NOT (day_of_week="Saturday" OR day_of_week="Sunday")
| eval avgmin2std={threshold}
| fields - day_of_week"""
    }
    splunk_request.assert_called_once_with(
        "POST", f"{splunk_base_url}/search/jobs/export", expected_request_body)


def anAsid():
    return "12345"


def aDateRange():
    return {"start_date": date(
        2021, 4, 6), "end_date": date(2021, 6, 28)}
