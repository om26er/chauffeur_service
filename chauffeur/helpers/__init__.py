import threading

from django.conf import settings
from django.core.mail import send_mail

from chauffeur.models import (
    User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER, ACTIVATION_KEY_DEFAULT,
    PASSWORD_RESET_KEY_DEFAULT)
from chauffeur.serializers import CustomerSerializer, DriverSerializer


class UserHelpers:
    user = None

    def __init__(self, email):
        self.email = email
        try:
            self.user = User.objects.get(email=self.email)
        except User.DoesNotExist:
            self.user = None

    def exists(self):
        return self.user is not None

    def is_active(self):
        return self.user.is_active

    def _set_is_active(self, active):
        self.user.is_active = active
        self.user.save()
        return self.user

    def activate_account(self):
        self.user.activation_key = ACTIVATION_KEY_DEFAULT
        return self._set_is_active(active=True)

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


def get_user_serializer_by_type(user):
    if user.user_type == USER_TYPE_CUSTOMER:
        return CustomerSerializer(user)
    elif user.user_type == USER_TYPE_DRIVER:
        return DriverSerializer(user)
    else:
        raise ValueError('Invalid user type')


def generate_random_key():
    import random
    return random.randrange(0, 99999, 5)


def _send_account_activation_email(email, activation_key):
    send_mail(
        'Chauffeur: Account activation',
        'Account activation key: {}'.format(activation_key),
        settings.EMAIL_HOST_USER,
        [str(email)],
        fail_silently=False)


def _send_password_reset_email(email, password_reset_key):
    send_mail(
        'Chauffeur: Password reset',
        'Password reset key: {}'.format(password_reset_key),
        settings.EMAIL_HOST_USER,
        [str(email)],
        fail_silently=False)


def _generate_activation_key_and_send_email(user):
    activation_key = generate_random_key()
    user.activation_key = activation_key
    user.save()
    _send_account_activation_email(user.email, activation_key)


def generate_activation_key_and_send_email(user):
    thread = threading.Timer(
        0, _generate_activation_key_and_send_email, args=(user,))
    thread.start()


def _generate_password_reset_key_and_send_email(user):
    password_reset_key = generate_random_key()
    user.password_reset_key = password_reset_key
    user.save()
    _send_password_reset_email(user.email, password_reset_key)


def generate_password_reset_key_and_send_email(user):
    thread = threading.Timer(
        0, _generate_password_reset_key_and_send_email, args=(user,))
    thread.start()
