from chalicelib.csv_rows import csv_rows


class PatientRegistrationsError(Exception):
    pass


PATIENT_REGISTRATION_DATA_LOOKUP_HEADERS = [
    "PUBLICATION", "EXTRACT_DATE", "TYPE", "CCG_CODE", "ONS_CCG_CODE", "CODE", "POSTCODE", "SEX", "AGE", "NUMBER_OF_PATIENTS"]


def get_patient_registration_count(s3, bucket_name, migration):
    ods_code = migration["ods_code"]
    patient_registrations_bucket = s3.Bucket(bucket_name)
    patient_registration_count = 0
    for data_file in patient_registrations_bucket.objects.all():
        rows = list(csv_rows(data_file.get()["Body"]))
        for row in rows:
            if ods_code == row["CODE"]:
                patient_registration_count = row["NUMBER_OF_PATIENTS"]
                break

    if patient_registration_count:
        return int(patient_registration_count)
    else:
        raise PatientRegistrationsError(f"ODS code {ods_code} not found")