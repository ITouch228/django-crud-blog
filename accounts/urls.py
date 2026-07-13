from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts.views import login_view, register_view

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
