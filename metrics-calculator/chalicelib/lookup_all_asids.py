from chalicelib.csv_rows import csv_rows

ASID_LOOKUP_HEADERS = [
    "ASID", "NACS", "OrgName", "MName", "PName", "OrgType", "PostCode"]


def lookup_all_asids(s3, bucket_name, migrations):
    asid_lookup_bucket = s3.Bucket(bucket_name)
    result = {}
    for lookup_file in asid_lookup_bucket.objects.all():
        rows = csv_rows(lookup_file.get()["Body"])
        for migration in migrations:
            ods_code = migration["ods_code"]
            asids = {"old": {"asid": "", "name": ""}, "new": {"asid": "", "name": ""}}
            if ods_code not in result:
                result[ods_code] = asids
            current_file_result = {}
            for row in rows:
                if ods_code == row["NACS"] and migration["product_id"] == row["PName"]:
                    current_file_result["new"] = {"asid": row["ASID"], "name": row["PName"]}
                else:
                    current_file_result["old"] = {"asid": row["ASID"], "name": row["PName"]}
            result[ods_code] |= current_file_result
    return result

# have we aleady got a result?
# if yes get the old and new asid from that
# search for old and new asid in file
# if found, replace the value of old and new