from http.cookies import SimpleCookie
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = AccessToken(token_key)
        user_id = token["user_id"]
        return User.objects.get(id=user_id)
    except(InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send, *args, **kwds):
        if scope["type"] == "websocket":
            headers = dict(scope["headers"])
            raw_cookies = headers.get(b"cookie", b"").decode()
            cookie = SimpleCookie()
            cookie.load(raw_cookies)
            token_key = cookie.get("access_token")
            if token_key:
                scope["user"] = await get_user_from_token(token_key.value)
            else:
                scope["user"] = AnonymousUser()
        
        await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
