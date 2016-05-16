from rest_framework import permissions

from chauffeur.models import USER_TYPE_CUSTOMER


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.email:
            return obj.email == request.user.email
        elif request.user.username:
            return obj.email == request.user.username
        return False


class IsCustomer(permissions.BasePermission):

    message = 'Only user of type \'Customer\' is allowed to request a driver.'

    def has_permission(self, request, view):
        return request.user.user_type == USER_TYPE_CUSTOMER
