from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username

    def has_permission(self, request, view):
        return super().has_permission(request, view)
