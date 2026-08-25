from django.urls import path

from .views import (
    ActivateUserView,
    ChangePasswordView,
    DeactivateUserView,
    LoginView,
    LogoutView,
    MeView,
    UserCreateView,
    UserDetailView,
    UserListView,
)


urlpatterns = [
    # Authentication
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),

    # User management
    path(
        "users/",
        UserListView.as_view(),
        name="user-list",
    ),

    path(
        "users/create/",
        UserCreateView.as_view(),
        name="user-create",
    ),

    path(
        "users/<int:pk>/",
        UserDetailView.as_view(),
        name="user-detail",
    ),

    path(
        "users/<int:pk>/activate/",
        ActivateUserView.as_view(),
        name="user-activate",
    ),

    path(
        "users/<int:pk>/deactivate/",
        DeactivateUserView.as_view(),
        name="user-deactivate",
    ),
]