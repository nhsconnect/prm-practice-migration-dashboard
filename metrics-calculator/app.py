import json
import os
import boto3
from chalice import Chalice

from chalicelib.metrics_engine import calculate_cutover_start_and_end_date
from chalicelib.s3 import read_object_s3, write_object_s3
from chalicelib.csv_rows import csv_rows

app = Chalice(app_name='metrics-calculator')


@app.lambda_function()
def calculate_dashboard_metrics_from_telemetry(event, context):
    old_asid = event['oldAsid']
    new_asid = event['newAsid']
    ods_code = event["odsCode"]

    telemetry_bucket_name = os.environ['TELEMETRY_BUCKET_NAME']
    old_telemetry_object_name = f"{old_asid}-telemetry.csv.gz"
    new_telemetry_object_name = f"{new_asid}-telemetry.csv.gz"
    s3 = boto3.resource("s3", region_name="eu-west-2")

    old_telemetry_generator = get_telemetry(
        s3, telemetry_bucket_name, old_telemetry_object_name)
    new_telemetry_generator = get_telemetry(
        s3, telemetry_bucket_name, new_telemetry_object_name)

    migration = calculate_cutover_start_and_end_date(
        old_telemetry_generator, new_telemetry_generator)

    org_details = get_org_details(ods_code)

    migrations = {"migrations": [migration | org_details]}
    upload_migrations(s3, migrations)
    return "ok"


def upload_migrations(s3, migrations):
    metrics_bucket_name = os.environ["METRICS_BUCKET_NAME"]
    write_object_s3(
        s3, f"s3://{metrics_bucket_name}/migrations.json", json.dumps(migrations))


def get_telemetry(s3, telemetry_bucket_name, new_telemetry_object_name):
    new_telemetry_stream = read_object_s3(
        s3, f"s3://{telemetry_bucket_name}/{new_telemetry_object_name}")
    new_telemetry_generator = csv_rows(new_telemetry_stream)
    return new_telemetry_generator


def get_org_details(ods_code):
    return {
        "practice_name": "Example practice",
        "ccg_name": "Greater Example",
        "source_system": "Ye Olde System",
        "target_system": "Shiny NU",
    }
