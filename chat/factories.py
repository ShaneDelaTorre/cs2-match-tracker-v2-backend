import factory
from factory.django import DjangoModelFactory
from faker import Faker
from chat.models import ChatMessages
from accounts.factories import UserFactory

fake = Faker()

class ChatMessageFactory(DjangoModelFactory):
    class Meta:
        model = ChatMessages

    sender = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    body = factory.LazyFunction(fake.sentence)
    is_read = factory.LazyFunction(lambda: False)