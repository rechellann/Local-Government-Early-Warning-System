from rest_framework import permissions


class IsLGUAdmin(permissions.BasePermission):
    """
    Custom permission to only allow LGU Admin users to access.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return 'LGU Admin' in request.user.groups.values_list('name', flat=True)


class IsDispatcherOrLGUAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Dispatcher or LGU Admin users to access.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        user_groups = request.user.groups.values_list('name', flat=True)
        return 'LGU Admin' in user_groups or 'Dispatcher' in user_groups