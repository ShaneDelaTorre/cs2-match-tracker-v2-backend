from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView

urlpatterns = [
    path("jwt/create/", CookieTokenObtainPairView.as_view()),
    path("jwt/refresh/", CookieTokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
]