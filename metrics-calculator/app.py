import boto3
import json
import logging
import os
from decimal import ROUND_HALF_UP, Decimal
from chalice import Chalice
from statistics import fmean

from chalicelib.get_data_from_splunk import get_telemetry_from_splunk, get_baseline_telemetry_from_splunk, \
    parse_threshold_from_telemetry, SplunkTelemetryMissing
from chalicelib.get_patient_registration_count import get_patient_registration_count, PatientRegistrationsError
from chalicelib.get_splunk_api_token import get_splunk_api_token
from chalicelib.lookup_all_asids import lookup_all_asids, AsidLookupError
from chalicelib.metrics_engine import calculate_cutover_start_and_end_date, \
    calculate_migrations_stats_per_supplier_combination
from chalicelib.migration_occurrences import get_migration_occurrences
from chalicelib.s3 import get_s3_resource, write_object_s3, objects_exist
from chalicelib.telemetry import get_telemetry, upload_telemetry, GetTelemetryError
from chalicelib.calculate_date_range import calculate_baseline_date_range, calculate_pre_cutover_date_range, \
    calculate_post_cutover_date_range

app = Chalice(app_name='metrics-calculator')
logger = logging.getLogger("Metrics Calculator")
logger.setLevel(logging.DEBUG)


@app.lambda_function()
def calculate_dashboard_metrics_from_telemetry(event, context):
    occurrences_bucket_name = os.environ['OCCURRENCES_BUCKET_NAME']
    asid_lookup_bucket_name = os.environ['ASID_LOOKUP_BUCKET_NAME']
    telemetry_bucket_name = os.environ['TELEMETRY_BUCKET_NAME']
    patient_registrations_bucket_name = os.environ['PATIENT_REGISTRATIONS_BUCKET_NAME']
    s3 = get_s3_resource()
    known_migrations = get_migration_occurrences(
        s3, occurrences_bucket_name)
    asids_lookup = lookup_all_asids(s3, asid_lookup_bucket_name, known_migrations)

    metrics = []
    for migration in known_migrations:
        try:
            ods_code = migration["ods_code"]
            asid_lookup = get_asids_for_ods_code(asids_lookup, ods_code)
            old_asid = asid_lookup["old"]["asid"]
            logger.debug(f"Old asid: {old_asid}")
            new_asid = asid_lookup["new"]["asid"]
            logger.debug(f"New asid: {new_asid}")
            old_telemetry_object_name = f"{old_asid}-telemetry.csv.gz"
            new_telemetry_object_name = f"{new_asid}-telemetry.csv.gz"

            old_telemetry_generator = get_telemetry(
                s3, telemetry_bucket_name, old_telemetry_object_name)
            new_telemetry_generator = get_telemetry(
                s3, telemetry_bucket_name, new_telemetry_object_name)

            migration_metrics = calculate_cutover_start_and_end_date(
                old_telemetry_generator, new_telemetry_generator)

            org_details = {
                "ods_code": ods_code,
                "ccg_name": migration["ccg_name"],
                "practice_name": migration["practice_name"]
            }

            try:
                patient_registration_count = get_patient_registration_count(
                    s3, patient_registrations_bucket_name, migration)
                org_details["patient_registration_count"] = patient_registration_count
            except PatientRegistrationsError as e:
                logging.error("Couldn't find patient registration count for migration", exc_info=True)

            system_details = {
                "source_system": asid_lookup["old"]["name"],
                "target_system": asid_lookup["new"]["name"]
            }
            metrics.append(migration_metrics | org_details | system_details)
        except AsidLookupError:
            logging.error("Couldn't find ASIDs for migration", exc_info=True)
        except GetTelemetryError:
            logging.error("Couldn't get telemetry for migration", exc_info=True)

    if len(metrics) > 0:
        mean_cutover = calculate_mean_cutover(metrics)
        supplier_combination_stats = calculate_migrations_stats_per_supplier_combination(metrics)

        migrations = {
            "mean_cutover_duration": mean_cutover,
            "supplier_combination_stats": supplier_combination_stats,
            "migrations": metrics
        }
        upload_migrations(s3, migrations)

    return "ok"


@app.lambda_function(name='splunk-data-exporter')
def export_splunk_data(event, context):
    occurrences_bucket_name = os.environ['OCCURRENCES_BUCKET_NAME']
    asid_lookup_bucket_name = os.environ['ASID_LOOKUP_BUCKET_NAME']
    telemetry_bucket_name = os.environ['TELEMETRY_BUCKET_NAME']
    splunk_host = os.environ['SPLUNK_HOST']

    s3 = get_s3_resource()
    known_migrations = get_migration_occurrences(
        s3, occurrences_bucket_name)
    number_of_successful_exports = 0

    if len(known_migrations) > 0:
        ssm = get_ssm_client()
        splunk_token = get_splunk_api_token(ssm, "/prod/splunk-api-token")
        asids_lookup = lookup_all_asids(s3, asid_lookup_bucket_name, known_migrations)
        for migration in known_migrations:
            try:
                export_data_for_migration(
                    migration, s3, asids_lookup, telemetry_bucket_name, splunk_token, splunk_host)
                number_of_successful_exports += 1
            except AsidLookupError:
                logger.error("Error finding ASIDs", exc_info=True)
            except SplunkTelemetryMissing:
                logger.error("No telemetry found", exc_info=True)
    logger.info(
        f"Processed {len(known_migrations)} migrations, {number_of_successful_exports} exported successfully")
    return "ok"


def export_data_for_migration(migration, s3, asids_lookup, telemetry_bucket_name, splunk_token, splunk_host):
    ods_code = migration["ods_code"]
    logger.debug(f"ODS code: {ods_code}")
    asid_lookup = get_asids_for_ods_code(asids_lookup, ods_code)
    old_asid = asid_lookup["old"]["asid"]
    logger.debug(f"Old asid: {old_asid}")
    new_asid = asid_lookup["new"]["asid"]
    logger.debug(f"New asid: {new_asid}")

    baseline_telemetry_filename = f"{old_asid}-baseline-telemetry.csv.gz"
    pre_cutover_telemetry_filename = f"{old_asid}-telemetry.csv.gz"
    post_cutover_telemetry_filename = f"{new_asid}-telemetry.csv.gz"

    telemetry_filenames = [baseline_telemetry_filename, pre_cutover_telemetry_filename, post_cutover_telemetry_filename]
    if objects_exist(s3, telemetry_bucket_name, telemetry_filenames):
        logger.debug("Existing files present in bucket - skipping further processing")
        return

    logger.debug("Querying splunk for telemetry data")
    baseline_date_range = calculate_baseline_date_range(
        migration["date"])
    logger.debug(
        f"Baseline date range: start date: {baseline_date_range['start_date']}, end date: {baseline_date_range['end_date']}")
    pre_cutover_date_range = calculate_pre_cutover_date_range(
        migration["date"])
    logger.debug(
        f"Pre-cutover date range: start date: {pre_cutover_date_range['start_date']}, end date: {pre_cutover_date_range['end_date']}")
    post_cutover_date_range = calculate_post_cutover_date_range(
        migration["date"])
    logger.debug(
        f"Post-cutover date range: start date: {post_cutover_date_range['start_date']}, end date: {post_cutover_date_range['end_date']}")

    baseline_telemetry = get_baseline_telemetry_from_splunk(
        splunk_host, splunk_token, old_asid, baseline_date_range)
    baseline_threshold = parse_threshold_from_telemetry(baseline_telemetry)
    logger.debug(f"Baseline threshold value: {baseline_threshold}")

    pre_cutover_telemetry = get_telemetry_from_splunk(
        splunk_host,
        splunk_token,
        old_asid,
        pre_cutover_date_range,
        baseline_threshold
    )
    post_cutover_telemetry = get_telemetry_from_splunk(
        splunk_host,
        splunk_token,
        new_asid,
        post_cutover_date_range,
        baseline_threshold
    )

    if pre_cutover_telemetry and post_cutover_telemetry:
        logger.debug("Uploading exported splunk data")
        upload_telemetry(
            s3,
            telemetry_bucket_name,
            baseline_telemetry,
            baseline_telemetry_filename,
            baseline_date_range['start_date'],
            baseline_date_range['end_date'])
        upload_telemetry(
            s3,
            telemetry_bucket_name,
            pre_cutover_telemetry,
            pre_cutover_telemetry_filename,
            pre_cutover_date_range['start_date'],
            pre_cutover_date_range['end_date'])
        upload_telemetry(
            s3,
            telemetry_bucket_name,
            post_cutover_telemetry,
            post_cutover_telemetry_filename,
            post_cutover_date_range['start_date'],
            post_cutover_date_range['end_date'])
        logger.debug("Files successfully uploaded")
    else:
        logger.debug(f"No telemetry files uploaded for {ods_code}")


def get_ssm_client():
    return boto3.client("ssm", region_name="eu-west-2")


def upload_migrations(s3, migrations):
    metrics_bucket_name = os.environ["METRICS_BUCKET_NAME"]
    write_object_s3(
        s3, f"s3://{metrics_bucket_name}/migrations.json", json.dumps(migrations))


def calculate_mean_cutover(metrics):
    durations = map(lambda x: x["cutover_duration"], metrics)
    mean = fmean(durations)
    rounded_mean = Decimal(mean).quantize(
        Decimal('.1'), rounding=ROUND_HALF_UP)
    return float(rounded_mean)


def get_asids_for_ods_code(asids_lookup, ods_code):
    asid_lookup = asids_lookup[ods_code]
    if len(asid_lookup["old"]["asid"]) == 0 and len(asid_lookup["new"]["asid"]) == 0:
        raise AsidLookupError(f"No ASIDs found for the ODS code \"{ods_code}\"")
    elif len(asid_lookup["old"]["asid"]) == 0:
        raise AsidLookupError(f"Only new ASID found for the ODS code \"{ods_code}\"")
    elif len(asid_lookup["new"]["asid"]) == 0:
        raise AsidLookupError(f"Only old ASID found for the ODS code \"{ods_code}\"")
    return asid_lookup
