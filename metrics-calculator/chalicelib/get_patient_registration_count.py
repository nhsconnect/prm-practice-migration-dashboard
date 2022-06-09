from chalicelib.csv_rows import csv_rows


class PatientRegistrationsError(Exception):
    pass


PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS = [
    "PUBLICATION", "EXTRACT_DATE", "TYPE", "CCG_CODE", "ONS_CCG_CODE", "CODE", "POSTCODE", "SEX", "AGE", "NUMBER_OF_PATIENTS"]


def get_patient_registration_count(s3, bucket_name, migration):
    ods_code = migration["ods_code"]
    migration_date = migration["date"]
    migration_date_as_string = migration_date.strftime("%B-%Y").lower()
    patient_registrations_bucket = s3.Bucket(bucket_name)
    patient_registration_count = 0
    migration_month_data = list(
        patient_registrations_bucket.objects.filter(Prefix=migration_date_as_string, MaxKeys=1))
    if len(migration_month_data) == 0:
        raise PatientRegistrationsError(f"Data for {migration_date_as_string} not found")
    rows = list(csv_rows(migration_month_data[0].get()["Body"]))
    for row in rows:
        if ods_code == row["CODE"]:
            patient_registration_count = row["NUMBER_OF_PATIENTS"]
            break

    if patient_registration_count:
        return int(patient_registration_count)
    else:
        raise PatientRegistrationsError(f"ODS code {ods_code} not found")