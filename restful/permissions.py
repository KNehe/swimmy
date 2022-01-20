from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a booking to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
