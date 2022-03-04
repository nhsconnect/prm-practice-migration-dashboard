import json
import boto3
from chalice.test import Client
from moto import mock_s3
import pytest
import os

from app import app
from tests.builders.file import build_gzip_csv


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture(scope="function")
def s3(aws_credentials):
    with mock_s3():
        yield boto3.resource('s3', region_name='us-east-1')


@pytest.fixture(scope="function")
def test_client():
    with Client(app) as client:
        yield client


@pytest.fixture(scope="function")
def lambda_environment_vars():
    with open('.chalice/config.json') as f:
        config = json.loads(f.read())
        yield config["stages"]["dev"]["lambda_functions"][
            "calculate_dashboard_metrics_from_telemetry"]["environment_variables"]


@mock_s3
def test_calculate_dashboard_metrics_from_telemetry(
        test_client, lambda_environment_vars, s3):
    telemetry_bucket_name = lambda_environment_vars["TELEMETRY_BUCKET_NAME"]
    telemetry_bucket = s3.create_bucket(Bucket=telemetry_bucket_name)
    telemetry_bucket.Object("1234-telemetry.csv.gz").put(
        Body=build_gzip_csv(
            header=["_time"],
            rows=[["2021-12-01T15:42:00.000+0000"]],
        )
    )
    telemetry_bucket.Object("5678-telemetry.csv.gz").put(
        Body=build_gzip_csv(
            header=["_time"],
            rows=[["2021-12-05T15:42:00.000+0000"]],
        )
    )
    metrics_bucket_name = lambda_environment_vars["METRICS_BUCKET_NAME"]
    s3.create_bucket(Bucket=metrics_bucket_name)

    result = test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry',
        {"oldAsid": "1234", "newAsid": "5678", "odsCode": "A12345"})

    assert result.payload == "ok"
