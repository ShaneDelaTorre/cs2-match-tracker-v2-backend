from rest_framework import serializers
from matches.models import Map, Match, RoundEvent, MatchStat


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = ["id", "name", "image_url"]
        read_only_fields = ["id"]


class RoundEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundEvent
        fields = [
            "id", "round_number", "round_result",
            "kills", "headshots", "survived", "mvp",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        if data["headshots"] > data["kills"]:
            raise serializers.ValidationError(
                "Headshots cannot exceed kills in a single round."
            )
        return data


class MatchStatSerializer(serializers.ModelSerializer):
    kd_ratio = serializers.FloatField(read_only=True)
    headshot_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = MatchStat
        fields = [
            "kills", "deaths", "assists", "headshots",
            "mvp_rounds", "score", "kd_ratio", "headshot_percentage",
        ]


class MatchSerializer(serializers.ModelSerializer):
    """Used for list and retrieve — read only, fully nested."""
    map = MapSerializer(read_only=True)
    rounds = RoundEventSerializer(many=True, read_only=True)
    stat = MatchStatSerializer(read_only=True)

    class Meta:
        model = Match
        fields = [
            "id", "map", "game_mode", "result",
            "team_score", "opponent_score", "duration",
            "played_at", "rounds", "stat",
        ]
        read_only_fields = ["id", "result", "team_score", "opponent_score"]


class MatchCreateSerializer(serializers.Serializer):
    """Used only for match creation input — not a ModelSerializer."""
    map_id = serializers.PrimaryKeyRelatedField(
        queryset=Map.objects.all(),
        source="map",
    )
    game_mode = serializers.ChoiceField(choices=Match.GameMode.choices)
    duration = serializers.IntegerField(min_value=1)
    played_at = serializers.DateTimeField()
    score = serializers.IntegerField(min_value=0, default=0)
    assists = serializers.IntegerField(min_value=0, default=0)
    rounds = RoundEventSerializer(many=True)

    def validate_rounds(self, rounds):
        if len(rounds) < 1:
            raise serializers.ValidationError("A match must have at least one round.")

        round_numbers = [r["round_number"] for r in rounds]
        if len(round_numbers) != len(set(round_numbers)):
            raise serializers.ValidationError("Duplicate round numbers are not allowed.")

        return rounds