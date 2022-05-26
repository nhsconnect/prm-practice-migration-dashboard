import boto3
import os
import pytest

from moto import mock_s3

from chalicelib.lookup_all_asids import lookup_all_asids, ASID_LOOKUP_HEADERS
from chalicelib.migration_occurrences import EMIS_PRODUCT_ID, TPP_PRODUCT_ID
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


def test_lookup_all_asids_raises_exception_when_there_are_no_asid_lookup_files(s3):
    ods_code = "ods-code"
    bucket_name = "test-bucket"
    s3.create_bucket(Bucket=bucket_name)
    migrations = [{
        "ods_code": ods_code
    }]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        "ods-code": {
            "old": {"asid": "", "name": ""},
            "new": {"asid": "", "name": ""}
        }}
    assert result == expected_result


def test_lookup_all_asids_returns_entry_without_asids_when_asids_are_not_found_for_an_ods_code(s3):
    ods_code = "ods-code"
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    migrations = [{
        "ods_code": ods_code
    }]
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[],
        ))

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        "ods-code": {
            "old": {"asid": "", "name": ""},
            "new": {"asid": "", "name": ""}
        }}
    assert result == expected_result


def test_lookup_all_asids_returns_both_asids_for_an_ods_code_from_one_file(s3):
    ods_code = "ods-code"
    activated_product_id = EMIS_PRODUCT_ID
    new_asid = {"asid": "12345", "name": EMIS_PRODUCT_ID}
    old_asid = {"asid": "09876", "name": TPP_PRODUCT_ID}
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [old_asid["asid"], ods_code, "", "", old_asid["name"], "", ""],
                [new_asid["asid"], ods_code, "", "", new_asid["name"], "", ""]
            ],
        ))

    migrations = [{
        "ods_code": ods_code,
        "product_id": activated_product_id
    }]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        "ods-code": {
            "new": {"asid": "12345", "name": EMIS_PRODUCT_ID},
            "old": {"asid": "09876", "name": TPP_PRODUCT_ID}
        }}
    assert result == expected_result


def test_lookup_all_asids_returns_both_asids_for_an_ods_code_from_two_files(s3):
    ods_code = "ods-code"
    activated_product_id = EMIS_PRODUCT_ID
    new_asid = {"asid": "12345", "name": EMIS_PRODUCT_ID}
    old_asid = {"asid": "09876", "name": TPP_PRODUCT_ID}
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    asid_lookup_bucket.Object("asid-lookup-1.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [old_asid["asid"], ods_code, "", "", old_asid["name"], "", ""]
            ],
        ))
    asid_lookup_bucket.Object("asid-lookup-2.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [new_asid["asid"], ods_code, "", "", new_asid["name"], "", ""]
            ],
        ))

    migrations = [{
        "ods_code": ods_code,
        "product_id": activated_product_id
    }]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        "ods-code": {
            "new": {"asid": "12345", "name": EMIS_PRODUCT_ID},
            "old": {"asid": "09876", "name": TPP_PRODUCT_ID}
        }}
    assert result == expected_result
