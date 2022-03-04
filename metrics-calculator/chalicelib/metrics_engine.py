from datetime import datetime

from dateutil.parser import *
import pytz
import functools


def get_oldest_message_date(ref_date, message):
    current_date = isoparse(message["_time"])
    result_date = ref_date
    if current_date < ref_date:
        result_date = current_date
    return result_date


def get_newest_message_date(ref_date, message):
    current_date = isoparse(message["_time"])
    result_date = ref_date
    if current_date > ref_date:
        result_date = current_date
    return result_date


def calculate_cutover_start_and_end_date(
        old_asid_extract_generator, new_asid_extract_generator):
    old_asid_newest_message_date = functools.reduce(
        get_newest_message_date,
        old_asid_extract_generator,
        pytz.utc.localize(datetime.min))
    new_asid_oldest_message_date = functools.reduce(
        get_oldest_message_date,
        new_asid_extract_generator,
        pytz.utc.localize(datetime.max))

    cutover_duration = new_asid_oldest_message_date - old_asid_newest_message_date

    return {
        "cutover_startdate": old_asid_newest_message_date.isoformat(),
        "cutover_enddate": new_asid_oldest_message_date.isoformat(),
        "cutover_duration": cutover_duration.days
    }
