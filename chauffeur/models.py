from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from chauffeur.managers import CustomUserManager
from chauffeur.helpers import (
    send_account_activation_email, generate_random_key)


ACTIVATION_KEY_DEFAULT = -1
PASSWORD_RESET_KEY_DEFAULT = -1

USER_TYPE_CUSTOMER = 0
USER_TYPE_DRIVER = 1


USER_TYPE_CHOICES = (
    (USER_TYPE_CUSTOMER, 'Customer'), (USER_TYPE_DRIVER, 'Driver'))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, blank=False, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True, blank=False)

    user_type = models.IntegerField(
        blank=False, default=-1, choices=USER_TYPE_CHOICES)
    activation_key = models.IntegerField(default=ACTIVATION_KEY_DEFAULT)
    password_reset_key = models.IntegerField(
        default=PASSWORD_RESET_KEY_DEFAULT)

    phone_number = models.CharField(max_length=255, blank=False)
    photo = models.ImageField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    number_of_hires = models.IntegerField(blank=True, default=0)

    # Driver specific fields
    driving_experience = models.CharField(max_length=255, blank=True)
    location_last_updated = models.DateTimeField(blank=True, null=True)
    bio = models.CharField(max_length=2000, blank=True)

    # Customer specific fields
    vehicle_type = models.CharField(max_length=255, blank=True)
    vehicle_category = models.CharField(max_length=255, blank=True)
    vehicle_make = models.CharField(max_length=255, blank=True)
    vehicle_model = models.CharField(max_length=255, blank=True)
    initial_app_payment = models.FloatField(blank=True, default=0.0)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.is_admin and self.is_new:
            # Hash the password.
            self.set_password(self.password)
            self.is_active = False
            self.is_new = False
            activation_key = generate_random_key()
            self.activation_key = activation_key
            send_account_activation_email(self.email, activation_key)
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
