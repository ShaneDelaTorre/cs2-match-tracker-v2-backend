from chat.models import ChatMessages
from accounts.models import User
from accounts.services import are_friends

def send_message(sender: User, receiver: User, body: str) -> ChatMessages:
    if not are_friends(sender, receiver):
        raise ValueError("Users must be friends before they can chat.")

    return ChatMessages.objects.create(
        sender=sender,
        receiver=receiver,
        body=body,
    )


def get_conversation(user_a: User, user_b: User):
    from django.db.models import Q
    return ChatMessages.objects.filter(
        Q(sender=user_a, receiver=user_b) |
        Q(sender=user_b, receiver=user_a)
    ).order_by("sent_at")