from datetime import date

import boto3
import os
import pytest

from moto import mock_s3

from chalicelib.get_patient_registration_count import get_patient_registration_count, PatientRegistrationsError, \
    PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS
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


def test_get_patient_registration_count_returns_number_of_patients_for_a_given_practice(s3):
    ods_code = "ods-code"
    migration = {
        "ods_code": ods_code,
        "date": date(2021, 7, 11)
    }
    bucket_name = "test-bucket"
    patient_registrations_bucket = s3.create_bucket(Bucket=bucket_name)

    patient_registrations_bucket.Object("july-2021-patient-registration-data.csv.gz").put(
        Body=build_gzip_csv(
            header=PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS,
            rows=[
                ["", "", "", "", "", ods_code, "", "", "", "1000"]
            ],
        ))

    result = get_patient_registration_count(s3, bucket_name, migration)

    expected_result = 1000

    assert result == expected_result


def test_get_patient_registration_count_raises_error_if_ods_code_not_found(s3):
    ods_code = "ods-code"
    migration = {
        "ods_code": ods_code,
        "date": date(2021, 7, 11)
    }
    other_ods_code = "other-ods-code"
    bucket_name = "test-bucket"
    patient_registrations_bucket = s3.create_bucket(Bucket=bucket_name)

    patient_registrations_bucket.Object("july-2021-patient-registration-data.csv.gz").put(
        Body=build_gzip_csv(
            header=PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS,
            rows=[
                ["", "", "", "", "", other_ods_code, "", "", "", "1000"]
            ],
        ))

    with pytest.raises(PatientRegistrationsError, match="ODS code ods-code not found"):
        get_patient_registration_count(s3, bucket_name, migration)


def test_get_patient_registration_count_returns_number_of_patients_for_a_given_practice_during_a_migration(s3):
    ods_code = "ods-code"
    migration = {
        "ods_code": ods_code,
        "date": date(2021, 7, 11)
    }
    bucket_name = "test-bucket"
    patient_registrations_bucket = s3.create_bucket(Bucket=bucket_name)

    patient_registrations_bucket.Object("july-2021-patient-registration-data.csv.gz").put(
        Body=build_gzip_csv(
            header=PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS,
            rows=[
                ["", "", "", "", "", ods_code, "", "", "", "1000"]
            ],
        ))
    patient_registrations_bucket.Object("june-2021-patient-registration-data.csv.gz").put(
        Body=build_gzip_csv(
            header=PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS,
            rows=[
                ["", "", "", "", "", ods_code, "", "", "", "2000"]
            ],
        ))

    result = get_patient_registration_count(s3, bucket_name, migration)

    expected_result = 1000

    assert result == expected_result


def test_get_patient_registration_count_returns_error_if_migration_month_data_is_not_found(s3):
    ods_code = "ods-code"
    migration = {
        "ods_code": ods_code,
        "date": date(2021, 7, 11)
    }
    bucket_name = "test-bucket"
    patient_registrations_bucket = s3.create_bucket(Bucket=bucket_name)

    patient_registrations_bucket.Object("june-2021-patient-registration-data.csv.gz").put(
        Body=build_gzip_csv(
            header=PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS,
            rows=[
                ["", "", "", "", "", ods_code, "", "", "", "1000"]
            ],
        ))

    with pytest.raises(PatientRegistrationsError, match="Data for july-2021 not found"):
        get_patient_registration_count(s3, bucket_name, migration)
