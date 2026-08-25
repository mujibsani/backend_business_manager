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
            and request.user.role == request.user.Role.ADMIN
        )


class IsManager(BasePermission):
    """
    Allows ADMIN and MANAGER users.
    """

    message = "Manager or Admin access required."

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


class IsStaff(BasePermission):
    """
    Allows authenticated business users with one of the
    permitted operational roles.

    Allowed:
        ADMIN
        MANAGER
        STAFF
    """

    message = (
        "You do not have permission to perform this action."
    )

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)

        allowed_roles = {
            "ADMIN",
            "MANAGER",
            "STAFF",
        }

        return str(role).upper() in allowed_roles


class IsAdminOrManager(BasePermission):
    """
    Allows ADMIN and MANAGER users.
    Alias-style permission for clarity.
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