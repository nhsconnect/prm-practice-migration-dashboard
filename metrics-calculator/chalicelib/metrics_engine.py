import itertools
from datetime import datetime

from dateutil.parser import *
import pytz
import functools

def first_message_below_threshold(old_asid_extract_generator, threshold):
    reversed_extract_dates_list = reversed(list(old_asid_extract_generator))
    first_message_date = None
    for day in reversed_extract_dates_list:
        if float(day["count"]) > threshold:
            return first_message_date
        first_message_date = isoparse(day["_time"])

def last_message_below_threshold(new_asid_extract_generator, threshold):
    last_message_date = None
    for day in new_asid_extract_generator:
        if float(day["count"]) > threshold:
            return last_message_date
        last_message_date = isoparse(day["_time"])

def calculate_cutover_start_and_end_date(
        old_asid_extract_generator, new_asid_extract_generator):
    first_day = next(itertools.islice(old_asid_extract_generator, 1))
    threshold = float(first_day["avgmin2std"])
    old_asid_newest_message_date = first_message_below_threshold(old_asid_extract_generator, threshold)
    new_asid_oldest_message_date = last_message_below_threshold(new_asid_extract_generator, threshold)

    cutover_duration = new_asid_oldest_message_date - old_asid_newest_message_date

    return {
        "cutover_startdate": old_asid_newest_message_date.isoformat(),
        "cutover_enddate": new_asid_oldest_message_date.isoformat(),
        "cutover_duration": cutover_duration.days
    }
