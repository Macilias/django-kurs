from django.db import models

ENERGY_SOURCE = (
    ('S', 'Solar'),
    ('W', 'Wind'),
    ('A', 'Atomic'),
    ('C', 'Carbon'),
)

FORECAST = (
    ('W', 'Weather'),
    ('M', 'Market'),
    ('N', 'Non'),
)


class Round(models.Model):
    current_triumph_source = models.CharField(max_length=1, choices=ENERGY_SOURCE)
    round_number = models.IntegerField(default=0)

    def __str__(self):
        return f"round: {self.round_number} triumph: {self.current_triumph_source}"


class Game(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)
    time = models.DateTimeField()
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
    game = models.ForeignKey(to='Game', on_delete=models.CASCADE)
    location = models.ForeignKey(to='CardHolder', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    value = models.IntegerField(default=0)
    source = models.CharField(max_length=1, choices=ENERGY_SOURCE)
    forecast = models.CharField(max_length=1, choices=FORECAST)

    def __str__(self):
        return f"{self.game.name} ({self.name})"


class CardHolder(models.Model):
    # class Meta:
    #     abstract = True
    pass


class Table(CardHolder):
    pass


class PriorityDeck(CardHolder):
    pass


class GlobalCardDeck(CardHolder):
    pass


class PlayersCollectedDeck(CardHolder):
    user = models.CharField(max_length=256)
    pass


class Player(CardHolder):
    game = models.ForeignKey(to='Game', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    score = models.IntegerField(default=0)
    source = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} is playing {self.game.name} score: {self.score}"
