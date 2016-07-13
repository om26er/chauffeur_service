from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from chauffeur.models import (
    ChauffeurBaseUser,
    Customer,
    Driver,
    HireRequest,
    Review,
)


class ChauffeurBaseUserSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=ChauffeurBaseUser.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ChauffeurBaseUser
        fields = (
            'id',
            'user_type',
            'password',
            'email',
        )


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    review_count = serializers.IntegerField(read_only=True)
    transmission_type = serializers.IntegerField(required=True)
    vehicle_type = serializers.IntegerField(required=True)
    vehicle_make = serializers.CharField(required=True)
    vehicle_model = serializers.CharField(required=True)

    class Meta:
        model = Customer
        fields = (
            'id',
            'email',
            'full_name',
            'phone_number',
            'photo',
            'number_of_hires',
            'review_count',
            'review_stars',
            'transmission_type',
            'vehicle_type',
            'vehicle_make',
            'vehicle_model',
            'initial_app_payment',
            'driver_filter_radius',
        )


def update_location_time(validated_data):
    location = validated_data.get('location')
    if location:
        validated_data.update({'location_last_updated': timezone.now()})


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    review_count = serializers.IntegerField(read_only=True)
    transmission_type = serializers.IntegerField(required=True)
    driving_experience = serializers.CharField(required=True)
    doc1 = serializers.ImageField(required=True)
    doc2 = serializers.ImageField(required=True)
    doc3 = serializers.ImageField(required=True)

    class Meta:
        model = Driver
        fields = (
            'id',
            'email',
            'full_name',
            'phone_number',
            'photo',
            'number_of_hires',
            'review_count',
            'review_stars',
            'transmission_type',
            'location',
            'location_last_updated',
            'driving_experience',
            'bio',
            'status',
            'location_reporting_type',
            'location_reporting_interval',
            'doc1',
            'doc2',
            'doc3',
        )

    def update(self, instance, validated_data):
        update_location_time(validated_data)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        update_location_time(validated_data)
        return super().create(validated_data)


class HireRequestSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=False)
    time_span = serializers.IntegerField(required=True)
    location = serializers.CharField(required=True)
    driver_name = serializers.CharField(read_only=True)
    driver_phone_number = serializers.EmailField(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    customer_phone_number = serializers.EmailField(read_only=True)

    class Meta:
        model = HireRequest
        fields = (
            'id',
            'customer',
            'driver',
            'start_time',
            'end_time',
            'time_span',
            'location',
            'status',
            'driver_name',
            'driver_phone_number',
            'customer_name',
            'customer_phone_number',
        )


class DriverFilterSerializer(serializers.Serializer):
    radius = serializers.FloatField(label='Search radius')
    base_location = serializers.CharField(label='Search base reference')
    start_time = serializers.DateTimeField(
        label='Job start time',
        required=False
    )
    time_span = serializers.IntegerField(label='Job duration')


class HireResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField(label='Response status code')


class ReviewSerializer(serializers.ModelSerializer):
    driver_review = serializers.FloatField(required=False)
    customer_review = serializers.FloatField(required=False)

    class Meta:
        model = Review
        fields = (
            'driver_review',
            'customer_review',
            'status',
            'driver',
            'driver_name',
            'driver_email',
            'customer',
            'customer_name',
            'customer_email',
        )
