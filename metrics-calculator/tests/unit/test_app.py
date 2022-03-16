import json
import pytest
from chalice.test import Client
from unittest.mock import ANY, Mock


@pytest.fixture
def s3_resource_mock(monkeypatch):
    monkeypatch.setattr("app.get_s3_resource", Mock())
    monkeypatch.setattr("app.write_object_s3", Mock())


@pytest.fixture
def telemetry_mock(monkeypatch):
    old_telemetry = (x for x in [
        {"_time": "2021-12-01T15:42:00.000+0000"}
    ])
    new_telemetry = (x for x in [
        {"_time": "2021-12-05T15:42:00.000+0000"}
    ])
    monkeypatch.setattr(
        "app.get_telemetry", Mock(
            side_effect=[old_telemetry, new_telemetry]))


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
    with open('.chalice/config.json') as f:
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
            "supplier_id": "",
            "product_id": "",
            "date": "",
        }
    ]
    lookup_asids_mock.return_value = {
        "old": {"asid": "1234", "name": "oldy"},
        "new": {"asid": "5678", "name": "newy"}
    }
    engine_mock.return_value = {"ods_code": 'A11111'}

    result = test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry')

    assert result.payload == "ok"


def test_includes_practice_details_from_occurrences_data_in_migration_metrics(
        test_client, occurrences_mock, lookup_asids_mock, engine_mock, upload_migrations_mock):
    migration_occurrence = {
        "ods_code": "A32323",
        "ccg_name": "Test CCG",
        "practice_name": "Test Surgery",
        "supplier_id": "10000",
        "product_id": "10000-001",
        "date": "2021-11-05",
    }
    occurrences_mock.return_value = [migration_occurrence]
    lookup_asids_mock.return_value = {
        "old": {"asid": "1234", "name": "oldy"},
        "new": {"asid": "5678", "name": "newy"}
    }
    engine_mock.return_value = {"ods_code": 'A11111'}

    test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry')

    upload_migrations_mock.assert_called_with(
        ANY,
        {
            "migrations": [{
                "practice_name": migration_occurrence["practice_name"],
                "ccg_name": migration_occurrence["ccg_name"],
                "ods_code": migration_occurrence["ods_code"],
                "source_system": "oldy",
                "target_system": "newy",
            }]
        })
