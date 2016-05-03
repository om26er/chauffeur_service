from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from chauffeur.models import User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER


class CustomerSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'first_name', 'last_name', 'password',
                  'email', 'phone_number', 'photo', 'location',
                  'number_of_hires', 'vehicle_type', 'vehicle_make',
                  'vehicle_model', 'vehicle_category', 'initial_app_payment')

    def create(self, validated_data):
        validated_data.update({'user_type': USER_TYPE_CUSTOMER})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            del validated_data['password']
            instance.set_password(password)
        return super().update(instance, validated_data)


class DriverSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'first_name', 'last_name', 'password',
                  'email', 'phone_number', 'photo', 'location',
                  'location_last_updated', 'driving_experience',
                  'number_of_hires', 'bio')

    def create(self, validated_data):
        validated_data.update({'user_type': USER_TYPE_DRIVER})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            del validated_data['password']
            instance.set_password(password)
        return super().update(instance, validated_data)
