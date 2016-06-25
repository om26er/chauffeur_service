from rest_framework import permissions

from chauffeur.models import USER_TYPE_CUSTOMER, USER_TYPE_DRIVER


class IsCustomer(permissions.BasePermission):
    message = 'Only user of type \'Customer\' is allowed to request a driver.'

    def has_permission(self, request, view):
        return request.user.user_type == USER_TYPE_CUSTOMER


class IsDriver(permissions.BasePermission):
    message = 'Only user of type \'Driver\' is allowed to respond.'

    def has_permission(self, request, view):
        return request.user.user_type == USER_TYPE_DRIVER
