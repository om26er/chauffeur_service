import datetime

from django.utils import timezone
from django.http import HttpResponse
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    GenericAPIView,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from simple_login.views import (
    RetrieveUpdateDestroyProfileAPIView,
    ActivationAPIView,
    LoginAPIView,
)

from chauffeur.models import (
    ChauffeurUser,
    HireRequest,
    Review,
    PushIDs,
    Charge,
    Segment,
    USER_TYPE_CUSTOMER,
    USER_TYPE_DRIVER,
    HIRE_REQUEST_PENDING,
    HIRE_REQUEST_ACCEPTED,
    HIRE_REQUEST_IN_PROGRESS,
    HIRE_REQUEST_CONFLICT,
    HIRE_REQUEST_DECLINED,
    HIRE_REQUEST_DONE,
    REVIEW_STATUS_DONE,
    REVIEW_STATUS_DRIVER_DONE,
    REVIEW_STATUS_CUSTOMER_DONE,
)
from chauffeur.serializers import (
    CustomerSerializer,
    DriverSerializer,
    HireRequestSerializer,
    DriverFilterSerializer,
    HireResponseSerializer,
    ReviewSerializer,
    PushIdSerializer,
    PricingSerializer,
    PriceValidator,
)
from chauffeur.responses import (
    BadRequest,
    Forbidden,
    NotModified,
    Ok,
    Conflict,
)
from chauffeur.paytm.helpers import verify, generate
from chauffeur import permissions as custom_permissions
from chauffeur import helpers as h
from chauffeur.helpers.user import UserHelpers
from chauffeur.helpers import (
    location as location_helpers,
    driver as driver_helpers,
)

MSG_NOT_APPROVED_BY_ADMIN = {'reason': 'NEED_ADMIN_APPROVAL'}


def update_end_time_to_string(serializer_data):
    request_end_time = serializer_data['end_time']
    if isinstance(request_end_time, datetime.datetime):
        serializer_data.update({'end_time': request_end_time.isoformat()})
    return serializer_data


def get_user_push_keys(user_instance):
    push_instances = PushIDs.objects.filter(user=user_instance)
    return [obj.push_key for obj in push_instances]


def get_serializer_class_by_user(user):
    if user.user_type == USER_TYPE_CUSTOMER:
        return CustomerSerializer
    elif user.user_type == USER_TYPE_DRIVER:
        return DriverSerializer


def add_price_to_data(data):
    obj = Charge.objects.get(id=int(data['price']))
    serializer = PricingSerializer(instance=obj)
    data.update({'price': serializer.data})
    return data


def is_driver_and_needs_admin_approval(user):
    return user.user_type == USER_TYPE_DRIVER \
            and not user.is_approved_by_admin


class RegisterCustomer(CreateAPIView):
    serializer_class = CustomerSerializer


class RegisterDriver(CreateAPIView):
    serializer_class = DriverSerializer


class ActivateAccount(ActivationAPIView):
    user_model = ChauffeurUser

    def get_serializer_class(self):
        return get_serializer_class_by_user(self.get_user())

    def post(self, *args, **kwargs):
        result = super().post(*args, **kwargs)
        if result.status_code == status.HTTP_200_OK and \
                is_driver_and_needs_admin_approval(self.get_user()):
            return Response(
                data=MSG_NOT_APPROVED_BY_ADMIN,
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            return result


class Login(LoginAPIView):
    user_model = ChauffeurUser

    def get_serializer_class(self):
        return get_serializer_class_by_user(self.get_user())

    def post(self, *args, **kwargs):
        result = super().post(*args, **kwargs)
        if is_driver_and_needs_admin_approval(self.get_user()):
            return Response(
                data=MSG_NOT_APPROVED_BY_ADMIN,
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            return result


class UserProfile(RetrieveUpdateDestroyProfileAPIView):
    user_model = ChauffeurUser

    def get_serializer_class(self):
        return get_serializer_class_by_user(self.get_user())


class UserPublicProfile(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ['get']

    def get_queryset(self):
        try:
            return ChauffeurUser.objects.get(id=self.kwargs['pk'])
        except ChauffeurUser.DoesNotExist:
            return None

    def get_serializer_class(self):
        if self.request.user.user_type == USER_TYPE_DRIVER:
            return CustomerSerializer
        elif self.request.user.user_type == USER_TYPE_CUSTOMER:
            return DriverSerializer

    def get(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=self.get_queryset())
        return Ok(serializer.data)


class ActiveRequests(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = HireRequestSerializer

    def is_customer(self):
        return self.request.user.user_type == USER_TYPE_CUSTOMER

    def is_driver(self):
        return self.request.user.user_type == USER_TYPE_DRIVER

    def get_queryset(self):
        if self.is_customer():
            id_parameter = 'customer_id'
        elif self.is_driver():
            id_parameter = 'driver_id'
        else:
            id_parameter = None

        return HireRequest.objects.filter(
            status__in=[
                HIRE_REQUEST_PENDING,
                HIRE_REQUEST_ACCEPTED,
                HIRE_REQUEST_IN_PROGRESS
            ],
            **{id_parameter: self.request.user.id}
        )

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        data = [add_price_to_data(dict(d)) for d in serializer.data]
        return Ok(data)


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
        return Ok(driver_serializer.data)


class RequestHire(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsCustomer,
    )

    def _get_driver(self, driver_id):
        try:
            return ChauffeurUser.objects.get(id=driver_id)
        except ChauffeurUser.DoesNotExist:
            return None

    def get_price(self, time_span):
        vehicle_type = self.request.user.vehicle_type
        segment = Segment.objects.get(identifier=vehicle_type)
        return Charge.objects.get(segment=segment, hours=int(time_span))

    def post(self, *args, **kwargs):
        customer = self.request.user
        self.request.data.update({'customer': customer.id})
        start_time = self.request.data.get('start_time')
        if not start_time:
            now = timezone.now()
            self.request.data.update({'start_time': now})
            start_time = now
        driver_id = self.request.data.get('driver')
        time_span = self.request.data.get('time_span')
        price = self.get_price(time_span)
        self.request.data.update({'price': price.id})
        serializer = HireRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        if not isinstance(start_time, datetime.datetime):
            # There could be some time lost between the user sends the
            # request to the service, due to network connectivity
            # or other factors.
            request_grace_period = datetime.timedelta(seconds=60)
            start_time = h.get_formatted_time_from_string(start_time)
            if start_time < timezone.now() - request_grace_period:
                data = {'start_time': 'Must not be behind current time.'}
                return BadRequest(data)
        time_span = datetime.timedelta(hours=int(time_span))
        driver = self._get_driver(int(driver_id))

        if driver_helpers.is_driver_available_for_hire(
                driver,
                start_time,
                start_time + time_span
        ):
            serializer.save()
            data = update_end_time_to_string(serializer.data)
            add_price_to_data(data)
            push_ids = get_user_push_keys(driver)
            h.send_hire_request_push_notification(push_ids, data)
            return Ok(data)
        else:
            return Conflict()


class RespondHire(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ['put']

    def get_queryset(self):
        return HireRequest.objects.get(id=self.kwargs['pk'])

    def is_customer(self):
        return self.request.user.user_type == USER_TYPE_CUSTOMER

    def is_driver(self):
        return self.request.user.user_type == USER_TYPE_DRIVER

    @property
    def user_id(self):
        return self.request.user.id

    def put(self, *args, **kwargs):
        data = self.request.data
        parameter_checker = HireResponseSerializer(data=data)
        parameter_checker.is_valid(raise_exception=True)
        hire_request = self.get_queryset()

        if self.is_customer():
            if hire_request.customer_id != self.user_id:
                return BadRequest({'message': 'You are not the requester.'})
        elif self.is_driver():
            if hire_request.driver_id != self.user_id:
                return BadRequest({'message': 'You are not the requestee.'})

        new_status = int(data.get('status'))
        if new_status < hire_request.status:
            return BadRequest({'message': 'Cannot go back.'})
        if new_status <= HIRE_REQUEST_PENDING or \
                new_status > HIRE_REQUEST_DONE:
            return BadRequest({'message': 'Unsupported status.'})

        if hire_request.status == HIRE_REQUEST_DECLINED:
            return BadRequest({
                    'message':
                    'Not allowed to change an already declined request.'
                })
        elif hire_request.status == new_status:
            return NotModified()

        if self.is_customer():
            if new_status == HIRE_REQUEST_ACCEPTED or \
                    new_status == HIRE_REQUEST_DECLINED:
                return BadRequest({
                        'message':
                        'Only drivers can accept/decline.'
                    })

        serializer = HireRequestSerializer(
            hire_request,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        customer = UserHelpers(id=hire_request.customer_id)
        LIST = [
            HIRE_REQUEST_ACCEPTED,
            HIRE_REQUEST_DECLINED,
            HIRE_REQUEST_IN_PROGRESS,
        ]
        if new_status in LIST:
            data = update_end_time_to_string(serializer.data)
            push_ids = get_user_push_keys(customer.user)
            h.send_hire_response_push_notification(push_ids, data)

        if new_status == HIRE_REQUEST_DONE:
            h.send_hire_response_push_notification(
                get_user_push_keys(hire_request.driver),
                update_end_time_to_string(serializer.data)
            )

        if new_status == HIRE_REQUEST_ACCEPTED:
            driver = UserHelpers(id=self.request.user.id)
            driver.append_hire_count()
            customer.append_hire_count()
            data.update({'status': HIRE_REQUEST_CONFLICT})
            h.send_superseded_notification(
                self.request.user,
                hire_request,
                data
            )
        return Ok(serializer.data)


class ListRequests(APIView):
    serializer_class = HireRequestSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        if self.request.user.user_type == USER_TYPE_CUSTOMER:
            return HireRequest.objects.filter(customer_id=self.request.user.id)
        elif self.request.user.user_type == USER_TYPE_DRIVER:
            return HireRequest.objects.filter(driver_id=self.request.user.id)
        return None

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        data = [add_price_to_data(dict(d)) for d in serializer.data]
        return Ok(data)


class PushId(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = PushIdSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        data.update({'user': self.request.user.id})
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            push_id = PushIDs.objects.get(
                device_id=self.request.data.get('device_id')
            )
            serializer = self.serializer_class(
                instance=push_id,
                data=self.request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except PushIDs.DoesNotExist:
            serializer.save()
        return Ok(serializer.data)


class ReviewView(RetrieveUpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ['put', 'get']

    def get_object(self):
        request_id = self.kwargs.get('pk')
        return Review.objects.get(request_id=request_id)

    def get_queryset(self):
        request_id = self.kwargs.get('pk')
        return Review.objects.get(request_id=request_id)

    def is_customer(self):
        return self.request.user.user_type == USER_TYPE_CUSTOMER

    def is_driver(self):
        return self.request.user.user_type == USER_TYPE_DRIVER

    def update(self, request, *args, **kwargs):
        review_object = self.get_queryset()
        if review_object.status == REVIEW_STATUS_DONE:
            return Forbidden({'reason': 'Cannot change finished review.'})
        if self.is_customer():
            if review_object.status == REVIEW_STATUS_CUSTOMER_DONE:
                return NotModified({'reason': 'Review already done'})
        if self.is_driver():
            if review_object.status == REVIEW_STATUS_DRIVER_DONE:
                return NotModified({'reason': 'Review already done'})
        serializer = self.serializer_class(
            instance=review_object,
            data=self.request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        review_status_new = serializer.data.get('status')
        if review_status_new == REVIEW_STATUS_DONE:
            customer = review_object.request.customer
            driver = review_object.request.driver
            customer_review = serializer.data.get('customer_review')
            driver_review = serializer.data.get('driver_review')
            calculate_and_set_review(customer, customer_review)
            calculate_and_set_review(driver, driver_review)
        return Ok(serializer.data)


def calculate_and_set_review(instance, review_stars):
    current_review_count = instance.review_count
    current_review_stars = instance.review_stars
    current_total = current_review_count * current_review_stars
    new_total = current_total + review_stars
    instance.review_count += 1
    instance.review_stars = new_total / instance.review_count
    instance.save()


class GetPrice(APIView):
    def post(self, *args, **kwargs):
        validator = PriceValidator(data=self.request.data)
        validator.is_valid(raise_exception=True)
        hours = int(self.request.data.get('hours'))
        segment = int(self.request.data.get('segment'))
        obj = Charge.objects.filter(segment__identifier=segment, hours=hours)
        if not obj:
            return BadRequest({'message': 'Non supported price filter.'})
        serializer = PricingSerializer(instance=obj[0])
        return Ok(serializer.data)


class PaytmView(APIView):
    def _get_request_data(self, method):
        if method == 'GET':
            return self.request.query_params.dict()
        else:
            return self.request.data.dict()

    def _common(self, method):
        request_endpoint = self.request.path_info.split('/')[-1]
        if request_endpoint == 'generatechecksum.cgi':
            return HttpResponse(
                generate(dict(self._get_request_data(method))))
        elif request_endpoint == 'verifychecksum.cgi':
            return HttpResponse(
                verify(dict(self._get_request_data(method))))
        else:
            # Wont ever reach here
            return HttpResponse('unknown url')

    def get(self, *args, **kwargs):
        return self._common('GET')

    def post(self, *args, **kwargs):
        return self._common('POST')
