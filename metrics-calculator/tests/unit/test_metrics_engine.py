from unittest.mock import ANY

from chalicelib.metrics_engine import calculate_cutover_start_and_end_date, \
    calculate_migrations_stats_per_supplier_combination


def test_calculate_cutover_start_and_end_date():
    old_asid_extract_generator = (x for x in [
        {"_time": "2021-11-25T00:00:00.000+0000",
            "count": "2000", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-11-26T00:00:00.000+0000",
            "count": "2854", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-11-27T00:00:00.000+0000",
            "count": "2754", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-12-02T00:00:00.000+0000",
            "count": "200", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-12-03T00:00:00.000+0000",
            "count": "200", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-12-04T00:00:00.000+0000", "count": "200", "avgmin2std": "1044.7268404372467"}])
    new_asid_extract_generator = (x for x in [
        {"_time": "2021-12-05T00:00:00.000+0000",
            "count": "300", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-12-06T00:00:00.000+0000",
            "count": "2854", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-12-07T00:00:00.000+0000",
            "count": "2754", "avgmin2std": "1044.7268404372467"},
        {"_time": "2021-12-08T00:00:00.000+0000",
            "count": "2554", "avgmin2std": "1044.7268404372467"}
    ])

    result = calculate_cutover_start_and_end_date(
        old_asid_extract_generator, new_asid_extract_generator)

    assert result == {
        "cutover_startdate": "2021-12-02T00:00:00+00:00",
        "cutover_enddate": "2021-12-06T00:00:00+00:00",
        "cutover_duration": 4,
    }


def test_calculate_migrations_stats_per_supplier_combination_returns_correct_count_for_multiple_occurrences_for_multiple_combination():
    metrics = [{"source_system": "source-system-1",
                "target_system": "target-system",
                "cutover_duration": 4
                },
               {"source_system": "source-system-1",
                "target_system": "target-system",
                "cutover_duration": 4
                },
               {"source_system": "source-system-2",
                "target_system": "target-system",
                "cutover_duration": 4
                },
               {"source_system": "source-system-2",
                "target_system": "target-system",
                "cutover_duration": 4
                }]

    result = calculate_migrations_stats_per_supplier_combination(metrics)

    expected_result = [
        {
            "source_system": metrics[0]["source_system"],
            "target_system": metrics[0]["target_system"],
            "count": 2,
            "mean_duration": ANY
        },
        {
            "source_system": metrics[2]["source_system"],
            "target_system": metrics[2]["target_system"],
            "count": 2,
            "mean_duration": ANY
        }]
    assert result == expected_result


def test_calculate_migrations_stats_per_supplier_combination_returns_correct_mean_cutover_duration_for_multiple_combination():
    metrics = [{"source_system": "source-system-1",
                "target_system": "target-system",
                "cutover_duration": 4
                },
               {"source_system": "source-system-1",
                "target_system": "target-system",
                "cutover_duration": 8
                },
               {"source_system": "source-system-2",
                "target_system": "target-system",
                "cutover_duration": 4
                },
               {"source_system": "source-system-2",
                "target_system": "target-system",
                "cutover_duration": 8
                }]
    result = calculate_migrations_stats_per_supplier_combination(metrics)

    expected_result = [
        {
            "source_system": metrics[0]["source_system"],
            "target_system": metrics[0]["target_system"],
            "count": ANY,
            "mean_duration": 6
        },
        {
            "source_system": metrics[2]["source_system"],
            "target_system": metrics[2]["target_system"],
            "count": ANY,
            "mean_duration": 6
        }]
    assert result == expected_result

