from chauffeur.models import (
    HireRequest, HIRE_REQUEST_ACCEPTED, HIRE_REQUEST_DONE,
    HIRE_REQUEST_INPROGRESS, SERVICE_GRACE_PERIOD)


JOB_ACTIVE_STATES = (
    HIRE_REQUEST_ACCEPTED, HIRE_REQUEST_INPROGRESS, HIRE_REQUEST_DONE, )


def _does_time_overlap(new_start, new_stop, old_start, old_stop):
    if old_start > new_stop:
        return False

    if new_start < old_start < new_stop:
        return True

    if old_start < new_start and new_stop < old_stop:
        return True

    if old_start < new_start and new_stop > old_stop:
        return True

    if old_stop < new_start:
        return False

    return False


def is_driver_available_for_hire(driver, start_time, end_time):
    hire_requests = HireRequest.objects.filter(
        driver=driver.id,
        status__in=JOB_ACTIVE_STATES)

    request_start = start_time - SERVICE_GRACE_PERIOD
    request_stop = end_time + SERVICE_GRACE_PERIOD

    for request in hire_requests:
        if _does_time_overlap(
                request_start, request_stop, request.start_time,
                request.end_time):
            return False

    return True
