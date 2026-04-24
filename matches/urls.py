from django.urls import path
from matches.views import (
    MapListView,
    MatchListCreateView,
    MatchDetailView,
    MatchStateAtRoundView,
)

urlpatterns = [
    path("maps/", MapListView.as_view(), name="map-list"),
    path("", MatchListCreateView.as_view(), name="match-list-create"),
    path("<int:pk>/", MatchDetailView.as_view(), name="match-detail"),
    path("<int:pk>/state/<int:round_n>/", MatchStateAtRoundView.as_view(), name="match-state-at-round"),
]