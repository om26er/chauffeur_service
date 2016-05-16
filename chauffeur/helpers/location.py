import datetime

from geopy.distance import vincenty

from chauffeur.models import User, USER_TYPE_DRIVER
from chauffeur.helpers import driver as driver_helpers
from chauffeur.serializers import DriverSerializer


def get_user_location(user):
    raw_location = user.location
    if raw_location == '':
        return None

    split = raw_location.split(',')
    return split[0], split[1]


def are_locations_within_radius(base_location, remote_location, radius):
    distance = vincenty(base_location, remote_location).kilometers
    return distance <= float(radius)


def filter_available_drivers(base_location, radius, start_time, time_span):
    result = []
    drivers = User.objects.filter(user_type=USER_TYPE_DRIVER, is_active=True)

    if not start_time:
        start_time = datetime.datetime.now()

    time_span = datetime.timedelta(minutes=time_span)

    for driver in drivers:
        if driver_helpers.is_driver_available_for_hire(
                driver, start_time, start_time+time_span):
            driver_location = get_user_location(driver)
            if are_locations_within_radius(base_location, driver_location,
                                           radius):
                result.append(driver)

    return DriverSerializer(result)
