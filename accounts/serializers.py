from rest_framework import serializers
from accounts.models import User, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "rank", "bio", "avatar_url"]
        read_only_fields = ["id"]


class PublicUserSerializer(serializers.ModelSerializer):
    """Used when viewing another user's profile — no email exposed."""
    class Meta:
        model = User
        fields = ["id", "username", "rank", "bio", "avatar_url"]
        read_only_fields = ["id"]


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)
    receiver = PublicUserSerializer(read_only=True)
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="receiver",
        write_only=True,
    )

    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "receiver_id", "status", "created_at"]
        read_only_fields = ["id", "sender", "status", "created_at"]