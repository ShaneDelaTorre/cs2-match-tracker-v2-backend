import factory
import random
from factory.django import DjangoModelFactory
from faker import Faker
from django.utils import timezone
from accounts.factories import UserFactory
from matches.models import Map, Match, RoundEvent, MatchStat

fake = Faker()

CS2_MAPS = [
    "Mirage", "Dust2", "Inferno", "Nuke", "Overpass",
    "Anubis", "Ancient", "Vertigo", "Train", "Cache",
]

class MapFactory(DjangoModelFactory):
    class Meta:
        model = Map
        django_get_or_create = ("name",)

    name = factory.Iterator(CS2_MAPS)
    image_url = ""

class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    user = factory.SubFactory(UserFactory)
    map = factory.SubFactory(MapFactory)
    game_mode = factory.Iterator(Match.GameMode.values)
    result = factory.Iterator(Match.Result.values)
    team_score = factory.LazyFunction(lambda: random.randint(0, 16))
    opponent_score = factory.LazyFunction(lambda: random.randint(0, 16))
    duration = factory.LazyFunction(lambda: random.randint(20, 60))
    played_at = factory.LazyFunction(timezone.now)

class RoundEventFactory(DjangoModelFactory):
    class Meta:
        model = RoundEvent

    match = factory.SubFactory(MatchFactory)
    round_number = factory.Sequence(lambda n: n + 1)
    round_result = factory.Iterator(RoundEvent.RoundResult.values)
    kills = factory.LazyFunction(lambda: random.randint(0, 5))
    headshots = factory.LazyAttribute(lambda o: random.randint(0, o.kills))
    survived = factory.LazyFunction(lambda: random.choice([True, False]))
    mvp = factory.LazyFunction(lambda: random.choice([True, False]))

class MatchStatFactory(DjangoModelFactory):
    class Meta:
        model = MatchStat

    match = factory.SubFactory(MatchFactory)
    kills = factory.LazyFunction(lambda: random.randint(0, 30))
    deaths = factory.LazyFunction(lambda: random.randint(0, 30))
    assists = factory.LazyFunction(lambda: random.randint(0, 15))
    headshots = factory.LazyAttribute(lambda o: random.randint(0, o.kills))
    mvp_rounds = factory.LazyFunction(lambda: random.randint(0, 10))
    score = factory.LazyFunction(lambda: random.randint(0, 100))