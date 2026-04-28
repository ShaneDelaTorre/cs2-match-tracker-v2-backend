from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView

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
    

class LogoutView(APIView):
    def post(self, request):
        response = Response({"success": True})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response