from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


USER_TYPE_CUSTOMER = 0
USER_TYPE_DRIVER = 1

USER_TYPE_CHOICES = (
    (USER_TYPE_CUSTOMER, 'Customer'), (USER_TYPE_DRIVER, 'Driver'))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class User(AbstractUser):
    user_type = models.IntegerField(
        blank=False, default=-1, choices=USER_TYPE_CHOICES)
    activation_key = models.IntegerField(blank=True, default=-1)
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

    USERNAME_FIELD = 'username'

    # FIXME: Find better way to make email unique
    AbstractUser._meta.get_field('email')._unique = True
    AbstractUser._meta.get_field('email').blank = False
    AbstractUser._meta.get_field('email').null = False

    def save(self, *args, **kwargs):
        # Hash the password.
        if not self.is_superuser:
            self.set_password(self.password)
            self.is_active = False
            from chauffeur import helpers
            helpers.generate_activation_key_and_send_email(self)
        super().save(*args, **kwargs)
