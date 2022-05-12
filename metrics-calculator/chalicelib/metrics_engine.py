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
