from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.conf import settings
from authlib.integrations.django_client import OAuth
from datetime import datetime

User = get_user_model()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        res = Response({"success": True})

        res.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=False,  # True in production
            samesite="Lax",
            path="/",
        )

        res.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )

        return res
    

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh_token")

        if not refresh:
            return Response({"detail": "No refresh token"}, status=401)

        request.data["refresh"] = refresh

        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")

        res = Response({"success": True})

        res.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )

        return res
    
class GoogleLoginView(APIView):
    permission_classes = []

    def get(self, request):
        redirect_uri = "http://localhost:8000/auth/google/callback/"
        return oauth.google.authorize_redirect(request, redirect_uri)

class GoogleCallbackView(APIView):
    permission_classes = []

    def get(self, request):
        token = oauth.google.authorize_access_token(request)
        claims = token.get("userinfo")

        google_id = claims["sub"]
        email = claims.get("email", "")

        print(token)

        try:
            user = User.objects.get(google_id=google_id)
            is_new = False
        except User.DoesNotExist:
            base_username = email.split("@")[0]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            username = f"{base_username}_{timestamp}"

            user = User.objects.create(
                username=username,
                email=email,
                google_id=google_id
            )
            is_new = True

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        frontend_url = "http://localhost:3000"
        redirect_url = f"{frontend_url}/profile/setup/" if is_new else f"{frontend_url}/dashboard/"
        response = redirect(redirect_url)

        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/"
        )

        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/" 
        )

        return response



class LogoutView(APIView):
    def post(self, request):
        response = Response({"success": True})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response