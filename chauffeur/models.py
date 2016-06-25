from datetime import timedelta
import os
import uuid

from django.db import models
from simple_login.models import BaseUser

from chauffeur_service.settings import AUTH_USER_MODEL

ACTIVATION_KEY_DEFAULT = -1
PASSWORD_RESET_KEY_DEFAULT = -1

USER_TYPE_CUSTOMER = 0
USER_TYPE_DRIVER = 1

HIRE_REQUEST_PENDING = 1
HIRE_REQUEST_ACCEPTED = 2
HIRE_REQUEST_DECLINED = 3
HIRE_REQUEST_INPROGRESS = 4
HIRE_REQUEST_DONE = 5
HIRE_REQUEST_CONFLICT = 6

SERVICE_GRACE_PERIOD = timedelta(minutes=60)

USER_TYPE_CHOICES = (
    (USER_TYPE_CUSTOMER, 'Customer'),
    (USER_TYPE_DRIVER, 'Driver'),
)


def get_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    name = str(uuid.uuid4()).replace('-', '_')
    filename = '{}.{}'.format(name, ext)
    return os.path.join('images', filename)


class User(BaseUser):
    full_name = models.CharField(max_length=255, blank=True)

    user_type = models.IntegerField(
        blank=False,
        default=-1,
        choices=USER_TYPE_CHOICES
    )
    transmission_type = models.IntegerField(blank=False, default=-1)
    push_notification_key = models.CharField(max_length=255, blank=True)

    phone_number = models.CharField(max_length=255, blank=False)
    photo = models.ImageField(blank=True)
    number_of_hires = models.IntegerField(blank=True, default=0)
    review_count = models.IntegerField(default=0, blank=True)
    review_stars = models.FloatField(default=-1.0, blank=True)

    # Driver specific fields
    driving_experience = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    location_last_updated = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(default=1)
    bio = models.CharField(max_length=2000, blank=True)
    location_reporting_type = models.IntegerField(default=1)
    location_reporting_interval = models.IntegerField(default=2)
    doc1 = models.ImageField(upload_to=get_image_file_path)
    doc2 = models.ImageField(upload_to=get_image_file_path)
    doc3 = models.ImageField(upload_to=get_image_file_path)

    # Customer specific fields
    vehicle_type = models.IntegerField(default=-1)
    vehicle_make = models.CharField(max_length=255, blank=True)
    vehicle_model = models.CharField(max_length=255, blank=True)
    initial_app_payment = models.FloatField(blank=True, default=0.0)
    driver_filter_radius = models.IntegerField(default=15)


class HireRequest(models.Model):
    customer = models.ForeignKey(
        AUTH_USER_MODEL,
        blank=False,
        related_name='customer'
    )
    driver = models.ForeignKey(User, blank=False, related_name='driver')
    start_time = models.DateTimeField(blank=False)
    time_span = models.IntegerField(blank=False)
    status = models.IntegerField(default=HIRE_REQUEST_PENDING)

    @property
    def end_time(self):
        return (self.start_time + timedelta(minutes=self.time_span)).__str__()

    @property
    def grace_pre(self):
        return self.start_time - SERVICE_GRACE_PERIOD

    @property
    def grace_post(self):
        return self.end_time + SERVICE_GRACE_PERIOD

    @property
    def driver_name(self):
        return self.driver.full_name

    @property
    def driver_email(self):
        return self.driver.email

    def __str__(self):
        return 'Hire Request by {} at {}'.format(
            self.driver.email,
            self.start_time.__str__()
        )
