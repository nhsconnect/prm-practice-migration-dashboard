import boto3
import json
from moto import mock_s3
from chalice.test import Client
from src.s3 import read_gzip_csv
from src.app import app
from tests.builders.file import build_gzip_csv


@mock_s3
def test_calculate_dashboard_metrics_from_telemetry():
    s3 = boto3.resource("s3", region_name="us-east-1")
    # telemetry_bucket = s3.create_bucket(Bucket="telemetry_bucket")
    metrics_bucket = s3.create_bucket(Bucket="metrics_bucket")
    # telemetry_bucket.Object("telemetry.csv").put(
    #     Body=build_gzip_csv(
    #         header=["id", "message", "comment"],
    #         rows=[["123", "A message", "A comment"], [
    #             "321", "Another message", "Another comment"]],
    #     )
    # )

    with Client(app) as client:
        client.lambda_.invoke(
            'calculate_dashboard_metrics_from_telemetry',
            {"telementryFile:": "telemetry.csv"})

    migrations_obj = metrics_bucket.Object("migrations.json").get()
    migrations_body = migrations_obj['Body'].read().decode('utf-8')

    assert json.loads(migrations_body) == {"foo": "bar"}
