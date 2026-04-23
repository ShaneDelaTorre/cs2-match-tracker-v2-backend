from django.db import models
from django.conf import settings

# Create your models here.
class Map(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image_url = models.URLField(blank=True, default="")

    def __str__(self):
        return self.name

class Match(models.Model):
    class GameMode(models.TextChoices):
        PREMIER = "Premier"
        COMPETITIVE = "Competitive"

    class Result(models.TextChoices):
        WIN = "Win"
        LOSS = "Loss"
        DRAW = "Draw"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matches")
    map = models.ForeignKey(Map, on_delete=models.PROTECT, related_name="matches")
    game_mode = models.CharField(max_length=24, choices=GameMode.choices, default=GameMode.PREMIER)
    team_score = models.PositiveSmallIntegerField()
    opponent_score = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField(help_text="Duration in minutes")
    played_at = models.DateTimeField()


class RoundEvent(models.Model):
    class RoundResult(models.TextChoices):
        WIN = "Win"
        LOSS = "Loss"

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="rounds")
    round_number = models.PositiveSmallIntegerField()
    round_result = models.CharField(max_length=12, choices=RoundResult.choices)
    kills = models.PositiveSmallIntegerField(default=0)
    headshots = models.PositiveSmallIntegerField(default=0)
    survived = models.BooleanField(default=False)
    mvp = models.BooleanField(default=False)

    class Meta:
        unique_together = ("match", "round_number",)
        ordering = ("round_number",)

class MatchStat(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="stat")
    kills = models.PositiveSmallIntegerField(default=0)
    deaths = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    headshots = models.PositiveSmallIntegerField(default=0)
    mvp_rounds = models.PositiveSmallIntegerField(default=0)
    score = models.PositiveSmallIntegerField(default=0)

    @property
    def kd_ratio(self):
        if self.deaths == 0:
            return float(self.kills)
        return round(self.kills/self.deaths, 2)
    
    @property
    def headshot_percentage(self):
        if self.kills == 0:
            return 0.0
        return round((self.headshots/self.kills) * 100, 2)

