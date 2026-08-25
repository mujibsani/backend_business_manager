from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    General user representation.

    Used for displaying users.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "date_joined",
        )

        read_only_fields = (
            "id",
            "date_joined",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Create a new Business Manager user.

    Password is write-only and is properly hashed
    through Django's set_password().
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "role",
        )

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username is required."
            )

        if User.objects.filter(
            username__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate_role(self, value):
        if value not in User.Role.values:
            raise serializers.ValidationError(
                "Invalid user role."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Update an existing user.

    Password is intentionally excluded.
    Role changes will be handled separately.
    """

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "is_active",
        )


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Change a user's Business Manager role.
    """

    class Meta:
        model = User
        fields = (
            "role",
        )

    def validate_role(self, value):
        if value not in User.Role.values:
            raise serializers.ValidationError(
                "Invalid user role."
            )

        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change a user's password.
    """

    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password":
                        "Passwords do not match."
                }
            )

        return attrs