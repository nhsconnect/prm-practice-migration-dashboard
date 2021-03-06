import gzip

from chalicelib.s3 import read_object_s3, write_object_s3
from chalicelib.csv_rows import csv_rows
from botocore.exceptions import ClientError


class GetTelemetryError(RuntimeError):
    pass


def get_telemetry(s3, telemetry_bucket_name, new_telemetry_object_name):
    try:
        new_telemetry_stream = read_object_s3(
            s3, f"s3://{telemetry_bucket_name}/{new_telemetry_object_name}")
        new_telemetry_generator = csv_rows(new_telemetry_stream)
    except ClientError as e:
        raise GetTelemetryError from e
    return new_telemetry_generator


def upload_telemetry(s3, bucket_name, telemetry_data, filename, start_date, end_date):
    metadata = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    zipped_telemetry = gzip.compress(telemetry_data)
    write_object_s3(s3, f"s3://{bucket_name}/{filename}", zipped_telemetry, metadata)
