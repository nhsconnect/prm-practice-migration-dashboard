import json
import pytest
import sys
from chalice.test import Client
from unittest.mock import Mock


@pytest.fixture
def s3_resource_mock(monkeypatch):
    monkeypatch.setattr("chalicelib.s3.get_s3_resource", Mock())
    monkeypatch.setattr("chalicelib.s3.write_object_s3", Mock())


@pytest.fixture
def telemetry_mock(monkeypatch):
    old_telemetry = (x for x in [
        {"_time": "2021-12-01T15:42:00.000+0000"}
    ])
    new_telemetry = (x for x in [
        {"_time": "2021-12-05T15:42:00.000+0000"}
    ])
    monkeypatch.setattr(
        "chalicelib.telemetry.get_telemetry", Mock(
            side_effect=[old_telemetry, new_telemetry]))


@pytest.fixture(scope="function")
def test_client(telemetry_mock, s3_resource_mock):
    from app import app
    with Client(app) as client:
        yield client
    sys.modules.pop('app')


@pytest.fixture(scope="function")
def lambda_environment_vars():
    with open('.chalice/config.json') as f:
        config = json.loads(f.read())
        yield config["stages"]["dev"]["lambda_functions"][
            "calculate_dashboard_metrics_from_telemetry"]["environment_variables"]


def test_calculate_dashboard_metrics_from_telemetry(
        test_client):

    result = test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry',
        {"oldAsid": "1234", "newAsid": "5678", "odsCode": "A12345"})

    assert result.payload == "ok"
