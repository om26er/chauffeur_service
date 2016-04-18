from rest_framework.generics import(
    ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework import permissions

from chauffeur.models import Customer, Driver
from chauffeur import permissions as chauffeur_permissions
from chauffeur.serializers import CustomerSerializer, DriverSerializer


class CustomerRegistrationView(CreateAPIView):

    serializer_class = CustomerSerializer


class DriverRegistrationView(CreateAPIView):

    serializer_class = DriverSerializer


class CustomerView(RetrieveUpdateDestroyAPIView):

    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.filter(id=self.kwargs.get('pk'))


class DriverView(RetrieveUpdateDestroyAPIView):

    serializer_class = DriverSerializer

    def get_queryset(self):
        return Driver.objects.filter(id=self.kwargs.get('pk'))


class CustomersListView(ListAPIView):

    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = (permissions.IsAdminUser, )


class DriversListView(ListAPIView):

    serializer_class = DriverSerializer
    queryset = Driver.objects.all()
    permission_classes = (permissions.IsAdminUser, )
