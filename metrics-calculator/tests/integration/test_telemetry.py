import gzip
import boto3
import os
import pytest

from moto import mock_s3
from chalicelib.csv_rows import csv_rows
from chalicelib.s3 import read_object_s3

from chalicelib.telemetry import upload_telemetry


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


def test_upload_telemetry(s3):
    bucket_name = "bucket-name"
    telemetry_data = b"telemetry-data"
    filename = "telemetry-file"
    s3.create_bucket(Bucket=bucket_name)

    upload_telemetry(s3, bucket_name, telemetry_data, filename)

    uploaded_telemetry = read_object_s3(s3, f"s3://{bucket_name}/{filename}")
    telemetry_string = uploaded_telemetry.read()
    unzipped_telemetry = gzip.decompress(telemetry_string)

    assert unzipped_telemetry == telemetry_data
