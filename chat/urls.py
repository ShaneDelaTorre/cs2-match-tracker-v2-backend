from django.urls import path
from .views import ChatHistory

urlpatterns = [
    path("<int:recepient_id>/", ChatHistory.as_view(), name="chat-history"),
]