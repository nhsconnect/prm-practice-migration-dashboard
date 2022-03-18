from itertools import chain
import json
import pytest

from chalice.test import Client
from unittest.mock import ANY, Mock

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
def telemetry_mock(monkeypatch):
    old_telemetry = old_telemetry_generator()
    new_telemetry = new_telemetry_generator()
    mock = Mock(side_effect=[old_telemetry, new_telemetry])
    monkeypatch.setattr("app.get_telemetry", mock)
    yield mock


@pytest.fixture
def occurrences_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.get_migration_occurrences", mock)
    yield mock


@pytest.fixture
def lookup_asids_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.lookup_asids", mock)
    yield mock


@pytest.fixture
def engine_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.calculate_cutover_start_and_end_date", mock)
    yield mock


@pytest.fixture(scope="function")
def upload_migrations_mock(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("app.upload_migrations", mock)
    yield mock


@pytest.fixture(scope="function")
def test_client(
        telemetry_mock, occurrences_mock, s3_resource_mock):
    from app import app
    with Client(app) as client:
        yield client


@pytest.fixture(scope="function")
def lambda_environment_vars():
    with open(".chalice/config.json") as f:
        config = json.loads(f.read())
        yield config["stages"]["dev"]["lambda_functions"][
            "calculate_dashboard_metrics_from_telemetry"]["environment_variables"]


def test_calculate_dashboard_metrics_from_telemetry(
        test_client, occurrences_mock, lookup_asids_mock, engine_mock):
    occurrences_mock.return_value = [
        {
            "ods_code": "",
            "ccg_name": "",
            "practice_name": "",
        }
    ]
    lookup_asids_mock.return_value = {
        "old": {"asid": "1234", "name": ""},
        "new": {"asid": "5678", "name": ""}
    }
    engine_mock.return_value = {"ods_code": "", "cutover_duration": 1}

    result = test_client.lambda_.invoke(
        "calculate_dashboard_metrics_from_telemetry")

    assert result.payload == "ok"


def test_includes_practice_details_from_occurrences_data_in_migration_metrics(
        test_client,
        occurrences_mock,
        lookup_asids_mock,
        engine_mock,
        upload_migrations_mock):
    migration_occurrence = {
        "ods_code": "A32323",
        "ccg_name": "Test CCG",
        "practice_name": "Test Surgery",
    }
    occurrences_mock.return_value = [migration_occurrence]
    lookup_asids_mock.return_value = {
        "old": {"asid": "1234", "name": "oldy"},
        "new": {"asid": "5678", "name": "newy"}
    }
    engine_mock.return_value = {"ods_code": "", "cutover_duration": 1}

    test_client.lambda_.invoke(
        "calculate_dashboard_metrics_from_telemetry")

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


def test_ignores_asid_lookup_failures(
        test_client,
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
    engine_mock.return_value = {"ods_code": "", "cutover_duration": 1}

    test_client.lambda_.invoke(
        "calculate_dashboard_metrics_from_telemetry")

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


def test_includes_metrics_for_multiple_migations(
        test_client,
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
    lookup_asids_mock.return_value = {
        "old": {"asid": "", "name": ""},
        "new": {"asid": "", "name": ""}
    }
    engine_mock.return_value = {"ods_code": "A11111", "cutover_duration": 1}

    test_client.lambda_.invoke(
        "calculate_dashboard_metrics_from_telemetry")

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
def test_calculates_average_cutover_duration_to_one_decimal_place(
        test_client,
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
    lookup_asids_mock.return_value = {
        "old": {"asid": "1234", "name": "oldy"},
        "new": {"asid": "5678", "name": "newy"}
    }
    engine_mock.return_value = {"ods_code": "A11111"}
    engine_mock.side_effect = map(
        lambda x: {"ods_code": "", "cutover_duration": x}, durations)

    test_client.lambda_.invoke(
        "calculate_dashboard_metrics_from_telemetry")

    upload_migrations_mock.assert_called_once_with(
        ANY,
        {
            "mean_cutover_duration": expected_average,
            "migrations": ANY
        })
