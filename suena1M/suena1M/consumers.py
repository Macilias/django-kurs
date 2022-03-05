import json
from ssl import SSLSession
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from random import shuffle
from django.contrib import messages

from .models import (
    Action,
    EnergySource,
    Forecast,
    CardValue,
    Card,
    CardHolder,
    GlobalCardDeck,
    Game,
    Player,
    PlayersCollectedDeck,
    PriorityDeck,
    Round,
    Table,
)


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_name = self.scope["url_route"]["kwargs"]["slug"]
        self.game_group_name = "game_%s" % self.game_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.game_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        payload = json.loads(text_data)
        action = payload["action"]
        message = payload["message"]
        acting_player = payload["player"]
        game = Game.objects.get(slug=self.game_name)

        if action == Action.START_GAME.label:
            self.start_game(game=game, acting_player=acting_player, message=message)

        # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.game_group_name,
        #     {"type": "chat_message", "message": message},
        # )

    # Receive message from room group
    def game(self, event):
        self.send(text_data=json.dumps({"message": f"{event}"}))

    def create_cards(self, game, location):
        # now lets create the card deck
        cards = []
        for s in EnergySource:
            for y in CardValue:
                c = Card(game=game, location=location, value=y, source=s)
                cards.append(c)
                c.save()

        return cards

    def start_game(self, game, acting_player, message):
        if game.is_started():
            print(f"game {game.name} is already started")
            return

        print(f"starting new game called {game.name} by {acting_player.get('name')}")

        game.started = True
        game.save()
        card_deck = GlobalCardDeck(game=game)
        card_deck.save()
        table = Table(game=game)
        table.save()
        prio_deck1 = PriorityDeck(game=game)
        prio_deck1.save()
        players_count = game.player_set.count()
        cards = self.create_cards(game=game, location=card_deck)
        shuffle(cards)
        if players_count == 2:
            prio_deck2 = PriorityDeck(game=game)
            prio_deck2.save()

        # add notification for other users about who started the game
        full_message = f"Er/Sie sagt: {message}"
        message = f"Das Spiel wurde von {acting_player.get('name')} gestartet. {full_message if message else ''}"
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {"type": "game", "message": message},
        )
