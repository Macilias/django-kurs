from django.db import models
from enum import Enum


class EnergySource(Enum):
    S = "Solar"
    W = "Wind"
    A = "Atomic"
    C = "Carbon"


class Forecast(Enum):
    W = "Weather"
    M = "Market"
    N = "Non"


class Round(models.Model):
    current_triumph_source = models.CharField(
        max_length=1, choices=[(e, e.value) for e in EnergySource]
    )
    round_number = models.IntegerField(default=0)

    def __str__(self):
        return f"round: {self.round_number} triumph: {self.current_triumph_source}"


class Game(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)
    time = models.DateTimeField(null=True)
    round_number = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    started = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def is_active(self):
        return self.active

    def is_started(self):
        return self.started


class Card(models.Model):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    location = models.ForeignKey(to="CardHolder", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    value = models.IntegerField(default=0)
    source = models.CharField(
        max_length=1, choices=[(e, e.value) for e in EnergySource]
    )
    forecast = models.CharField(max_length=1, choices=[(e, e.value) for e in Forecast])

    def __str__(self):
        return f"{self.game.name} ({self.name})"


class CardHolder(models.Model):
    pass


class Table(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    pass


class PriorityDeck(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    pass


class GlobalCardDeck(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    pass


class PlayersCollectedDeck(CardHolder):
    user = models.CharField(max_length=256)
    pass


class Player(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    dam = models.IntegerField(default=0)
    idm = models.IntegerField(default=0)
    round_score = models.IntegerField(default=0)
    game_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} is playing {self.game.name} game score: {self.game_score}"
