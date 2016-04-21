from chauffeur.models import User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER
from chauffeur.serializers import CustomerSerializer, DriverSerializer


def does_user_exist(username):
    try:
        User.objects.get(username=username)
        return True
    except User.DoesNotExist:
        return False


def set_is_user_active(username, state):
    user = User.objects.get(username=username)
    user.is_active = state
    user.save()
    return user


def is_activation_key_valid(activation_key):
    if activation_key:
        return True
    return False


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


def _send_account_activation_email(activation_key):
    pass


def _generate_activation_key_and_send_email(user):
    activation_key = generate_random_key()
    user.activation_key = activation_key
    user.save()
    _send_account_activation_email(activation_key=activation_key)


def generate_activation_key_and_send_email(user):
    import threading
    thread = threading.Timer(
        0, _generate_activation_key_and_send_email, args=(user,))
    thread.start()
