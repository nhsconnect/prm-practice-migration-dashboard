import csv
import gzip
import sys
import logging

logger = logging.getLogger(__name__)


def read_gzip_csv(self, object_uri: str):
    logger.info(
        "Reading file from: " + object_uri,
        extra={"event": "READING_FILE_FROM_S3", "object_uri": object_uri},
        )
    s3_object = self._object_from_uri(object_uri)

    try:
        response = s3_object.get()
        body = response["Body"]
        with gzip.open(body, mode="rt") as f:
            input_csv = csv.DictReader(f)
            yield from input_csv
    except self._client.meta.client.exceptions.NoSuchKey:
        logger.error(
            f"File not found: {object_uri}, exiting...",
            extra={"event": "FILE_NOT_FOUND_IN_S3", "object_uri": object_uri},
        )
        sys.exit(1)