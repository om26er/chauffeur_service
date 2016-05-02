import threading

from django.conf import settings
from django.core.mail import send_mail


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
