import datetime

from django.utils import timezone
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from simple_login.views import RetrieveUpdateDestroyProfileView

from chauffeur.models import (
    User,
    HireRequest,
    USER_TYPE_CUSTOMER,
    USER_TYPE_DRIVER,
    HIRE_REQUEST_ACCEPTED,
    HIRE_REQUEST_CONFLICT,
    HIRE_REQUEST_DECLINED,
)
from chauffeur.serializers import (
    CustomerSerializer,
    DriverSerializer,
    HireRequestSerializer,
    DriverFilterSerializer,
    HireResponseSerializer,
)
from chauffeur import permissions as custom_permissions
from chauffeur import helpers
from chauffeur.helpers.user import UserHelpers
from chauffeur.helpers import (
    location as location_helpers,
    driver as driver_helpers,
)


class RegisterCustomer(CreateAPIView):
    serializer_class = CustomerSerializer


class RegisterDriver(CreateAPIView):
    serializer_class = DriverSerializer


class FilterDrivers(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = DriverFilterSerializer

    def get_queryset(self):
        return location_helpers.filter_available_drivers(
            base_location=self.request.query_params.get('base_location', None),
            radius=self.request.query_params.get('radius', None),
            start_time=self.request.query_params.get('start_time', None),
            time_span=self.request.query_params.get('time_span', None)
        )

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        driver_serializer = DriverSerializer(self.get_queryset(), many=True)
        return Response(data=driver_serializer.data, status=status.HTTP_200_OK)


class UserProfile(RetrieveUpdateDestroyProfileView):
    def get_serializer_class(self):
        user = self.get_auth_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return CustomerSerializer
        elif user.user_type == USER_TYPE_DRIVER:
            return DriverSerializer


class RequestHire(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsCustomer,
    )

    def _get_driver(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        self.request.data.update({'customer': self.request.user.id})
        driver_id = self.request.data.get('driver')
        start_time = self.request.data.get('start_time')
        time_span = self.request.data.get('time_span')
        serializer = HireRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        time_span = datetime.timedelta(minutes=int(time_span))
        driver = self._get_driver(id=int(driver_id))
        start_time = helpers.get_formatted_time_from_string(start_time)
        if start_time < timezone.now():
            return Response(
                data={'start_time': 'Must not be behind current time.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if driver_helpers.is_driver_available_for_hire(
                driver,
                start_time,
                start_time + time_span
        ):
            serializer.save()
            helpers.send_hire_request_push_notification(
                driver.push_notification_key,
                serializer.data
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(status=status.HTTP_409_CONFLICT)


class RespondHire(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsDriver,
    )

    def put(self, request, *args, **kwargs):
        data = self.request.data
        parameter_checker = HireResponseSerializer(data=data)
        parameter_checker.is_valid(raise_exception=True)

        request_id = data.get('request_id')
        new_status = data.get('status')

        hire_request = HireRequest.objects.get(id=request_id)
        if hire_request.status == HIRE_REQUEST_DECLINED:
            return Response(
                data={'Not allowed to change an already declined request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif hire_request.status == int(new_status):
            return Response(status=status.HTTP_304_NOT_MODIFIED)

        serializer = HireRequestSerializer(
            hire_request,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        customer = UserHelpers(id=hire_request.customer_id)
        if new_status == HIRE_REQUEST_ACCEPTED:
            driver = UserHelpers(id=self.request.user.id)
            driver.append_hire_count()
            customer.append_hire_count()

        helpers.send_hire_response_push_notification(
            customer.get_push_key(),
            serializer.data
        )

        superseded_data = serializer.data
        superseded_data.update({'status': HIRE_REQUEST_CONFLICT})
        helpers.send_superseded_notification(
            self.request.user,
            hire_request,
            superseded_data
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)
