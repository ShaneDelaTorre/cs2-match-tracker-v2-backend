import factory
from factory.django import DjangoModelFactory
from faker import Faker
from accounts.models import User, FriendRequest

fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    rank = factory.Iterator(User.RankChoices.values)
    bio = factory.LazyFunction(fake.sentence)
    avatar_url = ""

class FriendRequestFactory(DjangoModelFactory):
    class Meta:
        model = FriendRequest

    sender = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    status = FriendRequest.Status.PENDING