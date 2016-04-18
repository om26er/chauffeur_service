from rest_framework import serializers

from chauffeur.models import Customer, Driver


class CustomerSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'username', 'password', 'email',
                  'phone_number', 'photo', 'location', 'number_of_hires',
                  'vehicle_type', 'vehicle_make', 'vehicle_model',
                  'vehicle_category', 'initial_app_payment', 'id')


class DriverSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ('first_name', 'last_name', 'username', 'email', 'password',
                  'phone_number', 'driving_experience', 'photo', 'location',
                  'location_last_updated', 'number_of_hires', 'bio', 'id')
