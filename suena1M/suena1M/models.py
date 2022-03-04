from django.db import models
from enum import Enum


class EnergySource(models.TextChoices):
    SOLAR = "S", "Solar"
    WIND = "W", "Wind"
    ATOMIC = "A", "Atomic"
    CARBON = "C", "Carbon"


class Forecast(models.TextChoices):
    WEATHER = "W", "Weather"
    MARKET = "M", "Market"


class CardValue(models.IntegerChoices):
    NEUN = 0
    ZEHN = 10
    JACK = 2
    DAME = 3
    KING = 4
    ASS = 11


class Round(models.Model):
    current_triumph_source = models.CharField(
        max_length=1, choices=EnergySource.choices
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
    value = models.IntegerField(choices=CardValue.choices)
    source = models.CharField(max_length=1, choices=EnergySource.choices)

    def __str__(self):
        return f"[{self.game.name}] {self.value}K {EnergySource(self.source).label} forecast: {self.forecast(as_label=True)} location: {self.location}"

    def color(self):
        if self.source == EnergySource.SOLAR:
            return "yellow"
        if self.source == EnergySource.WIND:
            return "#2f76c7"
        if self.source == EnergySource.ATOMIC:
            return "aqua"
        if self.source == EnergySource.CARBON:
            return "black"

    def forecast(self, as_label=False):
        if self.value == CardValue.DAME.value:
            if not as_label:
                return Forecast.WEATHER
            else:
                return Forecast(Forecast.WEATHER).label
        if self.value == CardValue.KING.value:
            if not as_label:
                return Forecast.MARKET
            else:
                return Forecast(Forecast.MARKET).label


class CardHolder(models.Model):
    def __str__(self):
        return f"abstract carholder id: {self.pk}"


class Table(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)

    def __str__(self):
        return f"table id: {self.pk}"


class PriorityDeck(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)

    def __str__(self):
        return f"priority deck id: {self.pk}"


class GlobalCardDeck(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)

    def __str__(self):
        return f"card deck id: {self.pk}"


class PlayersCollectedDeck(CardHolder):
    user = models.CharField(max_length=256)

    def __str__(self):
        return f"player {self.user.name} deck id: {self.pk}"


class Player(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    dam = models.IntegerField(default=0)
    idm = models.IntegerField(default=0)
    round_score = models.IntegerField(default=0)
    game_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} is playing {self.game.name} game score: {self.game_score} id: {self.pk}"
