import json
import boto3
from chalice import Chalice

app = Chalice(app_name='metrics-calculator')

# TODO: Telemetry bucket name config
# TODO: Telemetry file name config
# TODO: Metrics bucket name config


@app.lambda_function()
def calculate_dashboard_metrics_from_telemetry(event, context):
    s3 = boto3.resource("s3", region_name="eu-west-2")
    migrations = {"foo": "bar"}
    s3.Object("metrics_bucket", "migrations.json").put(
        Body=json.dumps(migrations))
    return "ok"


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
