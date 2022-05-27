from chalicelib.csv_rows import csv_rows
from chalicelib.migration_occurrences import EMIS_PRODUCT_ID, TPP_PRODUCT_ID, VISION_PRODUCT_ID


class AsidLookupError(Exception):
    pass


ASID_LOOKUP_HEADERS = [
    "ASID", "NACS", "OrgName", "MName", "PName", "OrgType", "PostCode"]


def lookup_all_asids(s3, bucket_name, migrations):
    result = {}
    if len(migrations) == 0:
        return result
    asid_lookup_bucket = s3.Bucket(bucket_name)
    for lookup_file in asid_lookup_bucket.objects.all():
        rows = list(csv_rows(lookup_file.get()["Body"]))
        for migration in migrations:
            ods_code = migration["ods_code"]
            asids = {"old": {"asid": "", "name": ""}, "new": {"asid": "", "name": ""}}
            if ods_code not in result:
                result[ods_code] = asids
            current_file_result = find_asids_in_file(migration, ods_code, rows)
            result[ods_code] |= current_file_result
    if len(result) == 0:
        raise AsidLookupError(f"Bucket {bucket_name} is empty")
    return result


def find_asids_in_file(migration, ods_code, rows):
    current_file_result = {}
    for row in rows:
        if ods_code == row["NACS"] and _is_same_product(migration["product_id"], row["PName"]):
            current_file_result["new"] = {"asid": row["ASID"], "name": row["PName"]}
        elif ods_code == row["NACS"] and _is_product_of_interest(row["PName"]):
            current_file_result["old"] = {"asid": row["ASID"], "name": row["PName"]}
    return current_file_result


def _is_same_product(finance_product_id, asid_lookup_pname):
    if finance_product_id == TPP_PRODUCT_ID and asid_lookup_pname == "SystmOne":
        return True
    elif finance_product_id == EMIS_PRODUCT_ID and asid_lookup_pname == "EMIS Web":
        return True
    elif finance_product_id == VISION_PRODUCT_ID and asid_lookup_pname == "Vision 3":
        return True
    return False


def _is_product_of_interest(product_name):
    return product_name in ["SystmOne", "EMIS Web", "Vision 3"]