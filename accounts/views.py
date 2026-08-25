from django.contrib.auth import login, logout
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsAdminOrManager
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


# ==========================================================
# LOGIN
# ==========================================================

class LoginView(APIView):
    """
    Login using username and password.

    Authentication:
        SessionAuthentication

    Login is available to everyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        login(request, user)

        return Response(
            {
                "message": "Login successful.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# LOGOUT
# ==========================================================

class LogoutView(APIView):
    """
    Logout the currently authenticated user.
    """

    def post(self, request):
        logout(request)

        return Response(
            {
                "message": "Logout successful."
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CURRENT USER
# ==========================================================

class MeView(APIView):
    """
    Return the currently authenticated user.
    """

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# USER LIST
# ==========================================================

class UserListView(APIView):
    """
    List application users.

    ADMIN:
        Can see all users.

    MANAGER:
        Can see MANAGER and STAFF users.

    STAFF:
        No access.
    """

    permission_classes = [IsAdminOrManager]

    def get(self, request):

        queryset = User.objects.all().order_by(
            "-date_joined"
        )

        # --------------------------------------------------
        # MANAGER CANNOT SEE ADMIN USERS
        # --------------------------------------------------

        if request.user.role == User.Role.MANAGER:
            queryset = queryset.exclude(
                role=User.Role.ADMIN
            )

        # --------------------------------------------------
        # SEARCH
        # --------------------------------------------------

        search = request.query_params.get(
            "search"
        )

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        # --------------------------------------------------
        # ROLE FILTER
        # --------------------------------------------------

        role = request.query_params.get("role")

        if role in User.Role.values:

            # Manager still cannot access ADMIN.
            if (
                request.user.role == User.Role.MANAGER
                and role == User.Role.ADMIN
            ):
                return Response(
                    {
                        "detail": (
                            "Manager cannot view Admin users."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            queryset = queryset.filter(
                role=role
            )

        # --------------------------------------------------
        # ACTIVE FILTER
        # --------------------------------------------------

        is_active = request.query_params.get(
            "is_active"
        )

        if is_active in ["true", "false"]:
            queryset = queryset.filter(
                is_active=is_active == "true"
            )

        serializer = UserSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CREATE USER
# ==========================================================

class UserCreateView(APIView):
    """
    Create a new application user.

    ADMIN:
        Can create ADMIN, MANAGER and STAFF.

    MANAGER:
        Can create MANAGER and STAFF.

    STAFF:
        No access.
    """

    permission_classes = [IsAdminOrManager]

    def post(self, request):

        serializer = UserCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            {
                "message": "User created successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# USER DETAIL
# ==========================================================

class UserDetailView(APIView):
    """
    Retrieve, update or deactivate a user.

    ADMIN:
        Full access.

    MANAGER:
        Can manage MANAGER and STAFF.

    STAFF:
        No access.
    """

    permission_classes = [IsAdminOrManager]

    def get_object(self, pk):

        try:
            return User.objects.get(pk=pk)

        except User.DoesNotExist:
            return None

    def get(self, request, pk):

        user = self.get_object(pk)

        if not user:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Manager cannot see Admin.
        if (
            request.user.role == User.Role.MANAGER
            and user.role == User.Role.ADMIN
        ):
            return Response(
                {
                    "detail": (
                        "Manager cannot access Admin users."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):

        user = self.get_object(pk)

        if not user:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Manager cannot modify Admin.
        if (
            request.user.role == User.Role.MANAGER
            and user.role == User.Role.ADMIN
        ):
            return Response(
                {
                    "detail": (
                        "Manager cannot modify Admin users."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            {
                "message": "User updated successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ChangePasswordView(APIView):
    """
    Change password for the currently authenticated user.
    """

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save(
            update_fields=["password"]
        )

        # Keep current session alive.
        login(request, user)

        return Response(
            {
                "message": (
                    "Password changed successfully."
                )
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ACTIVATE USER
# ==========================================================

class ActivateUserView(APIView):
    """
    Activate a user.

    ADMIN:
        Can activate anyone.

    MANAGER:
        Can activate MANAGER and STAFF.

    STAFF:
        No access.
    """

    permission_classes = [IsAdminOrManager]

    def post(self, request, pk):

        try:
            user = User.objects.get(pk=pk)

        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Manager cannot activate Admin.
        if (
            request.user.role == User.Role.MANAGER
            and user.role == User.Role.ADMIN
        ):
            return Response(
                {
                    "detail": (
                        "Manager cannot activate Admin users."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.is_active = True

        user.save(
            update_fields=["is_active"]
        )

        return Response(
            {
                "message": "User activated successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# DEACTIVATE USER
# ==========================================================

class DeactivateUserView(APIView):
    """
    Deactivate a user.

    A user cannot deactivate themselves.
    """

    permission_classes = [IsAdminOrManager]

    def post(self, request, pk):

        try:
            user = User.objects.get(pk=pk)

        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # --------------------------------------------------
        # CANNOT DEACTIVATE YOURSELF
        # --------------------------------------------------

        if user.pk == request.user.pk:
            return Response(
                {
                    "detail": (
                        "You cannot deactivate yourself."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # MANAGER CANNOT DEACTIVATE ADMIN
        # --------------------------------------------------

        if (
            request.user.role == User.Role.MANAGER
            and user.role == User.Role.ADMIN
        ):
            return Response(
                {
                    "detail": (
                        "Manager cannot deactivate "
                        "Admin users."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        user.is_active = False

        user.save(
            update_fields=["is_active"]
        )

        return Response(
            {
                "message": (
                    "User deactivated successfully."
                ),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )