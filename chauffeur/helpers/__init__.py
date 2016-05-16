from datetime import datetime
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def generate_random_key():
    import random
    # Ensures the return number is always 5 numbers long.
    return random.randint(10000, 99999)


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


def send_account_activation_email(email, key):
    thread = threading.Thread(
        target=_send_account_activation_email, args=(email, key))
    thread.start()


def _generate_password_reset_key_and_send_email(user):
    password_reset_key = generate_random_key()
    user.password_reset_key = password_reset_key
    user.save()
    _send_password_reset_email(user.email, password_reset_key)


def generate_password_reset_key_and_send_email(user):
    thread = threading.Thread(
        target=_generate_password_reset_key_and_send_email, args=(user,))
    thread.start()


def get_formatted_time_from_string(time_string):
    return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S")


def send_hire_request_push_notification(push_key, data):
    thread = threading.Thread(
        target=_send_push_notification, args=(push_key, data))
    thread.start()


def _send_push_notification(push_key, data):
    from gcm import GCM
    gcm = GCM('AIzaSyAKqZ5WrMh3ZinQLkVH8ftdE2qi1DRCCZg')
    gcm.plaintext_request(registration_id=push_key, data=data)
