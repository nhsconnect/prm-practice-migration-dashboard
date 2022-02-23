from unittest import mock

import boto3
import unittest
from moto import mock_s3

from src.s3 import read_gzip_csv
from tests.builders.file import build_gzip_csv


@mock_s3
def test_returns_csv_row_as_dictionary():
    pass
    # conn = boto3.resource("s3", region_name="eu-west-1")
    # bucket = conn.create_bucket(Bucket="test_bucket")
    # s3_object = bucket.Object("test_object.csv.gz")
    # s3_object.put(
    #     Body=build_gzip_csv(
    #         header=["id", "message", "comment"],
    #         rows=[["123", "A message", "A comment"], ["321", "Another message", "Another comment"]],
    #     )
    # )
    #
    # expected = [
    #     {"id": "123", "message": "A message", "comment": "A comment"},
    #     {"id": "321", "message": "Another message", "comment": "Another comment"},
    # ]
    #
    # actual = read_gzip_csv("s3://test_bucket/test_object.csv.gz")
    #
    # assert list(actual) == expected