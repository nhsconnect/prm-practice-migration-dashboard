import gzip

import boto3
import json
import pytest
import os

from moto import mock_s3, mock_ssm
from unittest.mock import MagicMock, Mock

from chalice.test import Client

from chalicelib.get_patient_registration_count import PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS
from chalicelib.lookup_asids import ASID_LOOKUP_HEADERS
from tests.builders.file import build_gzip_csv


SPINE_BASELINE_DATA = b"""_time,avgmin2std
    2021-12-08T00:00:00.000+0000,200.0"""
SPINE_PRE_CUTOVER_DATA = b"""_time,count,avgmin2std
    2021-12-08T00:00:00.000+0000,20,200.0"""
SPINE_POST_CUTOVER_DATA = b"""_time,count,avgmin2std
    2021-12-08T00:00:00.000+0000,20,200.0"""


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


@pytest.fixture(scope='function')
def ssm(aws_credentials):
    with mock_ssm():
        yield boto3.client('ssm', region_name='eu-west-2')


@pytest.fixture(scope="function")
def test_client():
    from app import app
    with Client(app) as client:
        yield client


@pytest.fixture(scope="function")
def splunk_response(monkeypatch):
    response_mock = Mock()
    connection_mock = Mock(return_value=MagicMock(getresponse=response_mock))
    monkeypatch.setattr(
        "chalicelib.get_data_from_splunk.HTTPSConnection", connection_mock)
    yield response_mock


@pytest.fixture(scope="function")
def calculator_lambda_env_vars():
    with open(".chalice/config.json") as f:
        config = json.loads(f.read())
        vars = config["stages"]["dev"]["lambda_functions"]["calculate_dashboard_metrics_from_telemetry"]["environment_variables"]
        for key in vars:
            os.environ[key] = vars[key]
        yield vars


@pytest.fixture(scope="function")
def exporter_lambda_env_vars():
    with open(".chalice/config.json") as f:
        config = json.loads(f.read())
        vars = config["stages"]["dev"]["lambda_functions"]["export_splunk_data"]["environment_variables"]
        for key in vars:
            os.environ[key] = vars[key]
        yield vars


def test_calculate_dashboard_metrics_from_telemetry(
        test_client, calculator_lambda_env_vars, s3):
    ods_code = "A12345"
    old_asid = "1234"
    new_asid = "5678"
    occurrences_bucket_name = calculator_lambda_env_vars["OCCURRENCES_BUCKET_NAME"]
    asid_lookup_bucket_name = calculator_lambda_env_vars["ASID_LOOKUP_BUCKET_NAME"]
    telemetry_bucket_name = calculator_lambda_env_vars["TELEMETRY_BUCKET_NAME"]
    patient_registrations_bucket_name = calculator_lambda_env_vars["PATIENT_REGISTRATIONS_BUCKET_NAME"]
    metrics_bucket_name = calculator_lambda_env_vars["METRICS_BUCKET_NAME"]
    ccg = "My CCG"
    practice = "My First Surgery"
    create_occurrences_data(
        occurrences_bucket_name, s3, ods_code, ccg, practice)
    create_asid_lookup_data(
        asid_lookup_bucket_name, s3, ods_code, old_asid, new_asid)
    create_patient_registrations_data(patient_registrations_bucket_name, s3, ods_code)
    create_telemetry_data(telemetry_bucket_name, s3, old_asid, new_asid)
    metrics_bucket = create_metrics_bucket(metrics_bucket_name, s3)

    response = test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry')
    assert response.payload == "ok"

    migrations_obj = metrics_bucket.Object("migrations.json").get()
    migrations_body = migrations_obj['Body'].read().decode('utf-8')

    assert json.loads(migrations_body) == {
        "mean_cutover_duration": 4.0,
        "supplier_combination_stats": [{
            "source_system": "SystmOne",
            "target_system": "EMIS Web",
            "count": 1,
            "mean_duration": 4
        }],
        "migrations": [{
            "cutover_startdate": "2021-12-02T00:00:00+00:00",
            "cutover_enddate": "2021-12-06T00:00:00+00:00",
            "cutover_duration": 4,
            "ccg_name": ccg,
            "practice_name": practice,
            "patient_registration_count": 1000,
            "source_system": "SystmOne",
            "target_system": "EMIS Web",
            "ods_code": ods_code
        }]}


def test_export_splunk_data(
        test_client, exporter_lambda_env_vars, s3, ssm, splunk_response):
    ods_code = "A12345"
    old_asid = "1234"
    new_asid = "5678"
    occurrences_bucket_name = exporter_lambda_env_vars["OCCURRENCES_BUCKET_NAME"]
    asid_lookup_bucket_name = exporter_lambda_env_vars["ASID_LOOKUP_BUCKET_NAME"]
    telemetry_bucket_name = exporter_lambda_env_vars["TELEMETRY_BUCKET_NAME"]
    telemetry_bucket = s3.create_bucket(Bucket=telemetry_bucket_name)
    ccg = "My CCG"
    practice = "My First Surgery"
    set_splunk_api_token(ssm)
    create_occurrences_data(
        occurrences_bucket_name, s3, ods_code, ccg, practice)
    create_asid_lookup_data(
        asid_lookup_bucket_name, s3, ods_code, old_asid, new_asid)
    create_mock_splunk_data(splunk_response)

    response = test_client.lambda_.invoke('splunk-data-exporter')
    assert response.payload == "ok"

    pre_cutover_telemetry_obj = telemetry_bucket.Object(
        f"{old_asid}-telemetry.csv.gz").get()
    pre_cutover_telemetry = pre_cutover_telemetry_obj['Body'].read()
    unzipped_pre_cutover_telemetry = gzip.decompress(pre_cutover_telemetry)
    assert unzipped_pre_cutover_telemetry == SPINE_PRE_CUTOVER_DATA

    post_cutover_telemetry_obj = telemetry_bucket.Object(
        f"{new_asid}-telemetry.csv.gz").get()
    post_cutover_telemetry = post_cutover_telemetry_obj['Body'].read()
    unzipped_post_cutover_telemetry = gzip.decompress(post_cutover_telemetry)
    assert unzipped_post_cutover_telemetry == SPINE_POST_CUTOVER_DATA


def set_splunk_api_token(ssm):
    ssm.put_parameter(
        Name="/prod/splunk-api-token",
        KeyId="a-test-key",
        Value="a-splunk-token",
        Type="SecureString")


def create_occurrences_data(occurrences_bucket_name, s3, ods_code, ccg, practice):
    occurrences_bucket = s3.create_bucket(Bucket=occurrences_bucket_name)
    occurrences_bucket.Object("activations-jun21.csv").put(
        Body=build_gzip_csv(
            header=["Service Recipient ID (e.g. ODS code where this is available)", "Change Status", "Call Off Ordering Party name", "Service Recipient Name", "Supplier ID", "Supplier Name", "Product Name ", "Product ID ",
                    "\"Product Type (Catalogue solution, Additional Service, Associated Service)\"", "M1 planned (Delivery Date)", "", "Actual M1 date", "Buyer verification date (M2)"],
            rows=[[ods_code, "Activation", ccg, practice, "10000",
                   "Emis", "Emis Web GP", "10000-001", "Catalogue Solution", "", "", "11/5/2021", ""]],
        )
    )


def create_asid_lookup_data(asid_lookup_bucket_name, s3, ods_code, old_asid, new_asid):
    asid_lookup_bucket = s3.create_bucket(Bucket=asid_lookup_bucket_name)
    asid_lookup_bucket.Object("activations-mar22").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[[old_asid, ods_code, "My First Surgery",
                   "THE PHOENIX PARTNERSHIP", "SystmOne", "GP Practice", "W1F 0UR"]],
        )
    )
    asid_lookup_bucket.Object("activations-apr22").put(
        Body=build_gzip_csv(
            header=ASID_LOOKUP_HEADERS,
            rows=[[new_asid, ods_code, "My First Surgery",
                   "EGTON MEDICAL INFORMATION SYSTEMS LTD (EMIS)", "EMIS Web", "GP Practice", "W1F 0UR"]],
        )
    )


def create_patient_registrations_data(patient_registrations_bucket_name, s3, ods_code):
    patient_registrations_bucket = s3.create_bucket(Bucket=patient_registrations_bucket_name)

    patient_registrations_bucket.Object("july-2021-patient-registration-data.csv.gz").put(
        Body=build_gzip_csv(
            header=PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS,
            rows=[
                ["", "", "", "", "", ods_code, "", "", "", "1000"]
            ],
        ))


def create_telemetry_data(bucket_name, s3, old_asid, new_asid):
    telemetry_bucket = s3.create_bucket(Bucket=bucket_name)
    telemetry_bucket.Object(f"{old_asid}-telemetry.csv.gz").put(
        Body=build_gzip_csv(
            header=["_time", "count", "avgmin2std"],
            rows=[["2021-11-25T00:00:00.000+0000", "2000", "1044.7268404372467"],
                  ["2021-11-26T00:00:00.000+0000", "2854", "1044.7268404372467"],
                  ["2021-11-27T00:00:00.000+0000", "2754", "1044.7268404372467"],
                  ["2021-12-02T00:00:00.000+0000", "200", "1044.7268404372467"],
                  ["2021-12-03T00:00:00.000+0000", "200", "1044.7268404372467"],
                  ["2021-12-04T00:00:00.000+0000", "200", "1044.7268404372467"]],
        )
    )
    telemetry_bucket.Object(f"{new_asid}-telemetry.csv.gz").put(
        Body=build_gzip_csv(
            header=["_time", "count", "avgmin2std"],
            rows=[["2021-12-05T00:00:00.000+0000", "300", "1044.7268404372467"],
                  ["2021-12-06T00:00:00.000+0000", "2854", "1044.7268404372467"],
                  ["2021-12-07T00:00:00.000+0000", "2754", "1044.7268404372467"],
                  ["2021-12-08T00:00:00.000+0000", "2554", "1044.7268404372467"]],
        )
    )


def create_metrics_bucket(metrics_bucket_name, s3):
    metrics_bucket = s3.create_bucket(Bucket=metrics_bucket_name)
    return metrics_bucket


def create_mock_splunk_data(splunk_response):

    splunk_response.side_effect = [
        Mock(status=200, read=lambda: SPINE_BASELINE_DATA),
        Mock(status=200, read=lambda: SPINE_PRE_CUTOVER_DATA),
        Mock(status=200, read=lambda: SPINE_POST_CUTOVER_DATA),
    ]
