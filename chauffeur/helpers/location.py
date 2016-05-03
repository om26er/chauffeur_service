from geopy.distance import vincenty

from chauffeur.models import User, USER_TYPE_DRIVER
from chauffeur.serializers import DriverSerializer


def get_user_location(user):
    raw_location = user.location
    if raw_location == '':
        return None

    split = raw_location.split(',')
    return split[0], split[1]


class LocationCalculator:
    user = None

    def __init__(self, email):
        self.email = email
        try:
            self.user = User.objects.get(email=self.email)
        except User.DoesNotExist:
            self.user = None

    def get_drivers_around(self, radius, base_location=None):
        result = []
        if not base_location:
            base_location = get_user_location(self.user)
            if not base_location:
                return DriverSerializer(result)

        drivers = User.objects.filter(
            user_type=USER_TYPE_DRIVER, is_active=True)

        for driver in drivers:
            driver_location = get_user_location(driver)
            distance = vincenty(base_location, driver_location).kilometers
            if distance <= float(radius):
                result.append(driver)

        if not result:
            return result

        return DriverSerializer(result)
