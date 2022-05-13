from datetime import datetime

import pytest as pytest

from chalicelib.migration_occurrences import _parse_migration

test_dates = [
    ("29/03/2021", datetime(2021, 3, 29)),
    ("11/07/2021", datetime(2021, 7, 11))
]


@pytest.mark.parametrize("input_date, expected_date", test_dates)
def test_parse_migration_parses_dates_correctly(input_date, expected_date):
    input_row = {
        "Service Recipient ID (e.g. ODS code where this is available)": "ods-code",
        "Call Off Ordering Party name": "ccg-name",
        "Service Recipient Name": "practice-name",
        "Supplier ID": "supplier-id",
        "Product ID ": "product-id",
        "Actual M1 date": input_date
    }

    migration = _parse_migration(input_row)

    expected_migration = {
        "ods_code": "ods-code",
        "ccg_name": "ccg-name",
        "practice_name": "practice-name",
        "supplier_id": "supplier-id",
        "product_id": "product-id",
        "date": expected_date
    }
    assert migration == expected_migration


def test_parse_migration_raises_exception_if_given_american_date_format():
    input_row = {
        "Service Recipient ID (e.g. ODS code where this is available)": "ods-code",
        "Call Off Ordering Party name": "ccg-name",
        "Service Recipient Name": "practice-name",
        "Supplier ID": "supplier-id",
        "Product ID ": "product-id",
        "Actual M1 date": "03/29/2021"
    }

    with pytest.raises(ValueError):
        _parse_migration(input_row)