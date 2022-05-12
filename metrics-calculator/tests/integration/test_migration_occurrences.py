import boto3
import os
import pytest

from datetime import datetime
from moto import mock_s3

from chalicelib.migration_occurrences import get_migration_occurrences
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


def test_returns_empty_list_when_there_are_no_migration_files(s3):
    occurrences_bucket = s3.create_bucket(Bucket="test-bucket")

    known_migrations = get_migration_occurrences(s3, occurrences_bucket.name)

    assert len(known_migrations) == 0


@pytest.mark.parametrize(
    "expected_supplier_id,expected_product_id",
    [
        ("10000", "10000-001"),
        ("10052", "10052-002"),
        ("10034", "10034-005")
    ])
def test_returns_migration_data_for_foundation_supplier_solutions(s3, expected_supplier_id, expected_product_id):
    occurrences_bucket = s3.create_bucket(Bucket="test-bucket")
    expected_ods_code = "T54321"
    expected_ccg = "A Test CCG"
    expected_practice = "A Test Practice"
    upload_test_migration_occurrences(
        occurrences_bucket, expected_ods_code, expected_ccg, expected_practice, expected_supplier_id, expected_product_id)

    known_migrations = get_migration_occurrences(s3, occurrences_bucket.name)

    assert len(known_migrations) == 1
    migration = known_migrations[0]
    assert migration["ods_code"] == expected_ods_code
    assert migration["ccg_name"] == expected_ccg
    assert migration["practice_name"] == expected_practice
    assert migration["supplier_id"] == expected_supplier_id
    assert migration["product_id"] == expected_product_id
    assert migration["date"] == datetime(2021, 5, 11)


def test_does_not_return_data_for_other_solutions(s3):
    occurrences_bucket = s3.create_bucket(Bucket="test-bucket")
    upload_test_migration_occurrences(
        occurrences_bucket, "T54321", "A Test CCG", "A Test Practice", "10046", "10046-001")

    known_migrations = get_migration_occurrences(s3, occurrences_bucket.name)

    assert len(known_migrations) == 0


def upload_test_migration_occurrences(
        occurrences_bucket,
        expected_ods_code,
        expected_ccg,
        expected_practice,
        expected_supplier_id,
        expected_product_id):
    occurrences_bucket.Object("activations-jun21.csv").put(
        Body=build_gzip_csv(
            header=["Service Recipient ID (e.g. ODS code where this is available)", "Change Status", "Call Off Ordering Party name", "Service Recipient Name", "Supplier ID", "Supplier Name", "Product Name ",
                    "Product ID ", "\"Product Type (Catalogue solution, Additional Service, Associated Service)\"", "M1 planned (Delivery Date)", "", "Actual M1 date", "Buyer verification date (M2)"],
            rows=[[expected_ods_code, "Activation", expected_ccg, expected_practice, expected_supplier_id, "", "",
                   expected_product_id, "Catalogue Solution", "", "", "11/5/2021", ""]],
        )
    )
