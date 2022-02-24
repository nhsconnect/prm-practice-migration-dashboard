import boto3
from moto import mock_s3

from src.s3 import write_object_s3


@mock_s3
def test_writes_object_content():
    s3 = boto3.resource("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test_bucket")

    json_string = b'{"fruit": "mango"}'
    write_object_s3(s3, "s3://test_bucket/test_object.json", json_string)

    s3_object_response = s3.Object("test_bucket", "test_object.json").get()
    assert s3_object_response["Body"].read() == json_string
