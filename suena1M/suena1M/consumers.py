import json
from ssl import SSLSession
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from random import shuffle

from .models import (
    EnergySource,
    Forecast,
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
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        player_name = text_data_json["player_name"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {"type": "chat_message", "message": message, "player_name": player_name},
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        player_name = event["player_name"]
        player = self.scope["session"]["player"]
        if player["name"] == player_name:
            player_name = "Du"

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": f"{player_name}: {message}"}))

    # def start_game(request, slug):
    #     game = get_object_or_404(Game, slug=slug)
    #     player = request.session["player"]
    #     message = request.POST["message"]
    #     if game.is_started():
    #         return HttpResponseRedirect(reverse("game", args=(game.slug,)))

    #     print(f"starting new game called {game.name} by {player.get('name')}")
    #     game.started = True
    #     game.save()
    #     card_deck = GlobalCardDeck(game=game)
    #     card_deck.save()
    #     table = Table(game=game)
    #     table.save()
    #     prio_deck1 = PriorityDeck(game=game)
    #     prio_deck1.save()
    #     players = game.player_set.all()
    #     cards = create_cards(game=game, location=card_deck)
    #     shuffle(cards)
    #     if len(players) == 2:
    #         prio_deck2 = PriorityDeck(game=game)
    #         prio_deck2.save()

    #     # add notification for other users about who started the game
    #     full_message = f"Er sagt: {message}"
    #     messages.info(
    #         request,
    #         f"Das Spiel wurde von {player.get('name')} gestartet. {full_message if message else ''}",
    #     )

    #     return HttpResponseRedirect(reverse("game", args=(game.slug,)))
