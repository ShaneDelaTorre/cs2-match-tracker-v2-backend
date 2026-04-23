from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    class RankChoices(models.TextChoices):
        UNRANKED = "Unranked"
        SILVER = "Below 5000"
        LIGHT_BLUE = "5000-9999"
        DARK_BLUE = "10000-14999"
        LIGHT_PURPLE = "15000-19999"
        DARK_PURPLE = "20000-24999"
        RED = "25000-29999"
        GOLD = "30000+"

    email = models.EmailField(unique=True)
    rank = models.CharField(max_length=30, choices=RankChoices.choices, default=RankChoices.UNRANKED)
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")

    def __str__(self):
        return f"User: {self.username} | Rank: {self.rank}"

class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        REJECTED = "rejected"

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    reciever = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recieved_requests")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("sender", "reciever")