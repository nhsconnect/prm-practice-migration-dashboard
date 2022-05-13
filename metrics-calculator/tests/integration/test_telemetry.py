import boto3
import gzip
import os
import pytest

from datetime import date
from moto import mock_s3

from chalicelib.s3 import read_object_s3, _object_from_uri
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


def test_upload_telemetry_uploads_zipped_telemetry(s3):
    bucket_name = "bucket-name"
    telemetry_data = b"telemetry-data"
    filename = "telemetry-file"
    s3.create_bucket(Bucket=bucket_name)

    upload_telemetry(s3, bucket_name, telemetry_data, filename, date(2021, 4, 6), date(2021, 6, 28))

    uploaded_telemetry = read_object_s3(s3, f"s3://{bucket_name}/{filename}")
    telemetry_string = uploaded_telemetry.read()
    unzipped_telemetry = gzip.decompress(telemetry_string)

    assert unzipped_telemetry == telemetry_data


def test_upload_telemetry_saves_start_and_end_dates_as_metadata(s3):
    bucket_name = "bucket-name"
    filename = "telemetry-file"
    s3.create_bucket(Bucket=bucket_name)
    upload_telemetry(s3, bucket_name, b"telemetry-data", filename, date(2021, 4, 6), date(2021, 6, 28))

    s3_object = _object_from_uri(s3, f"s3://{bucket_name}/{filename}")
    response = s3_object.get()
    returned_metadata = response["Metadata"]
    assert returned_metadata["start_date"] == "2021-04-06"
    assert returned_metadata["end_date"] == "2021-06-28"
