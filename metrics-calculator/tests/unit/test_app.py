import boto3
from chalice.test import Client
from moto import mock_s3
from src.app import app


@mock_s3
def test_calculate_dashboard_metrics_from_telemetry():
    s3 = boto3.resource("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="metrics_bucket")

    with Client(app) as client:
        result = client.lambda_.invoke(
            'calculate_dashboard_metrics_from_telemetry')

        assert result.payload == "ok"
