from decimal import ROUND_HALF_UP, Decimal
import json
import logging
import os
from statistics import fmean
from chalice import Chalice

from chalicelib.get_data_from_splunk import get_baseline_threshold_from_splunk_data
from chalicelib.lookup_asids import AsidLookupError, lookup_asids
from chalicelib.metrics_engine import calculate_cutover_start_and_end_date
from chalicelib.migration_occurrences import get_migration_occurrences
from chalicelib.s3 import get_s3_resource, write_object_s3
from chalicelib.telemetry import get_telemetry
from chalicelib.calculate_date_range import calculate_baseline_date_range, calculate_pre_cutover_date_range, calculate_post_cutover_date_range

app = Chalice(app_name='metrics-calculator')


@app.lambda_function()
def calculate_dashboard_metrics_from_telemetry(event, context):
    occurrences_bucket_name = os.environ['OCCURRENCES_BUCKET_NAME']
    asid_lookup_bucket_name = os.environ['ASID_LOOKUP_BUCKET_NAME']
    telemetry_bucket_name = os.environ['TELEMETRY_BUCKET_NAME']
    s3 = get_s3_resource()
    known_migrations = get_migration_occurrences(
        s3, occurrences_bucket_name)

    metrics = []
    for migration in known_migrations:
        try:
            asid_lookup = lookup_asids(
                s3, asid_lookup_bucket_name, migration)
            old_telemetry_object_name = f"{asid_lookup['old']['asid']}-telemetry.csv.gz"
            new_telemetry_object_name = f"{asid_lookup['new']['asid']}-telemetry.csv.gz"

            old_telemetry_generator = get_telemetry(
                s3, telemetry_bucket_name, old_telemetry_object_name)
            new_telemetry_generator = get_telemetry(
                s3, telemetry_bucket_name, new_telemetry_object_name)

            migration_metrics = calculate_cutover_start_and_end_date(
                old_telemetry_generator, new_telemetry_generator)

            org_details = {
                "ods_code": migration["ods_code"],
                "ccg_name": migration["ccg_name"],
                "practice_name": migration["practice_name"],
            }
            system_details = {
                "source_system": asid_lookup["old"]["name"],
                "target_system": asid_lookup["new"]["name"]
            }
            metrics.append(migration_metrics | org_details | system_details)
        except AsidLookupError:
            logging.error("Couldn't find ASIDs for migration", exc_info=True)

    if len(metrics) > 0:
        mean_cutover = calculate_mean_cutover(metrics)

        migrations = {
            "mean_cutover_duration": mean_cutover,
            "migrations": metrics
        }
        upload_migrations(s3, migrations)

    return "ok"


@app.lambda_function(name='export-splunk-data')
def export_splunk_data(event, context):
    occurrences_bucket_name = os.environ['OCCURRENCES_BUCKET_NAME']
    asid_lookup_bucket_name = os.environ['ASID_LOOKUP_BUCKET_NAME']
    telemetry_bucket_name = os.environ['TELEMETRY_BUCKET_NAME']

    s3 = get_s3_resource()
    known_migrations = get_migration_occurrences(
        s3, occurrences_bucket_name)

    for migration in known_migrations:
        asid_lookup = lookup_asids(
            s3, asid_lookup_bucket_name, migration)
        old_asid = asid_lookup["old"]["asid"]
        new_asid = asid_lookup["new"]["asid"]

        baseline_date_range = calculate_baseline_date_range(
            migration["date"])
        pre_cutover_date_range = calculate_pre_cutover_date_range(
            migration["date"])
        post_cutover_date_range = calculate_post_cutover_date_range(
            migration["date"])

        baseline_threshold = get_baseline_threshold_from_splunk_data(
            old_asid, baseline_date_range)

        pre_cutover_telemetry = get_telemetry_from_splunk(
            old_asid,
            baseline_threshold,
            pre_cutover_date_range
        )
        post_cutover_telemetry = get_telemetry_from_splunk(
            new_asid,
            baseline_threshold,
            post_cutover_date_range
        )

        pre_cutover_telemetry_filename = f"{old_asid}-telemetry.csv.gz"
        post_cutover_telemetry_filename = f"{new_asid}-telemetry.csv.gz"
        upload_telemetry(s3, telemetry_bucket_name, pre_cutover_telemetry, pre_cutover_telemetry_filename)
        upload_telemetry(s3, telemetry_bucket_name, post_cutover_telemetry, post_cutover_telemetry_filename)

    return "ok"


def upload_migrations(s3, migrations):
    metrics_bucket_name = os.environ["METRICS_BUCKET_NAME"]
    write_object_s3(
        s3, f"s3://{metrics_bucket_name}/migrations.json", json.dumps(migrations))


def calculate_mean_cutover(metrics):
    durations = map(lambda x: x["cutover_duration"], metrics)
    mean = fmean(durations)
    rounded_mean = Decimal(mean).quantize(
        Decimal('.1'), rounding=ROUND_HALF_UP)
    return f"{rounded_mean}"


def get_telemetry_from_splunk(asid, baseline_threshold, date_range):
    pass


def upload_telemetry(s3, bucket_name, telemetry_data, filename):
    pass
