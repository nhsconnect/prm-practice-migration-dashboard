from dateutil.parser import parse

from chalicelib.csv_rows import csv_rows


EMIS_SUPPLIER_ID = "10000"
VISION_SUPPLIER_ID = "10034"
TPP_SUPPLIER_ID = "10052"

EMIS_PRODUCT_ID = "10000-001"
TPP_PRODUCT_ID = "10052-002"
VISION_PRODUCT_ID = "10034-005"


def get_migration_occurrences(s3, bucket_name):
    occurrences_bucket = s3.Bucket(bucket_name)
    known_migrations = []
    for object in occurrences_bucket.objects.all():
        rows = csv_rows(object.get()["Body"])
        for row in rows:
            if row["Supplier ID"] not in [
                    EMIS_SUPPLIER_ID, VISION_SUPPLIER_ID, TPP_SUPPLIER_ID]:
                continue

            migration = _parse_migration(row)
            known_migrations.append(migration)
    return known_migrations


def _parse_migration(row):
    date_str = row["Actual M1 date"]
    migration = {
        "ods_code": row["Service Recipient ID (e.g. ODS code where this is available)"],
        "ccg_name": row["Call Off Ordering Party name"],
        "practice_name": row["Service Recipient Name"],
        "supplier_id": row["Supplier ID"],
        "product_id": row["Product ID "],
        "date": parse(date_str)
    }

    return migration
