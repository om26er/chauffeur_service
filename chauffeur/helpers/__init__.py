from datetime import datetime, timedelta
import threading

from gcm import GCM

from chauffeur.helpers import driver as driver_helpers
from chauffeur.helpers.user import UserHelpers

APP_PUSH_ID = 'AIzaSyDQQnF3t7ZtecQzlQhthWMsyIXnusS0sKY'
gcm = GCM(APP_PUSH_ID)


def get_formatted_time_from_string(time_string):
    return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S")


def _call_in_thread(func, *args, **kwargs):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.start()


def send_hire_request_push_notification(push_key, data):
    _call_in_thread(_send_push_notification, push_key=push_key, data=data)


def send_hire_response_push_notification(push_key, data):
    _call_in_thread(_send_push_notification, push_key=push_key, data=data)


def send_superseded_notification(driver, accepted_request, data):
    start_time = accepted_request.start_time
    end_time = start_time + timedelta(minutes=accepted_request.time_span)
    conflicts = driver_helpers.get_conflicting_hire_requests(
        driver,
        start_time,
        end_time
    )
    push_ids = [UserHelpers(id=conflict.customer_id).get_push_key()
                for conflict in conflicts]
    if push_ids:
        _send_superseded_notification(push_keys=push_ids, data=data)


def _send_superseded_notification(push_keys, data):
    _call_in_thread(_send_push_notifications, push_keys=push_keys, data=data)


def _send_push_notification(push_key, data):
    gcm.plaintext_request(registration_id=push_key, data=data)


def _send_push_notifications(push_keys, data):
    gcm.json_request(registration_ids=push_keys, data=data)
