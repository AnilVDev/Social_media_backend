from django.urls import path, include
from . import views
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("signup/", views.register_user, name="register"),
    path("userlist/", views.userlist, name="userlist"),
    path("profile/", UserDetailsView.as_view(), name="user_details"),
    path("update/", CustomUserUpdateView.as_view(), name="custom-user-update"),
    path("update-status/", UserUpdateStatusView.as_view(), name="update-status"),
    path("authenticate/", AuthenticationView.as_view(), name="authenticate"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
