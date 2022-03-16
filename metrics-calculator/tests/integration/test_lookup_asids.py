import boto3
import os
import pytest

from moto import mock_s3

from chalicelib.lookup_asids import ASID_LOOKUP_HEADERS, lookup_asids, AsidLookupError
from chalicelib.migration_occurrences import TPP_PRODUCT_ID, EMIS_PRODUCT_ID, VISION_PRODUCT_ID
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


def test_raises_exception_when_no_asids_found(s3):
    s3.create_bucket(Bucket="test-bucket")
    with pytest.raises(AsidLookupError):
        lookup_asids(s3, "test-bucket", {"product_id": ""})


@pytest.mark.parametrize(
    "systems,old_index,new_index,activated_product_id",
    [
        ([{"asid": "1", "pname": "SystmOne"}, {
         "asid": "2", "pname": "EMIS Web"}], 0, 1, EMIS_PRODUCT_ID),
        ([{"asid": "1", "pname": "SystmOne"}, {
         "asid": "2", "pname": "EMIS Web"}], 0, 1, EMIS_PRODUCT_ID),
        ([{"asid": "1", "pname": "SystmOne"}, {
         "asid": "2", "pname": "EMIS Web"}], 1, 0, TPP_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {
         "asid": "2", "pname": "SystmOne"}], 0, 1, TPP_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {
         "asid": "2", "pname": "SystmOne"}], 1, 0, EMIS_PRODUCT_ID),
        ([{"asid": "1", "pname": "Vision 3"}, {
         "asid": "2", "pname": "SystmOne"}], 0, 1, TPP_PRODUCT_ID),
        ([{"asid": "1", "pname": "Vision 3"}, {"asid": "2",
         "pname": "SystmOne"}], 1, 0, VISION_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {"asid": "2",
         "pname": "Vision 3"}], 0, 1, VISION_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {
         "asid": "2", "pname": "Vision 3"}], 1, 0, EMIS_PRODUCT_ID)
    ])
def test_returns_2_asids_from_same_lookup_file(
        s3, systems, old_index, new_index, activated_product_id):
    ods_code = "T55555"
    first = systems[0]
    second = systems[1]
    asid_lookup_bucket = s3.create_bucket(Bucket="test-bucket")
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [first["asid"], ods_code, "", "", first["pname"], "", ""],
                [second["asid"], ods_code, "", "", second["pname"], "", ""]
            ],
        ))

    lookup_result = lookup_asids(
        s3, "test-bucket", {"ods_code": ods_code, "product_id": activated_product_id})

    assert lookup_result["old"]["asid"] == systems[old_index]["asid"]
    assert lookup_result["new"]["asid"] == systems[new_index]["asid"]
    assert lookup_result["old"]["name"] == systems[old_index]["pname"]
    assert lookup_result["new"]["name"] == systems[new_index]["pname"]


@pytest.mark.parametrize(
    "systems,old_index,new_index,activated_product_id",
    [
        ([{"asid": "1", "pname": "SystmOne"}, {
         "asid": "2", "pname": "EMIS Web"}], 0, 1, EMIS_PRODUCT_ID),
        ([{"asid": "1", "pname": "SystmOne"}, {
         "asid": "2", "pname": "EMIS Web"}], 0, 1, EMIS_PRODUCT_ID),
        ([{"asid": "1", "pname": "SystmOne"}, {
         "asid": "2", "pname": "EMIS Web"}], 1, 0, TPP_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {
         "asid": "2", "pname": "SystmOne"}], 0, 1, TPP_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {
         "asid": "2", "pname": "SystmOne"}], 1, 0, EMIS_PRODUCT_ID),
        ([{"asid": "1", "pname": "Vision 3"}, {
         "asid": "2", "pname": "SystmOne"}], 0, 1, TPP_PRODUCT_ID),
        ([{"asid": "1", "pname": "Vision 3"}, {"asid": "2",
         "pname": "SystmOne"}], 1, 0, VISION_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {"asid": "2",
         "pname": "Vision 3"}], 0, 1, VISION_PRODUCT_ID),
        ([{"asid": "1", "pname": "EMIS Web"}, {
         "asid": "2", "pname": "Vision 3"}], 1, 0, EMIS_PRODUCT_ID)
    ])
def test_returns_2_asids_from_different_lookup_files(
        s3, systems, old_index, new_index, activated_product_id):
    ods_code = "T55555"
    first = systems[0]
    second = systems[1]
    asid_lookup_bucket = s3.create_bucket(Bucket="test-bucket")

    asid_lookup_bucket.Object("asid-lookup-1.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [first["asid"], ods_code, "", "", first["pname"], "", ""],
            ],
        ))
    asid_lookup_bucket.Object("asid-lookup-2.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                [second["asid"], ods_code, "", "", second["pname"], "", ""]
            ],
        ))

    lookup_result = lookup_asids(
        s3, "test-bucket", {"ods_code": ods_code, "product_id": activated_product_id})

    assert lookup_result["old"]["asid"] == systems[old_index]["asid"]
    assert lookup_result["new"]["asid"] == systems[new_index]["asid"]
    assert lookup_result["old"]["name"] == systems[old_index]["pname"]
    assert lookup_result["new"]["name"] == systems[new_index]["pname"]


def test_ignores_other_products(s3):
    ods_code = "T55555"
    asid_lookup_bucket = s3.create_bucket(Bucket="test-bucket")
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                ["1", ods_code, "", "", "SystmOne", "", ""],
                ["2", ods_code, "", "", "Some other product", "", ""]
            ],
        ))

    with pytest.raises(AsidLookupError):
        lookup_asids(
            s3, "test-bucket", {"ods_code": ods_code, "product_id": TPP_PRODUCT_ID})


def test_ignores_other_practices(s3):
    asid_lookup_bucket = s3.create_bucket(Bucket="test-bucket")
    asid_lookup_bucket.Object("asid-lookup.csv.gz").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[
                ["1", "odsone", "", "", "SystmOne", "", ""],
                ["2", "odsone", "", "", "EMIS Web", "", ""]
            ],
        ))

    with pytest.raises(AsidLookupError):
        lookup_asids(
            s3, "test-bucket", {"ods_code": "odstwo", "product_id": TPP_PRODUCT_ID})
