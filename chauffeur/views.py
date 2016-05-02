from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chauffeur.models import User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER
from chauffeur.serializers import CustomerSerializer, DriverSerializer
from chauffeur import permissions as custom_permissions
from chauffeur import helpers
from chauffeur.helpers.user import UserHelpers


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

    def put(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().patch(request, *args, **kwargs)


class DriverView(RetrieveUpdateDestroyAPIView):

    serializer_class = DriverSerializer
    permission_classes = (custom_permissions.IsOwner, )

    def get_queryset(self):
        return User.objects.filter(
            user_type=USER_TYPE_DRIVER, id=self.kwargs.get('pk'))

    def patch(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().put(request, *args, **kwargs)


class AccountActivationView(APIView):
    def _validate_data(self, email, activation_key):
        message = {}
        if not email:
            message.update({'email': ['Field is mandatory.']})

        if not activation_key:
            message.update({'activation_key': ['Field is mandatory.']})

        return message

    def post(self, request, **kwargs):
        email = request.data.get('email')
        activation_key = request.data.get('activation_key')
        message = self._validate_data(email, activation_key)
        if len(message) > 0:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        user_account = UserHelpers(email=email)
        if user_account.exists():
            if user_account.is_active():
                return Response(status=status.HTTP_304_NOT_MODIFIED)
            elif user_account.is_activation_key_valid(key=activation_key):
                user_account.activate_account()
                serializer = user_account.get_serializer()
                return Response(
                    data=serializer.data, status=status.HTTP_200_OK)
            return Response(
                data={'activation_key': ['Invalid activation key.']},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            data={'email': ['Not found.']}, status=status.HTTP_404_NOT_FOUND)


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

        user_account = UserHelpers(email=email)
        if user_account.exists():
            user = user_account.user
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


class PasswordChangeView(APIView):
    def _validate_data(self, email, password_reset_key, new_password):
        message = {}
        if not email:
            message.update({'email': ['Field is mandatory.']})

        if not password_reset_key:
            message.update({'password_reset_key': ['Field is mandatory.']})

        if not new_password:
            message.update({'new_password': ['Field is mandatory.']})
        return message

    def post(self, request, **kwargs):
        email = request.data.get('email')
        password_reset_key = request.data.get('password_reset_key')
        new_password = request.data.get('new_password')
        message = self._validate_data(email, password_reset_key, new_password)
        if len(message) > 0:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        user_account = UserHelpers(email=email)
        if user_account.exists():
            user = user_account.user
            if user.is_superuser or user.is_staff:
                return Response(
                    {'email': ['Cannot changed password for admin.']},
                    status=status.HTTP_400_BAD_REQUEST)
            if user_account.is_password_reset_valid(key=password_reset_key):
                user_account.change_password(new_password=new_password)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(
                    {'password_reset_key': ['Invalid password reset key.']},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {'email': ['No account registered with that email.']},
                status=status.HTTP_404_NOT_FOUND)


class UserStatusView(APIView):
    def get(self, request, **kwargs):
        email = request.query_params.get('email', None)
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

        user_account = UserHelpers(email=email)
        if not user_account.user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif not user_account.is_active():
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)
