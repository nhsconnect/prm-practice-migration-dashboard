import json
import logging
import os
from chalice import Chalice

from chalicelib.lookup_asids import AsidLookupError, lookup_asids
from chalicelib.metrics_engine import calculate_cutover_start_and_end_date
from chalicelib.migration_occurrences import get_migration_occurrences
from chalicelib.s3 import get_s3_resource, write_object_s3
from chalicelib.telemetry import get_telemetry

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

    migrations = {"migrations": metrics}
    upload_migrations(s3, migrations)
    return "ok"


def upload_migrations(s3, migrations):
    metrics_bucket_name = os.environ["METRICS_BUCKET_NAME"]
    write_object_s3(
        s3, f"s3://{metrics_bucket_name}/migrations.json", json.dumps(migrations))
