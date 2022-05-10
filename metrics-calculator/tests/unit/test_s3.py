import boto3
import gzip
from moto import mock_s3
import pytest
import os

from chalicelib.s3 import read_object_s3, write_object_s3, objects_exist
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


@mock_s3
def test_read_object_s3_returns_object_content(s3):
    bucket = s3.create_bucket(Bucket="test_bucket")
    s3_object = bucket.Object("test_object.csv.gz")
    gzipped_content = build_gzip_csv(
        header=["id", "message", "comment"],
        rows=[["123", "A message", "A comment"], [
            "321", "Another message", "Another comment"]],
    )
    s3_object.put(
        Body=gzipped_content
    )

    expected = "id,message,comment\n123,A message,A comment\n321,Another message,Another comment"

    csv_stream = read_object_s3(s3, "s3://test_bucket/test_object.csv.gz")

    with gzip.open(csv_stream, mode="rt") as f:
        actual = f.read()

    assert actual == expected


@mock_s3
def test_write_object_s3_writes_object_content(s3):
    s3.create_bucket(Bucket="test_bucket")

    json_string = b'{"fruit": "mango"}'
    write_object_s3(s3, "s3://test_bucket/test_object.json", json_string)

    s3_object_response = s3.Object("test_bucket", "test_object.json").get()
    assert s3_object_response["Body"].read() == json_string


@mock_s3
def test_objects_exist_checks_for_existing_files(s3):
    s3.create_bucket(Bucket="test_bucket")

    object_one = "object-one"
    object_two = "object-two"

    write_object_s3(s3, "s3://test_bucket/object-one", b'object-one')
    write_object_s3(s3, "s3://test_bucket/object-two", b'object-two')

    result = objects_exist(s3, "test_bucket", [object_one, object_two])

    assert result
