import pytest
from accounts.factories import UserFactory
from accounts.models import FriendRequest
from accounts.services import send_friend_request, respond_to_friend_request
from chat.services import send_message, get_conversation


@pytest.fixture
def user_a():
    return UserFactory()


@pytest.fixture
def user_b():
    return UserFactory()


@pytest.fixture
def friends(user_a, user_b):
    fr = send_friend_request(user_a, user_b)
    respond_to_friend_request(fr, accepting=True)
    return user_a, user_b


@pytest.mark.django_db
class TestSendMessage:
    def test_send_message_between_friends(self, friends):
        user_a, user_b = friends
        msg = send_message(user_a, user_b, "hello")
        assert msg.sender == user_a
        assert msg.receiver == user_b
        assert msg.body == "hello"

    def test_cannot_send_message_if_not_friends(self, user_a, user_b):
        with pytest.raises(ValueError, match="must be friends"):
            send_message(user_a, user_b, "hello")

    def test_cannot_send_message_if_pending(self, user_a, user_b):
        send_friend_request(user_a, user_b)
        with pytest.raises(ValueError, match="must be friends"):
            send_message(user_a, user_b, "hello")


@pytest.mark.django_db
class TestGetConversation:
    def test_returns_messages_in_order(self, friends):
        user_a, user_b = friends
        send_message(user_a, user_b, "first")
        send_message(user_b, user_a, "second")
        send_message(user_a, user_b, "third")
        messages = list(get_conversation(user_a, user_b))
        assert len(messages) == 3
        assert messages[0].body == "first"
        assert messages[1].body == "second"
        assert messages[2].body == "third"

    def test_only_returns_messages_between_these_two_users(self, friends):
        user_a, user_b = friends
        user_c = UserFactory()
        fr = send_friend_request(user_a, user_c)
        respond_to_friend_request(fr, accepting=True)
        send_message(user_a, user_b, "to b")
        send_message(user_a, user_c, "to c")
        messages = list(get_conversation(user_a, user_b))
        assert len(messages) == 1
        assert messages[0].body == "to b"

    def test_conversation_is_bidirectional(self, friends):
        user_a, user_b = friends
        send_message(user_a, user_b, "from a")
        send_message(user_b, user_a, "from b")
        messages = list(get_conversation(user_a, user_b))
        assert len(messages) == 2