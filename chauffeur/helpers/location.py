import datetime

from geopy.distance import vincenty

from django.utils import timezone

from chauffeur.models import User, USER_TYPE_DRIVER
from chauffeur.helpers import get_formatted_time_from_string
from chauffeur.helpers import driver as driver_helpers


def get_user_location(user):
    raw_location = user.location
    if raw_location == '':
        return None

    return get_location_from_string(raw_location)


def get_location_from_string(location_string):
    split = location_string.split(',')
    return split[0], split[1]


def are_locations_within_radius(base_location, remote_location, radius):
    distance = vincenty(base_location, remote_location).kilometers
    return float(radius) <= distance


def _resolve_time(time):
    if not time:
        return timezone.now()

    if not isinstance(time, datetime.datetime):
        return get_formatted_time_from_string(time)

    return time


def filter_available_drivers(base_location, radius, start_time, time_span):
    result = []
    drivers = User.objects.filter(user_type=USER_TYPE_DRIVER, is_active=True)
    start_time = _resolve_time(start_time)
    time_span = datetime.timedelta(minutes=int(time_span))
    base_location = get_location_from_string(base_location)

    for driver in drivers:
        if driver_helpers.is_driver_available_for_hire(
                driver, start_time, start_time+time_span):
            driver_location = get_user_location(driver)
            if are_locations_within_radius(base_location, driver_location,
                                           radius):
                result.append(driver)

    return result
