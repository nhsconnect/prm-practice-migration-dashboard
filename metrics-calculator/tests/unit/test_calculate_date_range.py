from datetime import date

from chalicelib.calculate_date_range import calculate_baseline_date_range, calculate_pre_cutover_date_range, calculate_post_cutover_date_range


def test_calculate_baseline_date_range():
    go_live_date = date(2021, 7, 12)

    date_range = calculate_baseline_date_range(go_live_date)

    assert date_range == {"start_date": date(2021, 4, 6), "end_date": date(2021, 6, 28)}


def test_calculate_pre_cutover_date_range():
    go_live_date = date(2021, 7, 12)

    date_range = calculate_pre_cutover_date_range(go_live_date)

    assert date_range == {"start_date": date(2021, 6, 29), "end_date": date(2021, 7, 19)}


def test_calculate_post_cutover_date_range():
    go_live_date = date(2021, 7, 12)

    date_range = calculate_post_cutover_date_range(go_live_date)

    assert date_range == {"start_date": date(2021, 7, 6), "end_date": date(2021, 7, 26)}
