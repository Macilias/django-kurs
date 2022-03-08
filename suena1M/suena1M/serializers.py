from rest_framework import serializers

from .models import (
    Game,
    Round,
    Card,
    Table,
    PriorityDeck,
    GlobalCardDeck,
    PlayersCollectedDeck,
    Player,
)


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = "__all__"


class CardSerializer(serializers.ModelSerializer):
    color_value = serializers.CharField(source="color")
    forecast_value = serializers.CharField(source="forecast")

    class Meta:
        model = Card
        fields = "__all__"


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"


class PriorityDeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorityDeck
        fields = "__all__"


class GlobalCardDeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalCardDeck
        fields = "__all__"


class PlayersCollectedDeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayersCollectedDeck
        fields = "__all__"


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"
