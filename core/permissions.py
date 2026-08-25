from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allows access only to users with ADMIN application role.
    """

    message = "Admin access required."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            == request.user.Role.ADMIN
        )


class IsManager(BasePermission):
    """
    Allows MANAGER users only.
    """

    message = "Manager access required."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            == request.user.Role.MANAGER
        )


class IsStaff(BasePermission):
    """
    Allows all authenticated application users.

    ADMIN
    MANAGER
    STAFF
    """

    message = "Authenticated user access required."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (
                request.user.Role.ADMIN,
                request.user.Role.MANAGER,
                request.user.Role.STAFF,
            )
        )


class IsAdminOrManager(BasePermission):
    """
    Allows ADMIN and MANAGER users.
    """

    message = "Admin or Manager access required."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (
                request.user.Role.ADMIN,
                request.user.Role.MANAGER,
            )
        )