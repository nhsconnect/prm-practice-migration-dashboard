from datetime import date, timedelta
import os
from itertools import chain
import json
import pytest

from unittest.mock import ANY, Mock

from app import calculate_dashboard_metrics_from_telemetry, export_splunk_data
from chalicelib.lookup_asids import AsidLookupError


def new_telemetry_generator():
    return (x for x in [
        {"_time": "2021-12-05T15:42:00.000+0000"}
    ]
    )


def old_telemetry_generator():
    return (x for x in [
        {"_time": "2021-12-01T15:42:00.000+0000"}
    ]
    )


@pytest.fixture
def s3_resource_mock(monkeypatch):
    monkeypatch.setattr("app.get_s3_resource", Mock())
    monkeypatch.setattr("app.write_object_s3", Mock())


@pytest.fixture
def ssm_client_mock(monkeypatch):
    monkeypatch.setattr("app.get_ssm_client", Mock())


@pytest.fixture
def telemetry_mock(monkeypatch):
    old_telemetry = old_telemetry_generator()
    new_telemetry = new_telemetry_generator()
    mock = Mock(side_effect=[old_telemetry, new_telemetry])
    monkeypatch.setattr("app.get_telemetry", mock)
    yield mock


@pytest.fixture
def upload_telemetry_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.upload_telemetry", mock)
    yield mock


@pytest.fixture
def occurrences_mock(monkeypatch):
    mock = Mock(return_value=[])
    monkeypatch.setattr("app.get_migration_occurrences", mock)
    yield mock


@pytest.fixture
def calculate_baseline_date_range_mock(monkeypatch):
    mock = Mock(
        return_value={"start_date": date.today(), "end_date": date.today()})
    monkeypatch.setattr("app.calculate_baseline_date_range", mock)
    yield mock


@pytest.fixture
def calculate_pre_cutover_date_range_mock(monkeypatch):
    mock = Mock(
        return_value={"start_date": date.today() - timedelta(2), "end_date": date.today() - timedelta(1)})
    monkeypatch.setattr("app.calculate_pre_cutover_date_range", mock)
    yield mock


@pytest.fixture
def calculate_post_cutover_date_range_mock(monkeypatch):
    mock = Mock(
        return_value={"start_date": date.today() + timedelta(1), "end_date": date.today() + timedelta(2)})
    monkeypatch.setattr("app.calculate_post_cutover_date_range", mock)
    yield mock


@pytest.fixture
def get_splunk_api_token_mock(monkeypatch):
    mock = Mock(return_value="mock-splunk-api-token")
    monkeypatch.setattr("app.get_splunk_api_token", mock)
    yield mock


@pytest.fixture
def get_baseline_threshold_from_splunk_data_mock(monkeypatch):
    mock = Mock(
        return_value="101")
    monkeypatch.setattr(
        "app.get_baseline_threshold_from_splunk_data", mock)
    yield mock


@pytest.fixture
def get_telemetry_from_splunk_mock(monkeypatch):
    mock = Mock(
        return_value="""_time",count,avgmin2std
"2021-09-06T00:00:00.000+0000",2,"4537.33933970307""")
    monkeypatch.setattr("app.get_telemetry_from_splunk", mock)
    yield mock


@pytest.fixture
def lookup_asids_mock(monkeypatch):
    mock = Mock()
    mock.return_value = {
        "old": {"asid": "", "name": ""},
        "new": {"asid": "", "name": ""}
    }
    monkeypatch.setattr("app.lookup_asids", mock)
    yield mock


@pytest.fixture
def engine_mock(monkeypatch):
    mock = Mock()
    mock.return_value = {"ods_code": "", "cutover_duration": 1}
    monkeypatch.setattr("app.calculate_cutover_start_and_end_date", mock)
    yield mock


@pytest.fixture(scope="function")
def upload_migrations_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.upload_migrations", mock)
    yield mock


@pytest.fixture(scope="function")
def mock_defaults(
        s3_resource_mock,
        ssm_client_mock,
        calculator_lambda_env_vars,
        exporter_lambda_env_vars,
        telemetry_mock,
        occurrences_mock,
        lookup_asids_mock,
        get_baseline_threshold_from_splunk_data_mock,
        get_splunk_api_token_mock,
        get_telemetry_from_splunk_mock,
        upload_telemetry_mock):
    pass


@pytest.fixture(scope="function")
def calculator_lambda_env_vars():
    with open(".chalice/config.json") as f:
        config = json.loads(f.read())
        vars = config["stages"]["dev"]["lambda_functions"]["calculate_dashboard_metrics_from_telemetry"]["environment_variables"]
        for key in vars:
            os.environ[key] = vars[key]
        yield vars


@pytest.fixture(scope="function")
def exporter_lambda_env_vars():
    with open(".chalice/config.json") as f:
        config = json.loads(f.read())
        vars = config["stages"]["dev"]["lambda_functions"]["export_splunk_data"]["environment_variables"]
        for key in vars:
            os.environ[key] = vars[key]
        yield vars


def test_calculate_dashboard_metrics_from_telemetry_runs_without_any_occurrences_data(
        mock_defaults, occurrences_mock, lookup_asids_mock):

    occurrences_mock.return_value = []

    result = calculate_dashboard_metrics_from_telemetry({}, {})

    assert result == "ok"


def test_calculate_dashboard_metrics_from_telemetry_includes_practice_details_from_occurrences_data_in_migration_metrics(
        mock_defaults,
        occurrences_mock,
        lookup_asids_mock,
        engine_mock,
        upload_migrations_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]

    calculate_dashboard_metrics_from_telemetry({}, {})

    upload_migrations_mock.assert_called_with(
        ANY,
        {
            "mean_cutover_duration": ANY,
            "migrations": [{
                "practice_name": migration_occurrence["practice_name"],
                "ccg_name": migration_occurrence["ccg_name"],
                "ods_code": migration_occurrence["ods_code"],
                "source_system": ANY,
                "target_system": ANY,
                "cutover_duration": ANY
            }]
        })


def test_calculate_dashboard_metrics_from_telemetry_ignores_asid_lookup_failures(
        mock_defaults,
        occurrences_mock,
        lookup_asids_mock,
        engine_mock,
        upload_migrations_mock):
    migration_occurrence_1 = {
        "ods_code": "A11111",
    }
    migration_occurrence_2 = {
        "ods_code": "B22222",
        "ccg_name": "",
        "practice_name": "",
    }
    occurrences_mock.return_value = [
        migration_occurrence_1, migration_occurrence_2]

    def fail_on_first_lookup(s3, bucket_name, migration):
        if migration == migration_occurrence_1:
            raise AsidLookupError("Error!")
        return {
            "old": {"asid": "", "name": ""},
            "new": {"asid": "", "name": ""}
        }
    lookup_asids_mock.side_effect = fail_on_first_lookup

    calculate_dashboard_metrics_from_telemetry({}, {})

    upload_migrations_mock.assert_called_once_with(
        ANY,
        {
            "mean_cutover_duration": "1.0",
            "migrations": [{
                "practice_name": ANY,
                "ccg_name": ANY,
                "ods_code": ANY,
                "source_system": ANY,
                "target_system": ANY,
                "cutover_duration": ANY
            }]
        })


def test_calculate_dashboard_metrics_from_telemetry_includes_metrics_for_multiple_migrations(
        mock_defaults,
        occurrences_mock,
        telemetry_mock,
        lookup_asids_mock,
        engine_mock,
        upload_migrations_mock):
    migration_occurrence_1 = {
        "ods_code": "A32323",
        "ccg_name": "First CCG",
        "practice_name": "First Surgery",
    }
    migration_occurrence_2 = {
        "ods_code": "B22222",
        "ccg_name": "Second CCG",
        "practice_name": "Second Surgery",
    }
    occurrences_mock.return_value = [
        migration_occurrence_1, migration_occurrence_2]
    telemetry_mock.side_effect = [
        old_telemetry_generator(), new_telemetry_generator(),
        old_telemetry_generator(), new_telemetry_generator()]

    calculate_dashboard_metrics_from_telemetry({}, {})

    upload_migrations_mock.assert_called_once_with(
        ANY,
        {
            "mean_cutover_duration": ANY,
            "migrations": [
                {
                    "practice_name": migration_occurrence_1["practice_name"],
                    "ccg_name": migration_occurrence_1["ccg_name"],
                    "ods_code": migration_occurrence_1["ods_code"],
                    "source_system": ANY,
                    "target_system": ANY,
                    "cutover_duration": ANY
                },
                {
                    "practice_name": migration_occurrence_2["practice_name"],
                    "ccg_name": migration_occurrence_2["ccg_name"],
                    "ods_code": migration_occurrence_2["ods_code"],
                    "source_system": ANY,
                    "target_system": ANY,
                    "cutover_duration": ANY
                }]
        })


@pytest.mark.parametrize(
    "durations,expected_average",
    [
        ([1], "1.0"),
        ([1, 1], "1.0"),
        ([4, 2], "3.0"),
        ([4, 3], "3.5"),
        ([2, 1, 1, 1], "1.3"),
        ([2, 1, 1, 1, 1, 1, 1], "1.1"),
    ])
def test_calculate_dashboard_metrics_from_telemetry_calculates_average_cutover_duration_to_one_decimal_place(
        mock_defaults,
        occurrences_mock,
        telemetry_mock,
        lookup_asids_mock,
        engine_mock,
        upload_migrations_mock,
        durations,
        expected_average):
    occurrences_mock.return_value = map(
        lambda x: {"ods_code": "", "ccg_name": "", "practice_name": ""}, durations)
    # The use of chain here is inspired by the answer to this Stack Overflow question:
    # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
    telemetry_mock.side_effect = chain(
        *map(lambda _: (old_telemetry_generator(), new_telemetry_generator()), durations))
    engine_mock.side_effect = map(
        lambda x: {"ods_code": "", "cutover_duration": x}, durations)

    calculate_dashboard_metrics_from_telemetry({}, {})

    upload_migrations_mock.assert_called_once_with(
        ANY,
        {
            "mean_cutover_duration": expected_average,
            "migrations": ANY
        })


def test_export_splunk_data_runs_without_any_occurrences_data(mock_defaults):
    result = export_splunk_data({}, {})

    assert result == "ok"


def test_export_splunk_data_gets_asids_for_ods_code_in_occurrences_data(
        mock_defaults,
        occurrences_mock,
        lookup_asids_mock,
        exporter_lambda_env_vars):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]

    export_splunk_data({}, {})

    lookup_asids_mock.assert_called_once_with(
        ANY,
        exporter_lambda_env_vars["ASID_LOOKUP_BUCKET_NAME"],
        migration_occurrence
    )


def test_export_splunk_data_gets_baseline_date_range(
        mock_defaults,
        occurrences_mock,
        calculate_baseline_date_range_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]

    export_splunk_data({}, {})

    calculate_baseline_date_range_mock.assert_called_once_with(
        migration_occurrence["date"])


def test_export_splunk_data_gets_pre_cutover_date_range(
        mock_defaults,
        occurrences_mock,
        calculate_pre_cutover_date_range_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]

    export_splunk_data({}, {})

    calculate_pre_cutover_date_range_mock.assert_called_once_with(
        migration_occurrence["date"])


def test_export_splunk_data_gets_post_cutover_date_range(
        mock_defaults,
        occurrences_mock,
        calculate_post_cutover_date_range_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]

    export_splunk_data({}, {})

    calculate_post_cutover_date_range_mock.assert_called_once_with(
        migration_occurrence["date"])


def test_export_splunk_data_does_not_get_splunk_api_token_when_there_are_no_migration_occurrences(
        mock_defaults,
        occurrences_mock,
        get_splunk_api_token_mock):
    occurrences_mock.return_value = []

    export_splunk_data({}, {})

    get_splunk_api_token_mock.assert_not_called()


def test_export_splunk_data_gets_splunk_api_token(
        mock_defaults,
        occurrences_mock,
        get_splunk_api_token_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]

    export_splunk_data({}, {})

    get_splunk_api_token_mock.assert_called_with(
        ANY,
        "/prod/splunk-api-token"
    )


def test_export_splunk_data_gets_splunk_api_token_once_regardless_of_number_of_migration_occurrences(
        mock_defaults,
        occurrences_mock,
        get_splunk_api_token_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [
        migration_occurrence, migration_occurrence]

    export_splunk_data({}, {})

    get_splunk_api_token_mock.assert_called_once()


def test_export_splunk_data_queries_splunk_for_baseline_threshold(
        mock_defaults,
        occurrences_mock,
        calculate_baseline_date_range_mock,
        lookup_asids_mock,
        exporter_lambda_env_vars,
        get_splunk_api_token_mock,
        get_baseline_threshold_from_splunk_data_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]
    old_asid = "12345"
    lookup_asids_mock.return_value = {
        "old": {"asid": old_asid, "name": ""},
        "new": {"asid": "", "name": ""}
    }

    export_splunk_data({}, {})

    get_baseline_threshold_from_splunk_data_mock.assert_called_once_with(
        exporter_lambda_env_vars["SPLUNK_HOST"],
        get_splunk_api_token_mock.return_value,
        old_asid,
        calculate_baseline_date_range_mock.return_value)


def test_export_splunk_data_queries_splunk_data_using_baseline_threshold(
        mock_defaults,
        occurrences_mock,
        calculate_pre_cutover_date_range_mock,
        calculate_post_cutover_date_range_mock,
        lookup_asids_mock,
        exporter_lambda_env_vars,
        get_splunk_api_token_mock,
        get_baseline_threshold_from_splunk_data_mock,
        get_telemetry_from_splunk_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]
    old_asid = "12345"
    new_asid = "09876"
    lookup_asids_mock.return_value = {
        "old": {"asid": old_asid, "name": ""},
        "new": {"asid": new_asid, "name": ""}
    }
    baseline_threshold = "10"
    get_baseline_threshold_from_splunk_data_mock.return_value = baseline_threshold

    export_splunk_data({}, {})

    get_telemetry_from_splunk_mock.assert_any_call(
        exporter_lambda_env_vars["SPLUNK_HOST"],
        get_splunk_api_token_mock.return_value,
        old_asid,
        calculate_pre_cutover_date_range_mock.return_value,
        baseline_threshold)
    get_telemetry_from_splunk_mock.assert_any_call(
        exporter_lambda_env_vars["SPLUNK_HOST"],
        get_splunk_api_token_mock.return_value,
        new_asid,
        calculate_post_cutover_date_range_mock.return_value,
        baseline_threshold)


def test_export_splunk_data_uploads_telemetry_to_s3(
        mock_defaults,
        occurrences_mock,
        upload_telemetry_mock,
        lookup_asids_mock,
        exporter_lambda_env_vars,
        get_telemetry_from_splunk_mock):
    migration_occurrence = aMigrationOccurrence()
    occurrences_mock.return_value = [migration_occurrence]
    old_asid = "12345"
    new_asid = "09876"
    lookup_asids_mock.return_value = {
        "old": {"asid": old_asid, "name": ""},
        "new": {"asid": new_asid, "name": ""}
    }
    old_telemetry_data = "old"
    new_telemetry_data = "new"
    get_telemetry_from_splunk_mock.side_effect = [
        old_telemetry_data, new_telemetry_data]

    export_splunk_data({}, {})

    upload_telemetry_mock.assert_any_call(
        ANY,
        exporter_lambda_env_vars["TELEMETRY_BUCKET_NAME"],
        old_telemetry_data,
        f"{old_asid}-telemetry.csv.gz"
    )
    upload_telemetry_mock.assert_any_call(
        ANY,
        exporter_lambda_env_vars["TELEMETRY_BUCKET_NAME"],
        new_telemetry_data,
        f"{new_asid}-telemetry.csv.gz"
    )


def aMigrationOccurrence():
    return {
        "ods_code": "A32323",
        "ccg_name": "Test CCG",
        "practice_name": "Test Surgery",
        "date": date(2021, 7, 11)
    }
