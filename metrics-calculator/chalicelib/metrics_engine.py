from dateutil.parser import *


def index_of_entry_above_threshold(activity_per_day, threshold):
    for i, day in enumerate(activity_per_day):
        if float(day["count"]) > threshold:
            return i
    raise Exception("Invalid data - none exceeds threshold")


def calculate_cutover_start_and_end_date(stats_preceding_cutover, stats_following_cutover):
    stats_preceding_cutover_list = list(stats_preceding_cutover)
    stats_following_cutover_list = list(stats_following_cutover)

    # The stats are in chronological order, so to search backwards for cutover start,
    # we reverse the order
    reversed_stats_preceding_cutover = list(
        reversed(stats_preceding_cutover_list))

    threshold = calculate_threshold(stats_preceding_cutover_list)

    try:
        cutover_start_date = find_date_of_entry_above_threshold(
            reversed_stats_preceding_cutover, threshold, -1)
    except Exception as exception:
        raise Exception("Start date out of range") from exception

    try:
        cutover_end_date = find_date_of_entry_above_threshold(
            stats_following_cutover_list, threshold)
    except Exception as exception:
        raise Exception("End date out of range") from exception

    cutover_duration = cutover_end_date - cutover_start_date
    return {
        "cutover_startdate": cutover_start_date.isoformat(),
        "cutover_enddate": cutover_end_date.isoformat(),
        "cutover_duration": cutover_duration.days
    }


def find_date_of_entry_above_threshold(events_per_day_list, threshold, offset=0):
    index = index_of_entry_above_threshold(
        events_per_day_list, threshold)

    day_stats = events_per_day_list[index + offset]

    return isoparse(day_stats["_time"])


def calculate_threshold(old_asid_activity_per_day):
    first_day = old_asid_activity_per_day[0]
    threshold = float(first_day["avgmin2std"])
    return threshold


def calculate_migrations_stats_per_supplier_combination(metrics):
    running_stats = []
    for metric in metrics:
        supplier_combination_stats = next((x for x in running_stats if is_matching_combination(metric, x)), None)
        if supplier_combination_stats is None:
            running_stats.append({
                "source_system": metric["source_system"],
                "target_system": metric["target_system"],
                "count": 1,
                "cumulative_duration": metric["cutover_duration"]
            })
        if supplier_combination_stats:
            supplier_combination_stats["count"] += 1
            supplier_combination_stats["cumulative_duration"] += metric["cutover_duration"]

    results = []
    for stats in running_stats:
        mean_duration = stats["cumulative_duration"] / stats["count"]
        results.append({
            "source_system": stats["source_system"],
            "target_system": stats["target_system"],
            "count": stats["count"],
            "mean_duration": mean_duration
        })
    return results


def is_matching_combination(metric, combination):
    return combination["source_system"] == metric["source_system"] and \
           combination["target_system"] == metric["target_system"]
