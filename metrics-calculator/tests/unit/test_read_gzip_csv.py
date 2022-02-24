from cmath import exp
import boto3
import gzip
from moto import mock_s3

from src.s3 import read_object_s3
from tests.builders.file import build_gzip_csv


@mock_s3
def test_returns_object_content():
    s3 = boto3.resource("s3", region_name="us-east-1")
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
