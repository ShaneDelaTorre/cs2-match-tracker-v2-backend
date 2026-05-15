from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, GoogleLoginView, GoogleCallbackView, MicrosoftLoginView, MicrosoftCallbackView, LogoutView

urlpatterns = [
    path("jwt/create/", CookieTokenObtainPairView.as_view()),
    path("jwt/refresh/", CookieTokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("google/login/", GoogleLoginView.as_view()),
    path("google/callback/", GoogleCallbackView.as_view()),
    path("microsoft/login/",MicrosoftLoginView.as_view()),
    path("microsoft/callback/", MicrosoftCallbackView.as_view()),
]