from dateutil.parser import *


def find_last_entry_below_threshold(activity_per_day, threshold):
    date_of_last_entry = None
    for day in activity_per_day:
        if float(day["count"]) > threshold:
            return date_of_last_entry
        date_of_last_entry = isoparse(day["_time"])


def calculate_cutover_start_and_end_date(old_asid_extract_generator, new_asid_extract_generator):
    old_asid_activity_per_day = list(old_asid_extract_generator)
    new_asid_activity_per_day = list(new_asid_extract_generator)
    first_day = old_asid_activity_per_day[0]
    threshold = float(first_day["avgmin2std"])
    old_asid_newest_message_date = find_last_entry_below_threshold(reversed(old_asid_activity_per_day), threshold)
    new_asid_oldest_message_date = find_last_entry_below_threshold(new_asid_activity_per_day, threshold)

    cutover_duration = new_asid_oldest_message_date - old_asid_newest_message_date

    return {
        "cutover_startdate": old_asid_newest_message_date.isoformat(),
        "cutover_enddate": new_asid_oldest_message_date.isoformat(),
        "cutover_duration": cutover_duration.days
    }
