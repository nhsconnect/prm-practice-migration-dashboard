import boto3
from chalice.test import Client
from moto import mock_s3
from src.app import app
from tests.builders.file import build_gzip_csv


@mock_s3
def test_calculate_dashboard_metrics_from_telemetry():
    s3 = boto3.resource("s3", region_name="us-east-1")
    telemetry_bucket = s3.create_bucket(Bucket="telemetry_bucket")
    s3.create_bucket(Bucket="metrics_bucket")
    telemetry_bucket.Object("1234-telemetry.csv").put(
        Body=build_gzip_csv(
            header=["_time"],
            rows=[["2021-12-01T15:42:00.000+0000"]],
        )
    )
    telemetry_bucket.Object("5678-telemetry.csv").put(
        Body=build_gzip_csv(
            header=["_time"],
            rows=[["2021-12-05T15:42:00.000+0000"]],
        )
    )

    with Client(app) as client:
        result = client.lambda_.invoke(
            'calculate_dashboard_metrics_from_telemetry',
            {"oldAsid": "1234", "newAsid": "5678", "odsCode": "A12345"})

        assert result.payload == "ok"
