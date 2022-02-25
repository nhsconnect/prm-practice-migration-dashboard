from lib.metrics_engine import calculate_cutover_start_and_end_date


def test_calculate_cutover_start_and_end_date():
    old_asid_extract_generator = (x for x in [
        {"_time": "2021-01-01T13:23:26.649+0000"},
        {"_time": "2021-01-02T13:23:26.649+0000"},
        {"_time": "2021-01-03T13:23:26.649+0000"}
    ])
    new_asid_extract_generator = (x for x in [
        {"_time": "2021-01-10T13:23:26.649+0000"},
        {"_time": "2021-01-11T13:23:26.649+0000"},
        {"_time": "2021-01-12T13:23:26.649+0000"}
    ])

    result = calculate_cutover_start_and_end_date(
        old_asid_extract_generator, new_asid_extract_generator)

    assert result == {
        "cutover_startdate": "2021-01-03T13:23:26.649000+00:00",
        "cutover_enddate": "2021-01-10T13:23:26.649000+00:00",
        "cutover_duration": 7
    }
