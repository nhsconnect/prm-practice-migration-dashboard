from io import BytesIO
from src.csv_rows import csv_rows
from tests.builders.file import build_gzip_csv


def test_csv_rows():
    gzipped_content = build_gzip_csv(
        header=["id", "message", "comment"],
        rows=[["123", "A message", "A comment"], [
            "321", "Another message", "Another comment"]],
    )

    expected = [
        {"id": "123", "message": "A message", "comment": "A comment"},
        {"id": "321", "message": "Another message", "comment": "Another comment"},
    ]

    stream = BytesIO(gzipped_content)

    actual = csv_rows(stream)

    assert list(actual) == expected
