from dateutil.parser import *


def index_of_entry_above_threshold(activity_per_day, threshold):
    for i, day in enumerate(activity_per_day):
        if float(day["count"]) > threshold:
            return i
    raise Exception("Invalid data - none exceeds threshold")


def calculate_cutover_start_and_end_date(old_asid_extract_generator, new_asid_extract_generator):
    old_asid_activity_per_day = list(old_asid_extract_generator)
    new_asid_activity_per_day = list(new_asid_extract_generator)
    first_day = old_asid_activity_per_day[0]
    threshold = float(first_day["avgmin2std"])
    reversed_old_asid_activity = list(reversed(old_asid_activity_per_day))
    index_for_old = index_of_entry_above_threshold(
        reversed_old_asid_activity, threshold)
    old_asid_newest_message_date = isoparse(
        reversed_old_asid_activity[index_for_old - 1]["_time"])
    index_for_new = index_of_entry_above_threshold(
        new_asid_activity_per_day, threshold)
    new_asid_oldest_message_date = isoparse(
        new_asid_activity_per_day[index_for_new]["_time"])

    cutover_duration = new_asid_oldest_message_date - old_asid_newest_message_date

    return {
        "cutover_startdate": old_asid_newest_message_date.isoformat(),
        "cutover_enddate": new_asid_oldest_message_date.isoformat(),
        "cutover_duration": cutover_duration.days
    }
