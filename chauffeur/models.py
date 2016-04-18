from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class Driver(AbstractBaseUser):

    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    username = models.CharField(max_length=255, blank=False, unique=True)
    email = models.EmailField(max_length=255, blank=False, unique=True)
    phone_number = models.CharField(max_length=255, blank=False)
    driving_experience = models.CharField(max_length=255, blank=False)
    photo = models.ImageField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    location_last_updated = models.DateTimeField(blank=True, auto_now_add=True)
    number_of_hires = models.IntegerField(blank=True, default=0)
    bio = models.CharField(max_length=2000, blank=True)

    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super().save(*args, **kwargs)


class Customer(AbstractBaseUser):

    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    username = models.CharField(max_length=255, blank=False, unique=True)
    email = models.EmailField(max_length=255, blank=False, unique=True)
    phone_number = models.CharField(max_length=255, blank=False)
    photo = models.ImageField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    number_of_hires = models.IntegerField(blank=True, default=0)
    vehicle_type = models.CharField(max_length=255, blank=False)
    vehicle_category = models.CharField(max_length=255, blank=False)
    vehicle_make = models.CharField(max_length=255, blank=False)
    vehicle_model = models.CharField(max_length=255, blank=False)
    initial_app_payment = models.FloatField(blank=True, default=0.0)

    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super().save(*args, **kwargs)
