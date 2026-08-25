from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


# ==========================================================
# USER SERIALIZER
# ==========================================================

class UserSerializer(serializers.ModelSerializer):
    """
    General user representation.

    Used when returning user information.
    Password is never exposed.
    """

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "date_joined",
        ]

        read_only_fields = [
            "id",
            "date_joined",
        ]


# ==========================================================
# CREATE USER
# ==========================================================

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Admin creates a new application user.

    Rules:

    ADMIN:
        Can create ADMIN, MANAGER and STAFF.

    MANAGER:
        Can create MANAGER and STAFF.

    STAFF:
        Cannot create users.

    Password is write-only.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "password",
            "password_confirm",
            "is_active",
        ]

        extra_kwargs = {
            "is_active": {
                "required": False,
            },
        }

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise serializers.ValidationError(
                {
                    "password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authenticated user is required."
            )

        current_user = request.user
        requested_role = attrs.get(
            "role",
            User.Role.STAFF,
        )

        # --------------------------------------------------
        # STAFF CANNOT CREATE USERS
        # --------------------------------------------------

        if current_user.role == User.Role.STAFF:
            raise serializers.ValidationError(
                "Staff users cannot create users."
            )

        # --------------------------------------------------
        # MANAGER CANNOT CREATE ADMIN
        # --------------------------------------------------

        if (
            current_user.role == User.Role.MANAGER
            and requested_role == User.Role.ADMIN
        ):
            raise serializers.ValidationError(
                "Manager cannot create an Admin user."
            )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


# ==========================================================
# UPDATE USER
# ==========================================================

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Update an existing user.

    Password is intentionally not handled here.

    Password changes should use a dedicated password
    endpoint/serializer.
    """

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authenticated user is required."
            )

        current_user = request.user
        target_user = self.instance

        requested_role = attrs.get(
            "role",
            target_user.role,
        )

        requested_active = attrs.get(
            "is_active",
            target_user.is_active,
        )

        # --------------------------------------------------
        # USER CANNOT MODIFY THEIR OWN ROLE
        # --------------------------------------------------

        if (
            target_user.pk == current_user.pk
            and "role" in attrs
            and requested_role != current_user.role
        ):
            raise serializers.ValidationError(
                {
                    "role": (
                        "You cannot change your own role."
                    )
                }
            )

        # --------------------------------------------------
        # USER CANNOT DEACTIVATE THEMSELVES
        # --------------------------------------------------

        if (
            target_user.pk == current_user.pk
            and "is_active" in attrs
            and requested_active is False
        ):
            raise serializers.ValidationError(
                {
                    "is_active": (
                        "You cannot deactivate yourself."
                    )
                }
            )

        # --------------------------------------------------
        # STAFF CANNOT UPDATE USERS
        # --------------------------------------------------

        if current_user.role == User.Role.STAFF:
            raise serializers.ValidationError(
                "Staff users cannot update users."
            )

        # --------------------------------------------------
        # MANAGER CANNOT CREATE/PROMOTE TO ADMIN
        # --------------------------------------------------

        if (
            current_user.role == User.Role.MANAGER
            and requested_role == User.Role.ADMIN
        ):
            raise serializers.ValidationError(
                "Manager cannot assign the Admin role."
            )

        # --------------------------------------------------
        # MANAGER CANNOT MODIFY ADMIN
        # --------------------------------------------------

        if (
            current_user.role == User.Role.MANAGER
            and target_user.role == User.Role.ADMIN
        ):
            raise serializers.ValidationError(
                "Manager cannot modify an Admin user."
            )

        return attrs


# ==========================================================
# PASSWORD CHANGE
# ==========================================================

class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password for the currently authenticated user.
    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        user = self.context["request"].user

        # --------------------------------------------------
        # CHECK OLD PASSWORD
        # --------------------------------------------------

        if not user.check_password(
            attrs["old_password"]
        ):
            raise serializers.ValidationError(
                {
                    "old_password": (
                        "Current password is incorrect."
                    )
                }
            )

        # --------------------------------------------------
        # CHECK NEW PASSWORD MATCH
        # --------------------------------------------------

        if (
            attrs["new_password"]
            != attrs["new_password_confirm"]
        ):
            raise serializers.ValidationError(
                {
                    "new_password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        # --------------------------------------------------
        # NEW PASSWORD CANNOT BE SAME
        # --------------------------------------------------

        if user.check_password(
            attrs["new_password"]
        ):
            raise serializers.ValidationError(
                {
                    "new_password": (
                        "New password must be different "
                        "from your current password."
                    )
                }
            )

        return attrs


# ==========================================================
# LOGIN
# ==========================================================

class LoginSerializer(serializers.Serializer):
    """
    Username/password authentication serializer.
    """

    username = serializers.CharField(
        required=True
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This user account is inactive."
            )

        attrs["user"] = user

        return attrs