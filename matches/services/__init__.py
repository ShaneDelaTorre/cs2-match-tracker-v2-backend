from django.db import transaction
from django.db.models import Sum, Count, Q
from matches.models import Match, RoundEvent, MatchStat, Map

def create_match(user, validated_data: dict) -> Match:
    rounds_data = validated_data.pop("rounds")
    score = validated_data.pop("score", 0)
    assists = validated_data.pop("assists", 0)

    # Validate headshots <= kills per round
    for i, round_data in enumerate(rounds_data):
        if round_data["headshots"] > round_data["kills"]:
            raise ValueError(
                f"Round {i + 1}: headshots cannot exceed kills."
            )

    # Derive scores and result from rounds
    team_score = sum(1 for r in rounds_data if r["round_result"] == RoundEvent.RoundResult.WIN)
    opponent_score = sum(1 for r in rounds_data if r["round_result"] == RoundEvent.RoundResult.LOSS)

    if team_score > opponent_score:
        result = Match.Result.WIN
    elif team_score < opponent_score:
        result = Match.Result.LOSS
    else:
        result = Match.Result.DRAW

    with transaction.atomic():
        match = Match.objects.create(
            user=user,
            team_score=team_score,
            opponent_score=opponent_score,
            result=result,
            **validated_data,
        )

        # Append-only round events — never updated after this point
        RoundEvent.objects.bulk_create([
            RoundEvent(match=match, **round_data)
            for round_data in rounds_data
        ])

        # Aggregate rounds to derive MatchStat
        aggregated = RoundEvent.objects.filter(match=match).aggregate(
            total_kills=Sum("kills"),
            total_headshots=Sum("headshots"),
            total_deaths=Count("id", filter=Q(survived=False)),
            total_mvps=Count("id", filter=Q(mvp=True)),
        )

        MatchStat.objects.create(
            match=match,
            kills=aggregated["total_kills"] or 0,
            deaths=aggregated["total_deaths"] or 0,
            assists=assists,
            headshots=aggregated["total_headshots"] or 0,
            mvp_rounds=aggregated["total_mvps"] or 0,
            score=score
        )

    return match


def get_match_state_at_round(match: Match, round_n: int) -> dict:
    return RoundEvent.objects.filter(
        match=match,
        round_number__lte=round_n,
    ).aggregate(
        team_score=Count("id", filter=Q(round_result=RoundEvent.RoundResult.WIN)),
        opponent_score=Count("id", filter=Q(round_result=RoundEvent.RoundResult.LOSS)),
        kills=Sum("kills"),
        headshots=Sum("headshots"),
        deaths=Count("id", filter=Q(survived=False)),
        mvps=Count("id", filter=Q(mvp=True)),
    )