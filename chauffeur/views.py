from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView)

from chauffeur.models import User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER
from chauffeur.serializers import CustomerSerializer, DriverSerializer
from chauffeur import permissions as custom_permissions


class CustomerRegistrationView(CreateAPIView):

    serializer_class = CustomerSerializer

    def post(self, request, *args, **kwargs):
        request.data.update({'user_type': USER_TYPE_CUSTOMER})
        return super().post(request, *args, **kwargs)


class DriverRegistrationView(CreateAPIView):

    serializer_class = DriverSerializer

    def post(self, request, *args, **kwargs):
        request.data.update({'user_type': USER_TYPE_DRIVER})
        return super().post(request, *args, **kwargs)


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
