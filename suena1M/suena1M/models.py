from django.utils import timezone
from django.db import models
from enum import Enum


class Action(models.TextChoices):
    CONNECT = "CON", "CONNECT"
    START_GAME = "STA", "START_GAME"
    PRIO_PICK = "PIC", "PRIO_PICK"  # round 1 - only when 2 players are playing
    # prio show and subsequent prio consume is called autmatically after 5 sec and is round 2
    PRIO_SPLIT = "SPL", "PRIO_SPLIT"  # round 3
    DAM_BID = "DAM", "DAM_BID"  # round 0
    IDM_BID = "IDM", "IDM_BID"  # round 4-N


class RoundPurpose(Enum):
    DAM_BID = 0
    PRIO_PICK = 1
    PRIO_SHOW = 2
    PRIO_SPLIT = 3
    IDM_BID = 4  # and subsequent


class EnergySource(models.TextChoices):
    SOLAR = "S", "Solar"
    WIND = "W", "Wind"
    ATOMIC = "A", "Atomic"
    CARBON = "C", "Carbon"


class Forecast(models.TextChoices):
    WEATHER = "W", "Weather"
    MARKET = "M", "Market"


forecast_lookup = {
    EnergySource.SOLAR.value: 100,
    EnergySource.WIND.value: 80,
    EnergySource.CARBON.value: 60,
    EnergySource.ATOMIC.value: 40,
}


class CardValue(models.IntegerChoices):
    NEUN = 0
    ZEHN = 10
    BUBE = 2
    DAME = 3
    KING = 4
    ASS = 11


class Game(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    round_hour_number = models.IntegerField(default=0)
    round_day_number = models.IntegerField(default=0)
    turn_hour_player = models.IntegerField(default=0)
    turn_day_player = models.IntegerField(default=0)
    splitted_cards_count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    started = models.BooleanField(default=False)
    current_domination = models.CharField(
        max_length=1, choices=EnergySource.choices, blank=True, null=True
    )

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def is_active(self):
        return self.active

    def is_inactive(self):
        return not self.active

    def is_started(self):
        return self.started

    def is_not_started(self):
        return not self.started

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Game, self).save(*args, **kwargs)


class Card(models.Model):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    location = models.ForeignKey(to="CardHolder", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    value = models.IntegerField(choices=CardValue.choices)
    source = models.CharField(max_length=1, choices=EnergySource.choices, null=False)

    def __str__(self):
        return f"[{self.game.name}] {self.value}K {EnergySource(self.source).label} forecast: {self.forecast()} location: {self.location}"

    def color(self):
        if self.source == EnergySource.SOLAR:
            return "#FFB600"
        if self.source == EnergySource.WIND:
            return "#2f76c7"
        if self.source == EnergySource.ATOMIC:
            return "aqua"
        if self.source == EnergySource.CARBON:
            return "black"

    def forecast(self):
        if self.value == CardValue.DAME.value:
            return Forecast(Forecast.WEATHER).label
        if self.value == CardValue.KING.value:
            return Forecast(Forecast.MARKET).label
        return ""


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
        return f"player {self.user} deck id: {self.pk}"


class Player(CardHolder):
    game = models.ForeignKey(to="Game", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    dam = models.IntegerField(null=True)
    idm = models.IntegerField(null=True)
    round_score = models.IntegerField(default=0)
    game_score = models.IntegerField(default=0)
    last_played_round = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} is playing {self.game.name} game score: {self.game_score} id: {self.pk}"
