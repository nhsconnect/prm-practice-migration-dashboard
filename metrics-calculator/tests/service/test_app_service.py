import boto3
import json
import pytest
import os

from moto import mock_s3
from unittest.mock import MagicMock, Mock

from chalice.test import Client
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


@pytest.fixture(scope="function")
def test_client():
    from app import app
    with Client(app) as client:
        yield client


@pytest.fixture(scope="function")
def splunk(monkeypatch):
    request_mock = Mock()
    splunk_call_mock = Mock(return_value=MagicMock(getresponse=request_mock))
    monkeypatch.setattr("app.HTTPSConnection", splunk_call_mock)
    yield request_mock


@pytest.fixture(scope="function")
def lambda_environment_vars():
    with open('.chalice/config.json') as f:
        config = json.loads(f.read())
        yield config["stages"]["dev"]["lambda_functions"]["calculate_dashboard_metrics_from_telemetry"]["environment_variables"]


def test_calculate_dashboard_metrics_from_telemetry(
        test_client, lambda_environment_vars, s3):
    ods_code = "A12345"
    old_asid = "1234"
    new_asid = "5678"
    occurrences_bucket_name = lambda_environment_vars["OCCURRENCES_BUCKET_NAME"]
    asid_lookup_bucket_name = lambda_environment_vars["ASID_LOOKUP_BUCKET_NAME"]
    telemetry_bucket_name = lambda_environment_vars["TELEMETRY_BUCKET_NAME"]
    metrics_bucket_name = lambda_environment_vars["METRICS_BUCKET_NAME"]
    ccg = "My CCG"
    practice = "My First Surgery"
    create_occurrences_data(
        occurrences_bucket_name, s3, ods_code, ccg, practice)
    create_asid_lookup_data(
        asid_lookup_bucket_name, s3, ods_code, old_asid, new_asid)
    create_telemetry_data(telemetry_bucket_name, s3, old_asid, new_asid)
    metrics_bucket = create_metrics_bucket(metrics_bucket_name, s3)

    response = test_client.lambda_.invoke(
        'calculate_dashboard_metrics_from_telemetry')
    assert response.payload == "ok"

    migrations_obj = metrics_bucket.Object("migrations.json").get()
    migrations_body = migrations_obj['Body'].read().decode('utf-8')

    assert json.loads(migrations_body) == {
        "mean_cutover_duration": "4.0",
        "migrations": [{
            "cutover_startdate": "2021-12-02T00:00:00+00:00",
            "cutover_enddate": "2021-12-06T00:00:00+00:00",
            "cutover_duration": 4,
            "ccg_name": ccg,
            "practice_name": practice,
            "source_system": "SystmOne",
            "target_system": "EMIS Web",
            "ods_code": ods_code
        }]}


@pytest.mark.skip(reason="Won't pass until all functionality implemented")
def test_export_splunk_data(
        test_client, lambda_environment_vars, s3, splunk):
    ods_code = "A12345"
    old_asid = "1234"
    new_asid = "5678"
    occurrences_bucket_name = lambda_environment_vars["OCCURRENCES_BUCKET_NAME"]
    asid_lookup_bucket_name = lambda_environment_vars["ASID_LOOKUP_BUCKET_NAME"]
    telemetry_bucket_name = lambda_environment_vars["TELEMETRY_BUCKET_NAME"]
    ccg = "My CCG"
    practice = "My First Surgery"
    create_occurrences_data(
        occurrences_bucket_name, s3, ods_code, ccg, practice)
    create_asid_lookup_data(
        asid_lookup_bucket_name, s3, ods_code, old_asid, new_asid)
    create_mock_splunk_data(splunk, old_asid)

    response = test_client.lambda_.invoke('splunk-data-exporter')
    assert response.payload == "ok"

    pre_cutover_telemetry_obj = telemetry_bucket_name.Object(
        f"{old_asid}-telemetry.csv.gz").get()
    pre_cutover_telemetry = pre_cutover_telemetry_obj['Body'].read().decode(
        'utf-8')
    assert json.loads(pre_cutover_telemetry) == SPINE_PRE_CUTOVER_DATA

    post_cutover_telemetry_obj = telemetry_bucket_name.Object(
        f"{new_asid}-telemetry.csv.gz").get()
    post_cutover_telemetry = post_cutover_telemetry_obj['Body'].read().decode(
        'utf-8')
    assert json.loads(post_cutover_telemetry) == SPINE_POST_CUTOVER_DATA


def create_occurrences_data(occurrences_bucket_name, s3, ods_code, ccg, practice):
    occurrences_bucket = s3.create_bucket(Bucket=occurrences_bucket_name)
    occurrences_bucket.Object("activations-jun21.csv").put(
        Body=build_gzip_csv(
            header=["Service Recipient ID (e.g. ODS code where this is available)", "Change Status", "Call Off Ordering Party name", "Service Recipient Name", "Supplier ID", "Supplier Name", "Product Name ", "Product ID ",
                    "\"Product Type (Catalogue solution, Additional Service, Associated Service)\"", "M1 planned (Delivery Date)", "", "Actual M1 date", "Buyer verification date (M2)"],
            rows=[[ods_code, "Activation", ccg, practice, "10000",
                   "Emis", "Emis Web GP", "10000-001", "Catalogue Solution", "", "", "11/5/21", ""]],
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


def create_mock_splunk_data(splunk):

    splunk.return_value = [
        lambda: Mock(status=200, read=lambda: SPINE_BASELINE_DATA),
        lambda: Mock(status=200, read=lambda: SPINE_PRE_CUTOVER_DATA),
        lambda: Mock(status=200, read=lambda: SPINE_POST_CUTOVER_DATA),
    ]
