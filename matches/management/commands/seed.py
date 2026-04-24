import random
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.factories import UserFactory, FriendRequestFactory
from matches.factories import MapFactory, MatchFactory, RoundEventFactory, MatchStatFactory
from chat.factories import ChatMessageFactory
from accounts.models import FriendRequest
from matches.models import Match

CS2_MAPS = [
    "Mirage", "Dust2", "Inferno", "Nuke", "Overpass",
    "Anubis", "Ancient", "Vertigo", "Train", "Cache",
]

class Command(BaseCommand):
    help = "Seed the database with realistic fake data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=10,
            help="Number of users to create (default: 10)"
        )
        parser.add_argument(
            "--matches", type=int, default=20,
            help="Number of matches per user (default: 20)"
        )
        parser.add_argument(
            "--rounds", type=int, default=24,
            help="Number of rounds per match (default: 24)"
        )

    def handle(self, *args, **options):
        user_count = options["users"]
        matches_per_user = options["matches"]
        rounds_per_match = options["rounds"]

        self.stdout.write("Seeding database...")

        with transaction.atomic():
            # Maps
            self.stdout.write("  Creating maps...")
            maps = [MapFactory(name=name) for name in CS2_MAPS]

            # Users
            self.stdout.write(f"  Creating {user_count} users...")
            users = UserFactory.create_batch(user_count)

            # Friend requests between random user pairs
            self.stdout.write("  Creating friendships...")
            for i, user in enumerate(users):
                potential_friends = [u for u in users if u != user]
                targets = random.sample(potential_friends, k=min(3, len(potential_friends)))
                for target in targets:
                    already_exists = FriendRequest.objects.filter(
                        sender=user, receiver=target
                    ).exists() or FriendRequest.objects.filter(
                        sender=target, receiver=user
                    ).exists()
                    if not already_exists:
                        FriendRequestFactory(
                            sender=user,
                            receiver=target,
                            status=FriendRequest.Status.ACCEPTED,
                        )

            # Matches, rounds, stats per user
            self.stdout.write(f"  Creating {matches_per_user} matches per user...")
            for user in users:
                for _ in range(matches_per_user):
                    match = MatchFactory(user=user, map=random.choice(maps))

                    round_numbers = random.sample(
                        range(1, rounds_per_match + 2),
                        k=rounds_per_match
                    )

                    total_kills = 0
                    total_headshots = 0
                    total_deaths = 0
                    total_mvps = 0

                    for round_num in sorted(round_numbers):
                        kills = random.randint(0, 4)
                        headshots = random.randint(0, kills)
                        survived = random.choice([True, False])
                        mvp = random.choice([True, False])

                        RoundEventFactory(
                            match=match,
                            round_number=round_num,
                            kills=kills,
                            headshots=headshots,
                            survived=survived,
                            mvp=mvp,
                        )

                        total_kills += kills
                        total_headshots += headshots
                        if not survived:
                            total_deaths += 1
                        if mvp:
                            total_mvps += 1

                    MatchStatFactory(
                        match=match,
                        kills=total_kills,
                        deaths=total_deaths,
                        assists=random.randint(0, 10),
                        headshots=total_headshots,
                        mvp_rounds=total_mvps,
                        score=random.randint(10, 100),
                    )

            # Chat messages between accepted friends
            self.stdout.write("  Creating chat messages...")
            accepted = FriendRequest.objects.filter(status=FriendRequest.Status.ACCEPTED)
            for fr in accepted:
                for _ in range(random.randint(3, 8)):
                    ChatMessageFactory(sender=fr.sender, receiver=fr.receiver)

        total_matches = Match.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Done. {user_count} users, {total_matches} matches seeded."
        ))