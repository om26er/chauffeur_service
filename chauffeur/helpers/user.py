from rest_framework.authtoken.models import Token

from chauffeur.models import (
    User, ACTIVATION_KEY_DEFAULT, PASSWORD_RESET_KEY_DEFAULT,
    USER_TYPE_CUSTOMER, USER_TYPE_DRIVER)
from chauffeur.serializers import CustomerSerializer, DriverSerializer


class UserHelpers:
    user = None

    def __init__(self, **kwargs):
        self.user = User.objects.get(**kwargs)

    def exists(self):
        return self.user is not None

    def is_active(self):
        return self.user.is_active

    def _set_is_active(self, active):
        self.user.is_active = active
        self.user.save()

    def activate_account(self):
        self.user.activation_key = ACTIVATION_KEY_DEFAULT
        self._set_is_active(active=True)

    def is_activation_key_valid(self, key):
        if key == ACTIVATION_KEY_DEFAULT:
            return False

        return int(self.user.activation_key) == int(key)

    def is_password_reset_valid(self, key):
        if key == PASSWORD_RESET_KEY_DEFAULT:
            return False

        return int(self.user.password_reset_key) == int(key)

    def change_password(self, new_password):
        self.user.set_password(new_password)
        self.user.password_reset_key = PASSWORD_RESET_KEY_DEFAULT
        self.user.save()

    def get_serializer(self):
        if self.user.user_type == USER_TYPE_CUSTOMER:
            return CustomerSerializer(self.user)
        elif self.user.user_type == USER_TYPE_DRIVER:
            return DriverSerializer(self.user)
        else:
            raise ValueError('Invalid user type')

    def get_token(self):
        return Token.objects.get(user_id=self.user.id).key

    def append_hire_count(self):
        self.user.number_of_hires += 1
        self.user.save()

    def get_push_key(self):
        return self.user.push_notification_key
