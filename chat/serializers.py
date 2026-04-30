from rest_framework import serializers
from chat.models import ChatMessages
from accounts.serializers import PublicUserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)
    receiver = PublicUserSerializer(read_only=True)
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('accounts.models', fromlist=['User']).User.objects.all(),
        source="receiver",
        write_only=True,
    )

    class Meta:
        model = ChatMessages
        fields = ["id", "sender", "receiver", "receiver_id", "body", "is_read", "sent_at"]
        read_only_fields = ["id", "sender", "is_read", "sent_at"]