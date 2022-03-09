from django.contrib import admin
from .models import (
    Card,
    CardHolder,
    PriorityDeck,
    GlobalCardDeck,
    PlayersCollectedDeck,
    Game,
    Player,
    Table,
)

admin.site.register(Card)
admin.site.register(CardHolder)
admin.site.register(PriorityDeck)
admin.site.register(GlobalCardDeck)
admin.site.register(PlayersCollectedDeck)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Table)
