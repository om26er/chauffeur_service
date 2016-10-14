from datetime import timedelta
import os
import uuid

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import models
from rest_framework.authtoken.models import Token
from simple_login.models import BaseUser

HIRE_REQUEST_PENDING = 1
HIRE_REQUEST_ACCEPTED = 2
HIRE_REQUEST_DECLINED = 3
HIRE_REQUEST_IN_PROGRESS = 4
HIRE_REQUEST_DONE = 5
HIRE_REQUEST_CONFLICT = 6

REVIEW_STATUS_PENDING = 0
REVIEW_STATUS_DRIVER_DONE = 1
REVIEW_STATUS_CUSTOMER_DONE = 2
REVIEW_STATUS_DONE = 3

SERVICE_GRACE_PERIOD = timedelta(minutes=60)

USER_TYPE_CUSTOMER = 0
USER_TYPE_DRIVER = 1
USER_TYPE_ADMIN = 3


def get_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    name = str(uuid.uuid4()).replace('-', '_')
    filename = '{}.{}'.format(name, ext)
    return os.path.join('images', filename)


class ChauffeurUser(BaseUser):
    user_type = models.IntegerField(blank=False, default=USER_TYPE_ADMIN)
    # Common profile fields
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, blank=False)
    photo = models.ImageField(blank=True, upload_to=get_image_file_path)
    # Drive specific profile fields
    bio = models.CharField(max_length=2000, blank=True)
    driving_experience = models.CharField(max_length=255, blank=True)
    doc1 = models.ImageField(upload_to=get_image_file_path)
    doc2 = models.ImageField(upload_to=get_image_file_path)
    doc3 = models.ImageField(upload_to=get_image_file_path)
    # Common preference fields
    transmission_type = models.IntegerField(blank=False, default=-1)
    # Customer specific preference fields
    vehicle_type = models.IntegerField(default=-1)
    vehicle_make = models.CharField(max_length=255, blank=True)
    vehicle_model = models.CharField(max_length=255, blank=True)
    driver_filter_radius = models.IntegerField(default=15)
    # Driver specific preference fields
    location_reporting_type = models.IntegerField(default=1)
    location_reporting_interval = models.IntegerField(default=15)
    # Common record fields
    number_of_hires = models.IntegerField(blank=True, default=0)
    review_count = models.IntegerField(default=0, blank=True)
    review_stars = models.FloatField(default=-1.0, blank=True)
    # Customer specific record fields
    initial_app_payment = models.FloatField(blank=True, default=0.0)
    # Driver specific record fields
    location = models.CharField(max_length=255, blank=True)
    location_last_updated = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(default=1)


@receiver(pre_delete, sender=ChauffeurUser)
def cascade_photos(*args, **kwargs):
    instance = kwargs['instance']
    instance.photo.delete()
    instance.doc1.delete()
    instance.doc2.delete()
    instance.doc3.delete()


class PushIDs(models.Model):
    user = models.ForeignKey(
        ChauffeurUser,
        blank=False,
        on_delete=models.CASCADE,
        related_name='push_notifications_id'
    )
    device_id = models.CharField(max_length=255, blank=False)
    push_key = models.CharField(max_length=255, blank=False)


class Segment(models.Model):
    identifier = models.IntegerField(blank=False, unique=True)
    name = models.CharField(max_length=255, blank=False, unique=True)

    def __str__(self):
        return self.name


class Charge(models.Model):
    segment = models.ForeignKey(Segment)
    hours = models.IntegerField(blank=False)
    briver_price = models.IntegerField(blank=False)
    driver_hourly_rate = models.IntegerField(blank=False)

    @property
    def driver_price(self):
        return self.hours * self.driver_hourly_rate

    @property
    def total_price(self):
        return self.driver_price + self.briver_price

    def __str__(self):
        return 'Segment: {}, Hours: {}, Pricing: {}'.format(
            self.segment.name,
            self.hours,
            self.total_price
        )


class HireRequest(models.Model):
    price = models.ForeignKey(
        Charge,
        blank=False,
        related_name='price'
    )
    customer = models.ForeignKey(
        ChauffeurUser,
        blank=False,
        related_name='customer'
    )
    driver = models.ForeignKey(
        ChauffeurUser,
        blank=False,
        related_name='driver'
    )
    location = models.CharField(max_length=255, blank=False)
    start_time = models.DateTimeField(blank=False)
    time_span = models.IntegerField(blank=False)
    status = models.IntegerField(default=HIRE_REQUEST_PENDING)

    @property
    def end_time(self):
        return self.start_time + timedelta(hours=self.time_span)

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
    def driver_phone_number(self):
        return self.driver.phone_number

    @property
    def customer_name(self):
        return self.customer.full_name

    @property
    def customer_phone_number(self):
        return self.customer.phone_number

    def __str__(self):
        return 'Hire Request by {} at {}'.format(
            self.driver.email,
            self.start_time.__str__()
        )


@receiver(post_save, sender=HireRequest)
def process_save(sender, instance=None, created=False, **kwargs):
    if created:
        Review.objects.create(request=instance)


class Review(models.Model):
    request = models.OneToOneField(
        HireRequest,
        blank=False,
        related_name='hire_request'
    )
    driver_review = models.FloatField(blank=True, null=True)
    customer_review = models.FloatField(blank=True, null=True)

    @property
    def driver(self):
        return self.request.driver.id

    @property
    def driver_name(self):
        return self.request.driver.full_name

    @property
    def driver_email(self):
        return self.request.driver.email

    @property
    def customer(self):
        return self.request.customer.id

    @property
    def customer_name(self):
        return self.request.customer.full_name

    @property
    def customer_email(self):
        return self.request.customer.email

    @property
    def status(self):
        if not self.driver_review and not self.customer_review:
            return REVIEW_STATUS_PENDING

        if self.driver_review and self.customer_review:
            return REVIEW_STATUS_DONE

        if self.customer_review and not self.driver_review:
            return REVIEW_STATUS_CUSTOMER_DONE

        if self.driver_review and not self.customer_review:
            return REVIEW_STATUS_DRIVER_DONE
