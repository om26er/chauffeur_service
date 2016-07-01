import datetime

from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from simple_login.views import (
    RetrieveUpdateDestroyProfileView,
    AccountActivationAPIView,
    LoginAPIView,
    AccountRegistrationAPIView,
)

from chauffeur.models import (
    Customer,
    Driver,
    ChauffeurBaseUser,
    HireRequest,
    USER_TYPE_CUSTOMER,
    USER_TYPE_DRIVER,
    HIRE_REQUEST_ACCEPTED,
    HIRE_REQUEST_CONFLICT,
    HIRE_REQUEST_DECLINED,
)
from chauffeur.serializers import (
    ChauffeurBaseUserSerializer,
    CustomerSerializer,
    DriverSerializer,
    HireRequestSerializer,
    DriverFilterSerializer,
    HireResponseSerializer,
    ReviewSerializer,
)
from chauffeur import permissions as custom_permissions
from chauffeur import helpers
from chauffeur.helpers.user import UserHelpers
from chauffeur.helpers import (
    location as location_helpers,
    driver as driver_helpers,
)


class RegisterCustomer(AccountRegistrationAPIView):
    serializer_class = ChauffeurBaseUserSerializer
    child_serializer_class = CustomerSerializer

    def get_child_parent_relation(self):
        return 'user_id', 'id'


class RegisterDriver(AccountRegistrationAPIView):
    serializer_class = ChauffeurBaseUserSerializer
    child_serializer_class = DriverSerializer

    def get_child_parent_relation(self):
        return 'user_id', 'id'


class ActivateAccount(AccountActivationAPIView):
    user_model = ChauffeurBaseUser
    serializer_class = ChauffeurBaseUserSerializer

    def get_child_serializer_class(self):
        user = self.get_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return CustomerSerializer
        elif user.user_type == USER_TYPE_DRIVER:
            return DriverSerializer

    def get_child_model(self):
        user = self.get_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return Customer
        elif user.user_type == USER_TYPE_DRIVER:
            return Driver


class Login(LoginAPIView):
    user_model = ChauffeurBaseUser
    serializer_class = ChauffeurBaseUserSerializer

    def get_child_serializer_class(self):
        user = self.get_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return CustomerSerializer
        elif user.user_type == USER_TYPE_DRIVER:
            return DriverSerializer

    def get_child_model(self):
        user = self.get_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return Customer
        elif user.user_type == USER_TYPE_DRIVER:
            return Driver


class UserProfile(RetrieveUpdateDestroyProfileView):
    user_model = ChauffeurBaseUser
    serializer_class = ChauffeurBaseUserSerializer

    def get_child_serializer_class(self):
        user = self.get_auth_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return CustomerSerializer
        elif user.user_type == USER_TYPE_DRIVER:
            return DriverSerializer

    def get_child_model(self):
        user = self.get_auth_user()
        if user.user_type == USER_TYPE_CUSTOMER:
            return Customer
        elif user.user_type == USER_TYPE_DRIVER:
            return Driver


class FilterDrivers(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsCustomer,
    )
    serializer_class = DriverFilterSerializer

    def get_queryset(self):
        return location_helpers.filter_available_drivers(
            base_location=self.request.query_params.get('base_location', None),
            radius=self.request.query_params.get('radius', None),
            start_time=self.request.query_params.get('start_time', None),
            time_span=self.request.query_params.get('time_span', None)
        )

    def get(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        driver_serializer = DriverSerializer(self.get_queryset(), many=True)
        return Response(data=driver_serializer.data, status=status.HTTP_200_OK)


class RequestHire(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsCustomer,
    )

    def _get_driver(self, id):
        try:
            return Driver.objects.get(id=id)
        except Driver.DoesNotExist:
            return None

    def post(self, *args, **kwargs):
        self.request.data.update({'customer': self.request.user.id})
        start_time = self.request.data.get('start_time')
        if not start_time:
            now = timezone.now()
            self.request.data.update({'start_time': now})
            start_time = now
        driver_id = self.request.data.get('driver')
        time_span = self.request.data.get('time_span')
        serializer = HireRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        if not isinstance(start_time, datetime.datetime):
            # There could be some time lost between the user sends the
            # request to the service, due to network connectivity
            # or other factors.
            request_grace_period = datetime.timedelta(seconds=60)
            start_time = helpers.get_formatted_time_from_string(start_time)
            if start_time < timezone.now() - request_grace_period:
                return Response(
                    data={'start_time': 'Must not be behind current time.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        time_span = datetime.timedelta(minutes=int(time_span))
        driver = self._get_driver(id=int(driver_id))

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

    def put(self, *args, **kwargs):
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


class ListRequests(ListAPIView):
    serializer_class = HireRequestSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        if self.request.user.user_type == USER_TYPE_CUSTOMER:
            return HireRequest.objects.filter(customer_id=self.request.user.id)
        elif self.request.user.user_type == USER_TYPE_DRIVER:
            return HireRequest.objects.filter(driver=self.request.user.id)
        return None


class Review(RetrieveUpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated, )
