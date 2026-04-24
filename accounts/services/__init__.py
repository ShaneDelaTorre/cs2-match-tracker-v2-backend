from django.db.models import Q
from accounts.models import FriendRequest, User

def send_friend_request(sender: User, receiver: User) -> FriendRequest:
    if sender == receiver:
        raise ValueError("You cannot send a friend request to yourself.")

    already_exists = FriendRequest.objects.filter(
        Q(sender=sender, receiver=receiver) |
        Q(sender=receiver, receiver=sender)
    ).exists()

    if already_exists:
        raise ValueError("A friend request already exists between these users.")

    return FriendRequest.objects.create(sender=sender, receiver=receiver)


def respond_to_friend_request(request: FriendRequest, accepting: bool) -> FriendRequest:
    if request.status != FriendRequest.Status.PENDING:
        raise ValueError("This request has already been responded to.")

    request.status = (
        FriendRequest.Status.ACCEPTED if accepting
        else FriendRequest.Status.REJECTED
    )
    request.save()
    return request


def are_friends(user_a: User, user_b: User) -> bool:
    return FriendRequest.objects.filter(
        Q(sender=user_a, receiver=user_b) |
        Q(sender=user_b, receiver=user_a),
        status=FriendRequest.Status.ACCEPTED,
    ).exists()