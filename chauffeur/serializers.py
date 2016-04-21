from django.http import Http404

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from chauffeur.models import User


class CustomerSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    vehicle_type = serializers.CharField(required=True)
    vehicle_make = serializers.CharField(required=True)
    vehicle_model = serializers.CharField(required=True)
    vehicle_category = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password',
                  'email', 'phone_number', 'photo', 'location',
                  'number_of_hires', 'vehicle_type', 'vehicle_make',
                  'vehicle_model', 'vehicle_category', 'initial_app_payment',
                  'user_type')


class DriverSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    driving_experience = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password',
                  'email', 'phone_number', 'photo', 'location',
                  'location_last_updated', 'driving_experience',
                  'number_of_hires', 'bio', 'user_type')
