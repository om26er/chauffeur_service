from datetime import timedelta
import os
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from chauffeur_service.settings import AUTH_USER_MODEL
from chauffeur.managers import CustomUserManager
from chauffeur.helpers import (
    send_account_activation_email,
    generate_random_key,
)


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


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    name = str(uuid.uuid4()).replace('-', '_')
    filename = '{}.{}'.format(name, ext)
    return os.path.join('images', filename)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, blank=False, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True, blank=False)

    user_type = models.IntegerField(
        blank=False, default=-1, choices=USER_TYPE_CHOICES)
    transmission_type = models.IntegerField(blank=False, default=-1)
    activation_key = models.IntegerField(default=ACTIVATION_KEY_DEFAULT)
    password_reset_key = models.IntegerField(
        default=PASSWORD_RESET_KEY_DEFAULT)
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

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.is_admin and self.is_new:
            # Hash the password.
            self.set_password(self.password)
            self.is_active = False
            self.is_new = False
            self.activation_key = generate_random_key()
            send_account_activation_email(self.email, self.activation_key)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


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
        return self.start_time + timedelta(minutes=self.time_span)

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
            self.driver.email, self.start_time.__str__())
