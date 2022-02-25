
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
    response = s3_object.get()
    body = response["Body"]
    return body


def write_object_s3(client, object_uri: str, body):
    s3_object = _object_from_uri(client, object_uri)
    s3_object.put(Body=body)
