from django.db.models import Q, Count, Avg, FloatField
from accounts.models import FriendRequest, User
from matches.models import Match, MatchStat

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

def get_career_summary(user) -> dict:
    base_qs = Match.objects.filter(user=user)

    totals = base_qs.aggregate(
        total=Count("id"),
        wins=Count("id", filter=Q(result=Match.Result.WIN)),
        losses=Count("id", filter=Q(result=Match.Result.LOSS)),
        draws=Count("id", filter=Q(result=Match.Result.DRAW)),
    )

    total = totals["total"] or 1  # avoid division by zero
    win_rate = round((totals["wins"] / total) * 100, 2)

    stat_averages = MatchStat.objects.filter(match__user=user).aggregate(
        avg_kills=Avg("kills"),
        avg_deaths=Avg("deaths"),
        avg_headshots=Avg("headshots"),
        avg_kills_f=Avg("kills", output_field=FloatField()),
        avg_deaths_f=Avg("deaths", output_field=FloatField()),
    )

    avg_kd = round(
        (stat_averages["avg_kills"] or 0) /
        max(stat_averages["avg_deaths"] or 1, 1),
        2
    )

    avg_hs_pct = round(
        (stat_averages["avg_headshots"] or 0) /
        max(stat_averages["avg_kills"] or 1, 1) * 100,
        2
    )

    # Win rate per map
    per_map = (
        base_qs
        .values("map__name")
        .annotate(
            played=Count("id"),
            won=Count("id", filter=Q(result=Match.Result.WIN)),
        )
        .order_by("-played")
    )

    map_stats = [
        {
            "map": entry["map__name"],
            "played": entry["played"],
            "won": entry["won"],
            "win_rate": round((entry["won"] / entry["played"]) * 100, 2),
        }
        for entry in per_map
    ]

    # Best map — minimum 5 matches, highest win rate
    best_map = max(
        (m for m in map_stats if m["played"] >= 5),
        key=lambda m: m["win_rate"],
        default=None,
    )

    # Current form — last 5 results
    last_5 = list(
        base_qs.order_by("-played_at").values_list("result", flat=True)[:5]
    )

    return {
        "total_matches": totals["total"],
        "wins": totals["wins"],
        "losses": totals["losses"],
        "draws": totals["draws"],
        "win_rate": win_rate,
        "avg_kd": avg_kd,
        "avg_headshot_pct": avg_hs_pct,
        "map_stats": map_stats,
        "best_map": best_map,
        "current_form": last_5,
    }