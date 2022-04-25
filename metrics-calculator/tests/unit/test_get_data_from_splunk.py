from datetime import date
from unittest.mock import Mock, MagicMock

import pytest as pytest

from chalicelib.get_data_from_splunk import get_baseline_threshold_from_splunk_data, SplunkQueryError


@pytest.fixture(scope="function")
def splunk(monkeypatch):
    request_mock = Mock()
    splunk_call_mock = Mock(return_value=MagicMock(getresponse=request_mock))
    monkeypatch.setattr("chalicelib.get_data_from_splunk.HTTPSConnection", splunk_call_mock)
    yield request_mock


def test_get_baseline_threshold_from_splunk_data_extracts_threshold_from_splunk_telemetry(splunk):
    asid = "12345"
    baseline_date_range = {"start_date": date(2021, 4, 6), "end_date": date(2021, 6, 28)}

    splunk.return_value = Mock(read=lambda:b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307""")

    baseline_threshold = get_baseline_threshold_from_splunk_data(
        asid, baseline_date_range)

    assert baseline_threshold == "4537.33933970307"


def test_get_baseline_threshold_from_splunk_data_handles_no_results(splunk):
    asid = "not-a-valid-asid"
    baseline_date_range = {"start_date": date(2021, 4, 6), "end_date": date(2021, 6, 28)}

    splunk.return_value = Mock(read=lambda:b"""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",0,""0""")

    with pytest.raises(ValueError, match="Threshold is not a positive value"):
        get_baseline_threshold_from_splunk_data(
            asid, baseline_date_range)


def test_get_baseline_threshold_from_splunk_data_handles_HTTP_response_failure(splunk):
    asid = "12345"
    baseline_date_range = {"start_date": date(2021, 4, 6), "end_date": date(2021, 6, 28)}

    splunk.return_value = Mock(status=404)

    with pytest.raises(SplunkQueryError, match="Splunk request returned a 404 code"):
        get_baseline_threshold_from_splunk_data(
            asid, baseline_date_range)