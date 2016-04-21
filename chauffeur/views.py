from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chauffeur.models import User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER
from chauffeur.serializers import CustomerSerializer, DriverSerializer
from chauffeur import permissions as custom_permissions
from chauffeur import helpers


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
            if helpers.is_activation_key_valid(activation_key=activation_key):
                user = helpers.set_is_user_active(username, True)
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
