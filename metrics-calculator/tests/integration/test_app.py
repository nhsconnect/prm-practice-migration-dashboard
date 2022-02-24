import boto3
import json
from moto import mock_s3
import pytest
import os

from chalice.test import Client
from src.app import app
from tests.builders.file import build_gzip_csv


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope='function')
def s3(aws_credentials):
    with mock_s3():
        yield boto3.resource('s3', region_name='us-east-1')


@pytest.fixture(scope="function")
def test_client():
    with Client(app) as client:
        yield client


@mock_s3
def test_calculate_dashboard_metrics_from_telemetry(test_client, s3):
    telemetry_bucket = s3.create_bucket(Bucket="telemetry_bucket")
    metrics_bucket = s3.create_bucket(Bucket="metrics_bucket")
    telemetry_bucket.Object("1234-telemetry.csv").put(
        Body=build_gzip_csv(
            header=["_time"],
            rows=[["2021-12-01T15:42:00.000+0000"], [
                "2021-12-02T15:42:00.000+0000"]],
        )
    )
    telemetry_bucket.Object("5678-telemetry.csv").put(
        Body=build_gzip_csv(
            header=["_time"],
            rows=[["2021-12-05T15:42:00.000+0000"], [
                "2021-12-06T15:42:00.000+0000"]],
        )
    )

    test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry',
        {"oldAsid": "1234", "newAsid": "5678", "odsCode": "A12345"})

    migrations_obj = metrics_bucket.Object("migrations.json").get()
    migrations_body = migrations_obj['Body'].read().decode('utf-8')

    assert json.loads(migrations_body) == {"migrations": [{
        "cutover_startdate": "2021-12-02T15:42:00+00:00",
        "cutover_enddate": "2021-12-05T15:42:00+00:00",
        "cutover_duration": 3,
        "practice_name": "Example practice",
        "ccg_name": "Greater Example",
        "source_system": "Ye Olde System",
        "target_system": "Shiny NU",
    }]}
