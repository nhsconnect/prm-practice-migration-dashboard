import boto3
import os
import pytest

from moto import mock_s3

from chalicelib.lookup_all_asids import lookup_all_asids, ASID_LOOKUP_HEADERS, AsidLookupError
from chalicelib.migration_occurrences import EMIS_PRODUCT_ID, TPP_PRODUCT_ID, VISION_PRODUCT_ID
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

    with pytest.raises(AsidLookupError, match="Bucket test-bucket is empty"):
        lookup_all_asids(s3, bucket_name, migrations)


def test_lookup_all_asids_returns_empty_dictionary_when_given_an_empty_list_of_migrations(s3):
    bucket_name = "test-bucket"
    s3.create_bucket(Bucket=bucket_name)
    migrations = []

    result = lookup_all_asids(s3, bucket_name, migrations)

    assert result == {}


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
    new_asid = {"asid": "12345", "name": "EMIS Web"}
    old_asid = {"asid": "09876", "name": "SystmOne"}
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
            "new": {"asid": "12345", "name": "EMIS Web"},
            "old": {"asid": "09876", "name": "SystmOne"}
        }}
    assert result == expected_result


def test_lookup_all_asids_returns_both_asids_for_an_ods_code_from_two_files(s3):
    ods_code = "ods-code"
    activated_product_id = EMIS_PRODUCT_ID
    new_asid = {"asid": "12345", "name": "EMIS Web"}
    old_asid = {"asid": "09876", "name": "SystmOne"}
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
            "new": {"asid": "12345", "name": "EMIS Web"},
            "old": {"asid": "09876", "name": "SystmOne"}
        }}
    assert result == expected_result


def test_lookup_all_asids_returns_both_asids_for_a_matching_ods_code(s3):
    ods_code = "ods-code"
    activated_product_id = EMIS_PRODUCT_ID
    new_asid = {"asid": "12345", "name": "EMIS Web"}
    old_asid = {"asid": "09876", "name": "SystmOne"}
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [old_asid["asid"], ods_code, "", "", old_asid["name"], "", ""],
                [new_asid["asid"], ods_code, "", "", new_asid["name"], "", ""],
                ["different-asid", "wrong-ods-code", "", "", "product-id", "", ""]
            ],
        ))

    migrations = [{
        "ods_code": ods_code,
        "product_id": activated_product_id
    }]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        "ods-code": {
            "new": {"asid": "12345", "name": "EMIS Web"},
            "old": {"asid": "09876", "name": "SystmOne"}
        }}
    assert result == expected_result


@pytest.mark.parametrize(
    "systems,old_index,new_index,activated_product_id",
    [
        ([{"asid": "1", "name": "SystmOne"}, {
            "asid": "2", "name": "EMIS Web"}], 0, 1, EMIS_PRODUCT_ID),
        ([{"asid": "1", "name": "SystmOne"}, {
            "asid": "2", "name": "EMIS Web"}], 0, 1, EMIS_PRODUCT_ID),
        ([{"asid": "1", "name": "SystmOne"}, {
            "asid": "2", "name": "EMIS Web"}], 1, 0, TPP_PRODUCT_ID),
        ([{"asid": "1", "name": "EMIS Web"}, {
            "asid": "2", "name": "SystmOne"}], 0, 1, TPP_PRODUCT_ID),
        ([{"asid": "1", "name": "EMIS Web"}, {
            "asid": "2", "name": "SystmOne"}], 1, 0, EMIS_PRODUCT_ID),
        ([{"asid": "1", "name": "Vision 3"}, {
            "asid": "2", "name": "SystmOne"}], 0, 1, TPP_PRODUCT_ID),
        ([{"asid": "1", "name": "Vision 3"}, {
            "asid": "2", "name": "SystmOne"}], 1, 0, VISION_PRODUCT_ID),
        ([{"asid": "1", "name": "EMIS Web"}, {
            "asid": "2", "name": "Vision 3"}], 0, 1, VISION_PRODUCT_ID),
        ([{"asid": "1", "name": "EMIS Web"}, {
            "asid": "2", "name": "Vision 3"}], 1, 0, EMIS_PRODUCT_ID)
    ])
def test_lookup_all_asids_returns_both_asids_for_a_matching_ods_code_and_relevant_product_id(
        s3, systems, old_index, new_index, activated_product_id):
    ods_code = "ods-code"
    system_one = systems[0]
    system_two = systems[1]
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [system_one["asid"], ods_code, "", "", system_one["name"], "", ""],
                [system_two["asid"], ods_code, "", "", system_two["name"], "", ""],
                ["different-asid", ods_code, "", "", "different-product-id", "", ""]
            ],
        ))

    migrations = [{
        "ods_code": ods_code,
        "product_id": activated_product_id
    }]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        "ods-code": {
            "new": systems[new_index],
            "old": systems[old_index]
        }}
    assert result == expected_result


def test_lookup_all_asids_returns_both_asids_for_multiple_matching_ods_codes(s3):
    ods_code_1 = "ods-code-1"
    ods_code_2 = "ods-code-2"
    activated_product_id_1 = EMIS_PRODUCT_ID
    activated_product_id_2 = TPP_PRODUCT_ID
    new_asid_1 = {"asid": "12345", "name": "EMIS Web"}
    old_asid_1 = {"asid": "09876", "name": "Vision 3"}
    new_asid_2 = {"asid": "08642", "name": "SystmOne"}
    old_asid_2 = {"asid": "13579", "name": "EMIS Web"}
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [old_asid_1["asid"], ods_code_1, "", "", old_asid_1["name"], "", ""],
                [new_asid_1["asid"], ods_code_1, "", "", new_asid_1["name"], "", ""],
                [old_asid_2["asid"], ods_code_2, "", "", old_asid_2["name"], "", ""],
                [new_asid_2["asid"], ods_code_2, "", "", new_asid_2["name"], "", ""]
            ],
        ))

    migrations = [
        {
            "ods_code": ods_code_1,
            "product_id": activated_product_id_1
        },
        {
            "ods_code": ods_code_2,
            "product_id": activated_product_id_2
        }
    ]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        ods_code_1: {
            "new": new_asid_1,
            "old": old_asid_1
        },
        ods_code_2: {
            "new": new_asid_2,
            "old": old_asid_2
        }
    }
    assert result == expected_result


def test_lookup_all_asids_stops_when_all_asids_are_found(s3):
    ods_code_1 = "ods-code-1"
    ods_code_2 = "ods-code-2"
    activated_product_id_1 = EMIS_PRODUCT_ID
    activated_product_id_2 = TPP_PRODUCT_ID
    new_asid_1 = {"asid": "new-asid-1", "name": "EMIS Web"}
    old_asid_1 = {"asid": "old-asid-1", "name": "Vision 3"}
    new_asid_2 = {"asid": "new-asid-2", "name": "SystmOne"}
    old_asid_2 = {"asid": "old-asid-2", "name": "EMIS Web"}
    bucket_name = "test-bucket"
    asid_lookup_bucket = s3.create_bucket(Bucket=bucket_name)
    asid_lookup_bucket.Object("asid-lookup-1.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [old_asid_1["asid"], ods_code_1, "", "", old_asid_1["name"], "", ""],
                [old_asid_2["asid"], ods_code_2, "", "", old_asid_2["name"], "", ""],
                [new_asid_2["asid"], ods_code_2, "", "", new_asid_2["name"], "", ""]
            ],
        ))
    asid_lookup_bucket.Object("asid-lookup-2.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [old_asid_1["asid"], ods_code_1, "", "", old_asid_1["name"], "", ""],
                [new_asid_1["asid"], ods_code_1, "", "", new_asid_1["name"], "", ""],
                [old_asid_2["asid"]+"_SHOULD_NOT_RETURN_THIS_ASID", ods_code_2, "", "", old_asid_2["name"], "", ""],
                [new_asid_2["asid"]+"_SHOULD_NOT_RETURN_THIS_ASID", ods_code_2, "", "", new_asid_2["name"], "", ""]
            ],
        ))

    migrations = [
        {
            "ods_code": ods_code_1,
            "product_id": activated_product_id_1
        },
        {
            "ods_code": ods_code_2,
            "product_id": activated_product_id_2
        }
    ]

    result = lookup_all_asids(s3, bucket_name, migrations)

    expected_result = {
        ods_code_1: {
            "new": new_asid_1,
            "old": old_asid_1
        },
        ods_code_2: {
            "new": new_asid_2,
            "old": old_asid_2
        }
    }
    assert result == expected_result