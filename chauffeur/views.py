from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chauffeur.models import (
    User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER, ACTIVATION_KEY_DEFAULT,
    PASSWORD_RESET_KEY_DEFAULT)
from chauffeur.serializers import CustomerSerializer, DriverSerializer
from chauffeur import permissions as custom_permissions
from chauffeur import helpers


class CustomerRegistrationView(CreateAPIView):

    serializer_class = CustomerSerializer


class DriverRegistrationView(CreateAPIView):

    serializer_class = DriverSerializer


class CustomerView(RetrieveUpdateDestroyAPIView):

    serializer_class = CustomerSerializer
    permission_classes = (custom_permissions.IsOwner,)

    def get_queryset(self):
        return User.objects.filter(
            user_type=USER_TYPE_CUSTOMER, id=self.kwargs.get('pk'))


class DriverView(RetrieveUpdateDestroyAPIView):

    serializer_class = DriverSerializer
    permission_classes = (custom_permissions.IsOwner, )

    def get_queryset(self):
        return User.objects.filter(
            user_type=USER_TYPE_DRIVER, id=self.kwargs.get('pk'))


class AccountActivationView(APIView):
    def _validate_data(self, username, activation_key):
        message = {}
        if not username:
            message.update({'username': ['Field is mandatory.']})

        if not activation_key:
            message.update({'activation_key': ['Field is mandatory.']})

        return message

    def post(self, request, **kwargs):
        username = request.data.get('username')
        activation_key = request.data.get('activation_key')
        message = self._validate_data(username, activation_key)
        if len(message) > 0:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        if helpers.does_user_exist(username=username):
            if helpers.is_user_active(username=username):
                return Response(status=status.HTTP_304_NOT_MODIFIED)
            elif helpers.is_activation_key_valid(
                    username=username, activation_key=activation_key):
                user = helpers.set_is_user_active(username, True)
                user.activation_key = ACTIVATION_KEY_DEFAULT
                user.save()
                serializer = helpers.get_user_serializer_by_type(user)
                return Response(
                    data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    data={'activation_key': ['Invalid activation key.']},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                data={'username': ['Not found.']},
                status=status.HTTP_404_NOT_FOUND)


class RequestPasswordResetView(APIView):
    def post(self, request, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response(
                {'email': ['Field is mandatory.']},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'email': ['Invalid email address.']},
                status=status.HTTP_400_BAD_REQUEST)

        if helpers.does_user_exist(email=email):
            user = User.objects.get(email=email)
            if user.is_superuser or user.is_staff:
                return Response(
                    {'email': ['Cannot reset password for admin.']},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                helpers.generate_password_reset_key_and_send_email(user=user)
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                {'email': ['No account registered with that email.']},
                status=status.HTTP_404_NOT_FOUND)


class PasswordChangeWithKeyView(APIView):
    def post(self, request, **kwargs):
        username = request.data.get('username')
        password_reset_key = request.data.get('password_reset_key')
        new_password = request.data.get('new_password')
        message = {}
        if not username:
            message.update({'username': ['Field is mandatory.']})

        if not password_reset_key:
            message.update({'password_reset_key': ['Field is mandatory.']})

        if not new_password:
            message.update({'new_password': ['Field is mandatory.']})

        if len(message) > 0:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        if helpers.does_user_exist(username=username):
            user = User.objects.get(username=username)
            if user.is_superuser or user.is_staff:
                return Response(
                    {'email': ['Cannot changed password for admin.']},
                    status=status.HTTP_400_BAD_REQUEST)

            if helpers.is_password_reset_key_valid(
                    username=username, password_reset_key=password_reset_key):
                user.set_password(new_password)
                user.password_reset_key = PASSWORD_RESET_KEY_DEFAULT
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(
                    {'password_reset_key': ['Invalid password reset key.']},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {'email': ['No account registered with that username.']},
                status=status.HTTP_404_NOT_FOUND)
