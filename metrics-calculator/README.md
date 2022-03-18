## Package and Deploy

`./scripts/build-and-package.sh`

## Architecture

The metrics calculator is a lambda, written in Python. It takes in data in gzipped CSV format and outputs a JSON file.

![Architecture diagram of metrics calculator](images/metrics-calculator-architecture.svg)

### Input data

The input data consists of three different kinds of (gzipped) CSV files:

- details of migrations that have occurred
- mappings from ODS code to ASIDs
- Spine messages sent & received for ASIDs.

#### Migration occurrences data

Details about migrations that have occurred originate in exports taken from the finance system. These Excel spreadsheets contain many worksheets with mostly irrelevant data, so in order to simplify things for the metrics calculator, the data in the "Pending Act upload" (or similar—it's not entirely consistently named) worksheet is copied into a blank spreadsheet from where it can be exported in CSV format. This CSV file is then manually gzipped and uploaded to the migration occurrences S3 bucket.

#### ASID mappings data

A mapping of ODS codes to ASIDs is published once a month by email. Contact the DIR team to request a subscription to the data.

The CSV files are manually gzipped and uploaded to the ASID lookups S3 bucket.

#### Telemetry data

In order to calculate the cutover period for a migration, Spine messages are checked around the time of the migration to see when the old system (referenced by its ASID) stops sending and receiving messages and when the new system starts sending and receiving messages.

A copy of Spine messages exists in Splunk, where queries on the data can be run. Since arranging Splunk integration is more involved, for now this data is queried manually and the exported data into CSV files per ASID, which are then manually gzipped and uploaded to the telemetry S3 bucket.

## Gzipping CSV files

To gzip a CSV file, run the following command from the command line:

```bash
gzip -c <CSV_FILE_PATH> > <OUTPUT_FILE_PATH>
```

- `CSV_FILE_PATH`: The path to the CSV file to be compressed.
- `OUTPUT_FILE_PATH`: The path to output the gzipped data to.
