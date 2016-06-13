from django.utils import timezone

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from chauffeur.models import (
    User,
    HireRequest,
    USER_TYPE_CUSTOMER,
    USER_TYPE_DRIVER,
)


def _calculate_new_review_average_if_review_request(
        instance, validated_data):
    review_stars = validated_data.get('review_stars')
    if review_stars:
        del validated_data['review_stars']
        current_review_count = instance.review_count
        current_review_stars = instance.review_stars
        current_total = current_review_count * current_review_stars
        new_total = current_total + review_stars
        instance.review_count += 1
        instance.review_stars = new_total / instance.review_count


def _hash_password_if_password_request(instance, validated_data):
    password = validated_data.get('password')
    if password:
        del validated_data['password']
        instance.set_password(password)


class CustomerSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    vehicle_type = serializers.IntegerField(required=True)
    vehicle_make = serializers.CharField(required=True)
    vehicle_model = serializers.CharField(required=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'full_name',
            'password',
            'user_type',
            'email',
            'phone_number',
            'photo',
            'number_of_hires',
            'vehicle_type',
            'vehicle_make',
            'vehicle_model',
            'initial_app_payment',
            'review_count',
            'review_stars',
            'driver_filter_radius',
        )

    def create(self, validated_data):
        validated_data.update({'user_type': USER_TYPE_CUSTOMER})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        _hash_password_if_password_request(instance, validated_data)
        _calculate_new_review_average_if_review_request(
            instance, validated_data)
        return super().update(instance, validated_data)


class DriverSerializer(serializers.ModelSerializer):
    user_type = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    driving_experience = serializers.CharField(required=True)
    review_count = serializers.IntegerField(read_only=True)
    transmission_type = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'full_name',
            'password',
            'user_type',
            'email',
            'phone_number',
            'photo',
            'location',
            'location_last_updated',
            'driving_experience',
            'number_of_hires',
            'bio',
            'status',
            'review_count',
            'review_stars',
            'location_reporting_type',
            'location_reporting_interval',
            'transmission_type',
        )

    def _append_location_time_if_location_request(self, validated_data):
        location = validated_data.get('location')
        if location:
            validated_data.update({'location_last_updated': timezone.now()})

    def create(self, validated_data):
        self._append_location_time_if_location_request(validated_data)
        validated_data.update({'user_type': USER_TYPE_DRIVER})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._append_location_time_if_location_request(validated_data)
        _hash_password_if_password_request(instance, validated_data)
        _calculate_new_review_average_if_review_request(
            instance, validated_data)
        return super().update(instance, validated_data)


class HireRequestSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=True)
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

    def create(self, validated_data):
        return super().create(validated_data)
