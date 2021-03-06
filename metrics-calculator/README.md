The AWS lambdas in this project have been created using the [Chalice framework](https://aws.github.io/chalice/). Building the project is done using Chalice, though it is deployed using the Terraform in the [dashboard-infra directory](../dashboard-infra/).

## Building and packaging

The following script will build and bundle up the lambdas into a single package, and then upload that package to an S3 bucket (that it will create if it doesn't exist). The script will then output a block of JSON that should be copied into the [Terraform vars file](../dashboard-infra/stacks/metrics-calculator/vars/dev.tfvars.json).

```bash
./scripts/build-and-package.sh
```

## Architecture

### Splunk data exporter

The Splunk data exporter is a lambda, written in Python. It uses the Splunk API to export data from Splunk. This "telemetry" is then saved as CSV files.

![Architecture diagram of Splunk data exporter](images/splunk-data-exporter-architecture.svg)

### Metrics calculator

The metrics calculator is a lambda, written in Python. It takes in data in gzipped CSV format and outputs a JSON file.

![Architecture diagram of metrics calculator](images/metrics-calculator-architecture.svg)

## Input data

Input data for the two lambdas comes from a variety of sources:

- details of migrations that have occurred
- mappings from ODS code to ASIDs
- Spine messages sent & received for ASIDs
- GP practice patient registration counts.

### Migration occurrences data

Details about migrations that have occurred originate in exports taken from the finance system. These Excel spreadsheets contain many worksheets with mostly irrelevant data, so in order to simplify things for the metrics calculator, the data in the "Pending Act upload" (or similar—it's not entirely consistently named) worksheet is copied into a blank spreadsheet from where it can be exported in CSV format.

This CSV file is then manually gzipped and uploaded to the migration occurrences S3 bucket.

### ASID mappings data

A mapping of ODS codes to ASIDs is published once a month by email. Contact the DIR team to request a subscription to the data.

The CSV files are manually gzipped and uploaded to the ASID lookups S3 bucket. The files all have the same name, so we have used a convention of putting them each in their own directory, based on which month they are for (e.g. `2021/1/asidLookup.csv.gz` for the January 2021 lookup data).

### Telemetry data

In order to calculate the cutover period for a migration, Spine messages are checked around the time of the migration to see when the old system (referenced by its ASID) stops sending and receiving messages and when the new system starts sending and receiving messages.

A copy of Spine messages exists in Splunk cloud, where queries on the data can be run. The splunk data exporter lambda will query Splunk for message activity during a given time window, export that data to gzipped CSV files, which it then uploads to the telemetry S3 bucket.

The metrics calculator then uses the telemetry files in the S3 bucket.

### Patient registration counts

Patient registration data can be downloaded from [this website](https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice) and uploaded to the patient registrations S3 bucket. The metrics calculator will look for the registration count at the practice in the month that the migration occurred, so data for every month containing a migration occurrence will need uploading to the bucket.

The CSV files are manually gzipped and uploaded to the patient registrations S3 bucket. The files all have the same name (`gp-reg-pat-prac-all.csv`), so before uploading them to the S3 bucket they are renamed to add the month and year as a prefix (this is the convention that is expected by the metrics calculator) (e.g. `april-2021-gp-reg-pat-prac-all.csv.gz`).

## Gzipping CSV files

To gzip a CSV file, run the following command from the command line:

```bash
gzip -c <CSV_FILE_PATH> > <OUTPUT_FILE_PATH>
```

- `CSV_FILE_PATH`: The path to the CSV file to be compressed.
- `OUTPUT_FILE_PATH`: The path to output the gzipped data to.
