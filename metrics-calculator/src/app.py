import json
import boto3
from chalice import Chalice
from src.metrics_engine import calculate_cutover_start_and_end_date

from src.read_object_s3 import read_object_s3
from src.csv_rows import csv_rows

app = Chalice(app_name='metrics-calculator')

# TODO: Telemetry bucket name config
# TODO: Telemetry file name config
# TODO: Metrics bucket name config


@app.lambda_function()
def calculate_dashboard_metrics_from_telemetry(event, context):
    s3 = boto3.resource("s3", region_name="eu-west-2")
    telemetry_bucket_name = "telemetry_bucket"

    old_telemetry_object_name = f"{event['oldAsid']}-telemetry.csv"
    old_telemetry_stream = read_object_s3(
        s3, f"s3://{telemetry_bucket_name}/{old_telemetry_object_name}")
    old_telemetry_generator = csv_rows(old_telemetry_stream)

    new_telemetry_object_name = f"{event['newAsid']}-telemetry.csv"
    new_telemetry_stream = read_object_s3(
        s3, f"s3://{telemetry_bucket_name}/{new_telemetry_object_name}")
    new_telemetry_generator = csv_rows(new_telemetry_stream)

    migration = calculate_cutover_start_and_end_date(
        old_telemetry_generator, new_telemetry_generator)

    org_details = get_org_details(event["odsCode"])

    migrations = {"migrations": [migration | org_details]}
    metrics_bucket_name = "metrics_bucket"
    s3.Object(metrics_bucket_name, "migrations.json").put(
        Body=json.dumps(migrations))
    return "ok"


def get_org_details(ods_code):
    return {
        "practice_name": "Example practice",
        "ccg_name": "Greater Example",
        "source_system": "Ye Olde System",
        "target_system": "Shiny NU",
    }


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
