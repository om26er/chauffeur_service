from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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


class AccountActivationView(APIView):

    def _does_user_exist(self, username):
        try:
            User.objects.get(username=username)
            return True
        except User.DoesNotExist:
            return False

    def _is_activation_key_valid(self, activation_key):
        return False

    def post(self, request, **kwargs):
        message = {}
        username = request.data.get('username')
        activation_key = request.data.get('activation_key')
        if not username:
            message.update({'username': 'Field is mandatory'})

        if not activation_key:
            message.update({'activation_key': 'Field is mandatory'})

        if len(message) > 0:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        if self._does_user_exist(username=username):
            if self._is_activation_key_valid(activation_key=activation_key):
                User.objects.get(username=username).is_active = True
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(
                    data={'activation_key': 'Invalid key'},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                data={'username': 'User with that name already exists'},
                status=status.HTTP_400_BAD_REQUEST)
