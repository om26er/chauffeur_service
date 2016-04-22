from django.conf import settings
from django.core.mail import send_mail

from chauffeur.models import (
    User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER, ACTIVATION_KEY_DEFAULT,
    PASSWORD_RESET_KEY_DEFAULT)
from chauffeur.serializers import CustomerSerializer, DriverSerializer


def does_user_exist(**kwargs):
    try:
        User.objects.get(**kwargs)
        return True
    except User.DoesNotExist:
        return False


def is_user_active(username):
    return User.objects.get(username=username).is_active


def set_is_user_active(username, state):
    user = User.objects.get(username=username)
    user.is_active = state
    user.save()
    return user


def is_activation_key_valid(username, activation_key):
    if activation_key == ACTIVATION_KEY_DEFAULT:
        return False

    user = User.objects.get(username=username)
    return int(user.activation_key) == int(activation_key)


def is_password_reset_key_valid(username, password_reset_key):
    if password_reset_key == PASSWORD_RESET_KEY_DEFAULT:
        return False

    user = User.objects.get(username=username)
    return int(user.password_reset_key) == int(password_reset_key)


def get_user_serializer_by_type(user):
    if user.user_type == USER_TYPE_CUSTOMER:
        return CustomerSerializer(user)
    elif user.user_type == USER_TYPE_DRIVER:
        return DriverSerializer(user)
    else:
        raise ValueError('Invalid user type')


def generate_random_key():
    import random
    return random.randrange(0, 9999, 4)


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
    import threading
    thread = threading.Timer(
        0, _generate_activation_key_and_send_email, args=(user,))
    thread.start()


def _generate_password_reset_key_and_send_email(user):
    password_reset_key = generate_random_key()
    user.password_reset_key = password_reset_key
    user.save()
    _send_password_reset_email(user.email, password_reset_key)


def generate_password_reset_key_and_send_email(user):
    import threading
    thread = threading.Timer(
        0, _generate_password_reset_key_and_send_email, args=(user,))
    thread.start()
