import pytest
from accounts.factories import UserFactory, FriendRequestFactory
from accounts.models import FriendRequest
from accounts.services import send_friend_request, respond_to_friend_request, are_friends


@pytest.fixture
def user_a():
    return UserFactory()


@pytest.fixture
def user_b():
    return UserFactory()


@pytest.mark.django_db
class TestFriendRequest:
    def test_send_friend_request(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        assert fr.status == FriendRequest.Status.PENDING
        assert fr.sender == user_a
        assert fr.receiver == user_b

    def test_cannot_send_to_self(self, user_a):
        with pytest.raises(ValueError, match="yourself"):
            send_friend_request(user_a, user_a)

    def test_cannot_send_duplicate(self, user_a, user_b):
        send_friend_request(user_a, user_b)
        with pytest.raises(ValueError, match="already exists"):
            send_friend_request(user_a, user_b)

    def test_cannot_send_reverse_duplicate(self, user_a, user_b):
        send_friend_request(user_a, user_b)
        with pytest.raises(ValueError, match="already exists"):
            send_friend_request(user_b, user_a)

    def test_accept_friend_request(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        fr = respond_to_friend_request(fr, accepting=True)
        assert fr.status == FriendRequest.Status.ACCEPTED

    def test_reject_friend_request(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        fr = respond_to_friend_request(fr, accepting=False)
        assert fr.status == FriendRequest.Status.REJECTED

    def test_cannot_respond_twice(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        respond_to_friend_request(fr, accepting=True)
        with pytest.raises(ValueError, match="already been responded"):
            respond_to_friend_request(fr, accepting=False)


@pytest.mark.django_db
class TestAreFriends:
    def test_are_friends_after_accept(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        respond_to_friend_request(fr, accepting=True)
        assert are_friends(user_a, user_b) is True

    def test_are_friends_bidirectional(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        respond_to_friend_request(fr, accepting=True)
        assert are_friends(user_b, user_a) is True

    def test_not_friends_if_pending(self, user_a, user_b):
        send_friend_request(user_a, user_b)
        assert are_friends(user_a, user_b) is False

    def test_not_friends_if_rejected(self, user_a, user_b):
        fr = send_friend_request(user_a, user_b)
        respond_to_friend_request(fr, accepting=False)
        assert are_friends(user_a, user_b) is False