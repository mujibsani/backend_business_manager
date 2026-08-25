from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction


User = get_user_model()


# ==========================================================
# HELPERS
# ==========================================================

def _validate_role(role):
    """
    Validate that the supplied role is a valid
    Business Manager role.
    """

    if role not in User.Role.values:
        raise ValidationError(
            f"Invalid role: {role}"
        )

    return role


def _validate_password(password):
    """
    Basic password validation.

    Django's password validators will also run when
    passwords are validated through forms/admin.
    """

    if not password:
        raise ValidationError(
            "Password is required."
        )

    if len(password) < 8:
        raise ValidationError(
            "Password must contain at least 8 characters."
        )


def _validate_username(username):
    """
    Validate username.
    """

    if not username:
        raise ValidationError(
            "Username is required."
        )

    username = username.strip()

    if not username:
        raise ValidationError(
            "Username cannot be empty."
        )

    return username


# ==========================================================
# CREATE USER
# ==========================================================

@transaction.atomic
def create_user(
    *,
    username,
    password,
    role=User.Role.STAFF,
    first_name="",
    last_name="",
    email="",
    created_by=None,
):
    """
    Create a Business Manager user.

    Rules:

        ADMIN
            Can create ADMIN, MANAGER and STAFF.

        MANAGER
            Can create STAFF only.

        STAFF
            Cannot create users.
    """

    username = _validate_username(username)
    _validate_password(password)
    role = _validate_role(role)

    # ------------------------------------------------------
    # Check username
    # ------------------------------------------------------

    if User.objects.filter(
        username__iexact=username
    ).exists():

        raise ValidationError(
            "A user with this username already exists."
        )

    # ------------------------------------------------------
    # Authorization
    # ------------------------------------------------------

    if created_by is not None:

        if not created_by.is_authenticated:
            raise ValidationError(
                "Authentication is required."
            )

        # STAFF cannot create users.
        if created_by.role == User.Role.STAFF:
            raise ValidationError(
                "Staff users cannot create users."
            )

        # MANAGER can create STAFF only.
        if (
            created_by.role == User.Role.MANAGER
            and role != User.Role.STAFF
        ):
            raise ValidationError(
                "Managers can create Staff users only."
            )

    # ------------------------------------------------------
    # Create user
    # ------------------------------------------------------

    user = User(
        username=username,
        first_name=first_name or "",
        last_name=last_name or "",
        email=email or "",
        role=role,
        is_active=True,
    )

    user.set_password(password)
    user.save()

    return user


# ==========================================================
# UPDATE USER
# ==========================================================

@transaction.atomic
def update_user(
    *,
    user,
    first_name=None,
    last_name=None,
    email=None,
    is_active=None,
):
    """
    Update basic user information.

    Role changes are intentionally handled separately.
    """

    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    if email is not None:
        user.email = email

    if is_active is not None:
        user.is_active = is_active

    user.save(
        update_fields=[
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]
    )

    return user


# ==========================================================
# CHANGE ROLE
# ==========================================================

@transaction.atomic
def change_user_role(
    *,
    user,
    new_role,
    changed_by,
):
    """
    Change a user's Business Manager role.

    Rules:

        ADMIN
            Can assign any role.

        MANAGER
            Can assign STAFF only.

        STAFF
            Cannot change roles.

    Additional safety:

        A user cannot change their own role.
    """

    if not changed_by:
        raise ValidationError(
            "Authenticated user is required."
        )

    if not changed_by.is_authenticated:
        raise ValidationError(
            "Authentication is required."
        )

    new_role = _validate_role(new_role)

    # ------------------------------------------------------
    # Prevent self role modification
    # ------------------------------------------------------

    if user.pk == changed_by.pk:
        raise ValidationError(
            "You cannot change your own role."
        )

    # ------------------------------------------------------
    # Authorization
    # ------------------------------------------------------

    if changed_by.role == User.Role.STAFF:

        raise ValidationError(
            "Staff users cannot change user roles."
        )

    if (
        changed_by.role == User.Role.MANAGER
        and new_role != User.Role.STAFF
    ):

        raise ValidationError(
            "Managers can assign Staff role only."
        )

    # ------------------------------------------------------
    # Protect the last active Admin
    # ------------------------------------------------------

    if user.role == User.Role.ADMIN:

        if new_role != User.Role.ADMIN:

            active_admin_count = User.objects.filter(
                role=User.Role.ADMIN,
                is_active=True,
            ).exclude(
                pk=user.pk
            ).count()

            if active_admin_count == 0:

                raise ValidationError(
                    "The last active Admin cannot "
                    "be demoted."
                )

    # ------------------------------------------------------
    # Change role
    # ------------------------------------------------------

    user.role = new_role

    user.save(
        update_fields=[
            "role",
        ]
    )

    return user


# ==========================================================
# ACTIVATE USER
# ==========================================================

@transaction.atomic
def activate_user(
    *,
    user,
    activated_by,
):
    """
    Activate a user.

    ADMIN and MANAGER can activate users.
    STAFF cannot.
    """

    if not activated_by:
        raise ValidationError(
            "Authenticated user is required."
        )

    if not activated_by.is_authenticated:
        raise ValidationError(
            "Authentication is required."
        )

    if activated_by.role == User.Role.STAFF:
        raise ValidationError(
            "Staff users cannot activate users."
        )

    user.is_active = True

    user.save(
        update_fields=[
            "is_active",
        ]
    )

    return user


# ==========================================================
# DEACTIVATE USER
# ==========================================================

@transaction.atomic
def deactivate_user(
    *,
    user,
    deactivated_by,
):
    """
    Deactivate a user.

    ADMIN and MANAGER can deactivate users.

    Safety:
        - Cannot deactivate yourself.
        - Cannot deactivate the last active Admin.
    """

    if not deactivated_by:
        raise ValidationError(
            "Authenticated user is required."
        )

    if not deactivated_by.is_authenticated:
        raise ValidationError(
            "Authentication is required."
        )

    if deactivated_by.role == User.Role.STAFF:
        raise ValidationError(
            "Staff users cannot deactivate users."
        )

    # ------------------------------------------------------
    # Prevent self deactivation
    # ------------------------------------------------------

    if user.pk == deactivated_by.pk:

        raise ValidationError(
            "You cannot deactivate yourself."
        )

    # ------------------------------------------------------
    # Protect last active Admin
    # ------------------------------------------------------

    if user.role == User.Role.ADMIN:

        active_admin_count = User.objects.filter(
            role=User.Role.ADMIN,
            is_active=True,
        ).count()

        if active_admin_count <= 1:

            raise ValidationError(
                "The last active Admin cannot "
                "be deactivated."
            )

    # ------------------------------------------------------
    # Deactivate
    # ------------------------------------------------------

    user.is_active = False

    user.save(
        update_fields=[
            "is_active",
        ]
    )

    return user


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@transaction.atomic
def change_password(
    *,
    user,
    old_password,
    new_password,
    confirm_password,
):
    """
    Change the authenticated user's password.
    """

    if not user:
        raise ValidationError(
            "User is required."
        )

    if not user.is_authenticated:
        raise ValidationError(
            "Authentication is required."
        )

    # ------------------------------------------------------
    # Validate old password
    # ------------------------------------------------------

    if not user.check_password(old_password):

        raise ValidationError(
            "Current password is incorrect."
        )

    # ------------------------------------------------------
    # Validate new password
    # ------------------------------------------------------

    _validate_password(new_password)

    if new_password != confirm_password:

        raise ValidationError(
            "New passwords do not match."
        )

    # ------------------------------------------------------
    # Prevent same password
    # ------------------------------------------------------

    if user.check_password(new_password):

        raise ValidationError(
            "New password must be different "
            "from the current password."
        )

    # ------------------------------------------------------
    # Save password
    # ------------------------------------------------------

    user.set_password(new_password)

    user.save(
        update_fields=[
            "password",
        ]
    )

    return user