import datetime

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from chauffeur.models import (
    User, HireRequest, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER,
    HIRE_REQUEST_ACCEPTED, HIRE_REQUEST_CONFLICT)
from chauffeur.serializers import (
    CustomerSerializer, DriverSerializer, HireRequestSerializer)
from chauffeur import permissions as custom_permissions
from chauffeur import helpers
from chauffeur.helpers.user import UserHelpers
from chauffeur.helpers import (
    location as location_helpers,
    driver as driver_helpers)


class CustomerRegistrationView(CreateAPIView):

    serializer_class = CustomerSerializer


class DriverRegistrationView(CreateAPIView):

    serializer_class = DriverSerializer


class CustomerView(RetrieveUpdateDestroyAPIView):

    serializer_class = CustomerSerializer
    permission_classes = (
        custom_permissions.IsOwner, permissions.IsAuthenticated,
    )

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
    permission_classes = (
        custom_permissions.IsOwner, permissions.IsAuthenticated,
    )

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

        try:
            user_account = UserHelpers(email=email)
        except User.DoesNotExist:
            return Response(
                data={'email': ['Not found.']},
                status=status.HTTP_404_NOT_FOUND)

        if user_account.is_active():
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        elif user_account.is_activation_key_valid(key=activation_key):
            user_account.activate_account()
            serializer = user_account.get_serializer()
            temp_data = serializer.data
            temp_data.update({'token': user_account.get_token()})
            return Response(data=temp_data, status=status.HTTP_200_OK)
        return Response(
            data={'activation_key': ['Invalid activation key.']},
            status=status.HTTP_400_BAD_REQUEST)


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

        try:
            user_account = UserHelpers(email=email)
        except User.DoesNotExist:
            return Response(
                {'email': ['No account registered with that email.']},
                status=status.HTTP_404_NOT_FOUND)

        user = user_account.user
        if user.is_superuser or user.is_staff:
            return Response(
                {'email': ['Cannot reset password for admin.']},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            helpers.generate_password_reset_key_and_send_email(user=user)
            return Response(status=status.HTTP_200_OK)


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

        try:
            user_account = UserHelpers(email=email)
        except User.DoesNotExist:
            return Response(
                {'email': ['No account registered with that email.']},
                status=status.HTTP_404_NOT_FOUND)

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

        try:
            user_account = UserHelpers(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user_account.is_active():
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class FilterDriversView(ListAPIView):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = DriverSerializer

    def get_queryset(self):
        return location_helpers.filter_available_drivers(
            base_location=self.request.query_params.get('base_location', None),
            radius=self.request.query_params.get('radius', None),
            start_time=self.request.query_params.get('start_time', None),
            time_span=self.request.query_params.get('time_span', None))

    def _validate_data(self, radius, base_location, start_time, time_span):
        message = {}
        if not radius:
            message.update({'radius': ['Field is mandatory.']})

        if not base_location:
            message.update({'base_location': ['Field is mandatory.']})

        if not start_time:
            message.update({'start_time': ['Field is mandatory.']})

        if not time_span:
            message.update({'time_span': ['Field is mandatory.']})

        return message

    def get(self, request, *args, **kwargs):
        radius = request.query_params.get('radius', None)
        base_location = request.query_params.get('base_location', None)
        start_time = request.query_params.get('start_time', None)
        time_span = request.query_params.get('time_span', None)
        message = self._validate_data(
            radius, base_location, start_time, time_span)
        if len(message) > 0:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)


class UserDetailsView(APIView):
    permission_classes = (
        custom_permissions.IsOwner, permissions.IsAuthenticated,
    )

    def get(self, request, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        if user.user_type == USER_TYPE_CUSTOMER:
            serializer = CustomerSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.user_type == USER_TYPE_DRIVER:
            serializer = DriverSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ActivationKeyView(APIView):

    def post(self, request, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response(
                data={'email': ['Field is mandatory.']},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            user_account = UserHelpers(email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user_account.is_active():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            helpers.send_account_activation_email(
                user_account.user.email, user_account.user.activation_key)
            return Response(status=status.HTTP_200_OK)


class HireRequestView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, custom_permissions.IsCustomer, )

    def _get_driver(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        request.data.update({'customer': self.request.user.id})
        driver_id = int(request.data.get('driver'))
        start_time = request.data.get('start_time')
        time_span = datetime.timedelta(
            minutes=int(request.data.get('time_span')))

        driver = self._get_driver(id=driver_id)
        start_time = helpers.get_formatted_time_from_string(start_time)
        if start_time < timezone.now():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if driver_helpers.is_driver_available_for_hire(driver, start_time,
                                                       start_time + time_span):
            serializer = HireRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                helpers.send_hire_request_push_notification(
                    driver.push_notification_key, serializer.data)
                return Response(
                    data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_409_CONFLICT)


class HireResponseView(APIView):
    permission_classes = (
        permissions.IsAuthenticated, custom_permissions.IsDriver, )

    def _validate_data(self, request_id, status):
        message = {}
        if not request_id:
            message.update({'request_id': ['Field is mandatory.']})

        if not status:
            message.update({'status': ['Field is mandatory.']})

        return message

    def patch(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        status = request.data.get('status')
        message = self._validate_data(request_id, status)
        if message:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        hire_request = HireRequest.objects.get(id=request_id)
        serializer = HireRequestSerializer(
            hire_request, data=request.data, partial=True)

        if serializer.is_valid():
            customer = UserHelpers(id=hire_request.customer_id)
            if status == HIRE_REQUEST_ACCEPTED:
                driver = UserHelpers(id=self.request.user.id)
                driver.append_hire_count()
                customer.append_hire_count()

            serializer.save()
            helpers.send_hire_response_push_notification(
                customer.get_push_key(), serializer.data)

            superseded_data = serializer.data
            superseded_data.update({'status', HIRE_REQUEST_CONFLICT})
            helpers.send_superseded_notification(
                self.request.user, hire_request, superseded_data)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
