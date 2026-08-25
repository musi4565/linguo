from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RefreshLoginView,
    RegisterView,
    TelegramConnectUrlView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshLoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("telegram/connect-url/", TelegramConnectUrlView.as_view()),
]
