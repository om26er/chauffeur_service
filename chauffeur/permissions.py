from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.email:
            return obj.email == request.user.email
        elif request.user.username:
            return obj.email == request.user.username
        return False
