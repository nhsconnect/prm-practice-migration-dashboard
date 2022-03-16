from chalicelib.csv_rows import csv_rows
from chalicelib.migration_occurrences import EMIS_PRODUCT_ID, TPP_PRODUCT_ID, VISION_PRODUCT_ID


ASID_LOOKUP_HEADERS = [
    "ASID", "NACS", "OrgName", "MName", "PName", "OrgType", "PostCode"]


class AsidLookupError(Exception):
    pass


def lookup_asids(s3, bucket_name, migration):
    asid_lookup_bucket = s3.Bucket(bucket_name)
    old = None
    new = None
    activated_product_id = migration["product_id"]
    for lookup_file in asid_lookup_bucket.objects.all():
        rows = csv_rows(lookup_file.get()["Body"])
        for row in rows:
            if row["NACS"] != migration["ods_code"]:
                continue
            if _is_same_product(activated_product_id, row["PName"]):
                new = _create_result_item(row)
            elif _is_product_of_interest(row["PName"]):
                old = _create_result_item(row)
        if old is not None and new is not None:
            break

    if old is None and new is None:
        raise AsidLookupError(
            f"No ASIDs found for the ODS code \"{migration['ods_code']}\"")
    elif old is None:
        raise AsidLookupError(
            f"Only new ASID found for the ODS code \"{migration['ods_code']}\"")
    elif new is None:
        raise AsidLookupError(
            f"Only old ASID found for the ODS code \"{migration['ods_code']}\"")

    return {
        "old": {
            "asid": old["asid"],
            "name": old["pname"],
        },
        "new": {
            "asid": new["asid"],
            "name": new["pname"]
        }
    }


def _create_result_item(row):
    return {"asid": row["ASID"], "pname": row["PName"]}


def _is_product_of_interest(product_name):
    return product_name in ["SystmOne", "EMIS Web", "Vision 3"]


def _is_same_product(finance_product_id, asid_lookup_pname):
    if finance_product_id == TPP_PRODUCT_ID and asid_lookup_pname == "SystmOne":
        return True
    elif finance_product_id == EMIS_PRODUCT_ID and asid_lookup_pname == "EMIS Web":
        return True
    elif finance_product_id == VISION_PRODUCT_ID and asid_lookup_pname == "Vision 3":
        return True
    return False
