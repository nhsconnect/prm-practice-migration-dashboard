from chalicelib.s3 import read_object_s3
from chalicelib.csv_rows import csv_rows


def get_telemetry(s3, telemetry_bucket_name, new_telemetry_object_name):
    new_telemetry_stream = read_object_s3(
        s3, f"s3://{telemetry_bucket_name}/{new_telemetry_object_name}")
    new_telemetry_generator = csv_rows(new_telemetry_stream)
    return new_telemetry_generator
