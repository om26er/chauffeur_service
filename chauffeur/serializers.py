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


def _calculate_new_review_average_if_review_request(
        instance,
        validated_data
):
    review_stars = validated_data.get('review_stars')
    if review_stars:
        del validated_data['review_stars']
        current_review_count = instance.review_count
        current_review_stars = instance.review_stars
        current_total = current_review_count * current_review_stars
        new_total = current_total + review_stars
        instance.review_count += 1
        instance.review_stars = new_total / instance.review_count


class ChauffeurBaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=ChauffeurBaseUser.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    review_count = serializers.IntegerField(read_only=True)
    transmission_type = serializers.IntegerField(required=True)

    class Meta:
        model = ChauffeurBaseUser
        fields = (
            'id',
            'full_name',
            'password',
            'email',
            'phone_number',
            'photo',
            'number_of_hires',
            'review_count',
            'review_stars',
            'transmission_type',
        )


class CustomerSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(read_only=True)
    vehicle_type = serializers.IntegerField(required=True)
    vehicle_make = serializers.CharField(required=True)
    vehicle_model = serializers.CharField(required=True)

    class Meta:
        model = Customer
        fields = (
            'user_type',
            'vehicle_type',
            'vehicle_make',
            'vehicle_model',
            'initial_app_payment',
            'driver_filter_radius',
        )


class DriverSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(read_only=True)
    driving_experience = serializers.CharField(required=True)
    doc1 = serializers.ImageField(required=True)
    doc2 = serializers.ImageField(required=True)
    doc3 = serializers.ImageField(required=True)

    class Meta:
        model = Driver
        fields = (
            'user_type',
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


class HireRequestSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=False)
    time_span = serializers.IntegerField(required=True)
    driver_name = serializers.CharField(read_only=True)
    driver_email = serializers.EmailField(read_only=True)

    class Meta:
        model = HireRequest
        fields = (
            'customer',
            'driver',
            'start_time',
            'end_time',
            'time_span',
            'status',
            'driver_name',
            'driver_email',
            'id',
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
    request_id = serializers.IntegerField(label='Request')
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
