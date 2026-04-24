import pytest
from django.utils import timezone
from matches.models import Match, RoundEvent, MatchStat
from matches.services import create_match, get_match_state_at_round
from matches.factories import MapFactory, MatchFactory, RoundEventFactory
from accounts.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def map():
    return MapFactory(name="Mirage")


def make_rounds(results):
    """Helper — build a list of round dicts from a list of 'Win'/'Loss' strings."""
    return [
        {
            "round_number": i + 1,
            "round_result": result,
            "kills": 2,
            "headshots": 1,
            "survived": True,
            "mvp": False,
        }
        for i, result in enumerate(results)
    ]


@pytest.mark.django_db
class TestCreateMatch:
    def test_result_derived_as_win(self, user, map):
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 30,
            "played_at": timezone.now(),
            "score": 40,
            "rounds": make_rounds(["Win", "Win", "Win", "Loss", "Loss"]),
        }
        match = create_match(user=user, validated_data=data)
        assert match.result == Match.Result.WIN
        assert match.team_score == 3
        assert match.opponent_score == 2

    def test_result_derived_as_loss(self, user, map):
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 30,
            "played_at": timezone.now(),
            "score": 20,
            "rounds": make_rounds(["Loss", "Loss", "Loss", "Win", "Win"]),
        }
        match = create_match(user=user, validated_data=data)
        assert match.result == Match.Result.LOSS
        assert match.team_score == 2
        assert match.opponent_score == 3

    def test_result_derived_as_draw(self, user, map):
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 30,
            "played_at": timezone.now(),
            "score": 30,
            "rounds": make_rounds(["Win", "Win", "Loss", "Loss"]),
        }
        match = create_match(user=user, validated_data=data)
        assert match.result == Match.Result.DRAW

    def test_round_events_created(self, user, map):
        rounds = make_rounds(["Win", "Loss", "Win"])
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 25,
            "played_at": timezone.now(),
            "score": 30,
            "rounds": rounds,
        }
        match = create_match(user=user, validated_data=data)
        assert RoundEvent.objects.filter(match=match).count() == 3

    def test_match_stat_derived_from_rounds(self, user, map):
        rounds = [
            {
                "round_number": 1,
                "round_result": "Win",
                "kills": 3,
                "headshots": 2,
                "survived": True,
                "mvp": True,
            },
            {
                "round_number": 2,
                "round_result": "Loss",
                "kills": 1,
                "headshots": 0,
                "survived": False,
                "mvp": False,
            },
        ]
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 25,
            "played_at": timezone.now(),
            "score": 30,
            "rounds": rounds,
        }
        match = create_match(user=user, validated_data=data)
        stat = match.stat
        assert stat.kills == 4
        assert stat.headshots == 2
        assert stat.deaths == 1
        assert stat.mvp_rounds == 1

    def test_rejects_headshots_exceeding_kills(self, user, map):
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 25,
            "played_at": timezone.now(),
            "score": 30,
            "rounds": [
                {
                    "round_number": 1,
                    "round_result": "Win",
                    "kills": 1,
                    "headshots": 3,  # invalid
                    "survived": True,
                    "mvp": False,
                }
            ],
        }
        with pytest.raises(ValueError, match="headshots cannot exceed kills"):
            create_match(user=user, validated_data=data)

    def test_no_partial_data_on_failure(self, user, map):
        """If service raises, no Match or RoundEvent rows should exist."""
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 25,
            "played_at": timezone.now(),
            "score": 30,
            "rounds": [
                {
                    "round_number": 1,
                    "round_result": "Win",
                    "kills": 1,
                    "headshots": 5,  # invalid
                    "survived": True,
                    "mvp": False,
                }
            ],
        }
        with pytest.raises(ValueError):
            create_match(user=user, validated_data=data)

        assert Match.objects.count() == 0
        assert RoundEvent.objects.count() == 0


@pytest.mark.django_db
class TestMatchStateAtRound:
    def test_state_at_round_n(self, user, map):
        rounds = [
            {
                "round_number": 1,
                "round_result": "Win",
                "kills": 3,
                "headshots": 1,
                "survived": True,
                "mvp": True,
            },
            {
                "round_number": 2,
                "round_result": "Loss",
                "kills": 2,
                "headshots": 1,
                "survived": False,
                "mvp": False,
            },
            {
                "round_number": 3,
                "round_result": "Win",
                "kills": 4,
                "headshots": 2,
                "survived": True,
                "mvp": False,
            },
        ]
        data = {
            "map": map,
            "game_mode": Match.GameMode.PREMIER,
            "duration": 30,
            "played_at": timezone.now(),
            "score": 40,
            "rounds": rounds,
        }
        match = create_match(user=user, validated_data=data)

        state = get_match_state_at_round(match, round_n=2)
        assert state["team_score"] == 1
        assert state["opponent_score"] == 1
        assert state["kills"] == 5
        assert state["headshots"] == 2
        assert state["deaths"] == 1