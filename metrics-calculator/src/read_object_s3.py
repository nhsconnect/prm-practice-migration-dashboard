
import sys
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def _object_from_uri(client, uri: str):
    object_url = urlparse(uri)
    s3_bucket = object_url.netloc
    s3_key = object_url.path.lstrip("/")
    return client.Object(s3_bucket, s3_key)


def read_object_s3(client, object_uri: str):
    logger.info(
        "Reading file from: " + object_uri,
        extra={"event": "READING_FILE_FROM_S3", "object_uri": object_uri},
    )
    s3_object = _object_from_uri(client, object_uri)

    try:
        response = s3_object.get()
        body = response["Body"]
        return body
    except client.meta.client.exceptions.NoSuchKey:
        logger.error(
            f"File not found: {object_uri}, exiting...",
            extra={"event": "FILE_NOT_FOUND_IN_S3", "object_uri": object_uri},
        )
        sys.exit(1)


def write_object_s3(client, object_uri: str, body):
    s3_object = _object_from_uri(client, object_uri)

    try:
        s3_object.put(Body=body)
    except client.meta.client.exceptions.NoSuchKey:
        logger.error(
            f"File not written: {object_uri}, exiting...",
            extra={"event": "FILE_CANNOT_BE_WRITTEN_TO_S3", "object_uri": object_uri},
        )
        sys.exit(1)