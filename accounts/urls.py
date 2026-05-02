from django.urls import path
from accounts.views import (
    OwnProfileView,
    PublicProfileView,
    AccountSearchView,
    FriendRequestListCreateView,
    FriendRequestRespondView,
    FriendsListView,
)

urlpatterns = [
    path("me/", OwnProfileView.as_view(), name="own-profile"),
    path("users/<int:pk>/", PublicProfileView.as_view(), name="public-profile"),
    path("users/username/", AccountSearchView.as_view(), name="search-user-by-username"),
    path("friend-requests/", FriendRequestListCreateView.as_view(), name="friend-requests"),
    path("friend-requests/<int:pk>/respond/", FriendRequestRespondView.as_view(), name="friend-request-respond"),
    path("friends/", FriendsListView.as_view(), name="user-friends")
]