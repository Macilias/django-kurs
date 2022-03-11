import json
from ssl import SSLSession
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from random import shuffle
from django.contrib import messages
from django.forms.models import model_to_dict

from .serializers import (
    GameSerializer,
    PlayerSerializer,
    CardSerializer,
)

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
        acting_player = payload["player"]

        if action == Action.CONNECT.label:
            self.game(payload)

        if action == Action.START_GAME.label:
            message = None
            if "message" in payload:
                message = payload["message"]
            self.start_game(acting_player=acting_player, message=message)

        if action == Action.DAM_BID.label:
            value = None
            if "value" in payload:
                value = payload["value"]
                self.dam_bid(acting_player=acting_player, value=value)
            else:
                print("could not find vlaue in payload")

        if action == Action.PRIO_PICK.label:
            print(Action.PRIO_PICK.label, payload)
            pass  # optional

        if action == Action.PRIO_SPLIT.label:
            print(Action.PRIO_SPLIT.label, payload)
            pass

        if action == Action.IDM_BID.label:
            print(Action.IDM_BID.label, payload)
            pass

        # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.game_group_name,
        #     {"type": "chat_message", "message": message},
        # )

    # Receive message from room group
    def game(self, payload):
        game_instance = Game.objects.get(slug=self.game_name)
        game_json = GameSerializer(game_instance).data
        user_is_player = False
        if "registered_for_games" in self.scope["session"]:
            if game_instance.id in self.scope["session"]["registered_for_games"]:
                user_is_player = True

        players = game_instance.player_set.all()
        players_count = len(players)
        ready_to_start = 2 <= players_count < 4

        message = None
        if "message" in payload:
            message = payload["message"]

        level = None
        if "level" in payload:
            level = payload["level"]

        player = None
        players_cards = []
        if "player" in self.scope["session"]:
            player = self.scope["session"]["player"]
            players_cards = Card.objects.filter(location=player["id"])

        # round_hour_number
        if "dam_highest_value" in payload:
            bidding_done = payload["dam_bidding_done"]
            highest_bidder_id = payload["dam_highest_bidder_id"]
            selected_prio_deck = 0
            if bidding_done:
                game_instance.round_hour_number += 1
                if players_count > 2:
                    selected_prio_deck = 1
                    game_instance.round_hour_number += 1
                # if players_count > 2:
                #     priority_decks = game_instance.prioritydeck_set.all()
                #     priority_deck1_cards = Card.objects.filter(
                #         location=priority_decks[0].id
                #     )
                #     for card in priority_deck1_cards:
                #         card.location = highest_bidder_id
                #         card.save()
                #     players_cards = Card.objects.filter(location=player["id"])
                #     game_instance.round_hour_number += 1
                game_instance.save()
                game_json = GameSerializer(game_instance).data

            highest_value = payload["dam_highest_value"]
            highest_bidder_name = payload["dam_highest_bidder_name"]
            context = {
                "registered": user_is_player,
                "game": game_json,
                "player": player,
                "selected_prio_deck": selected_prio_deck,
                # "players_cards": CardSerializer(players_cards, many=True).data,
                "message": message,
                "level": level,
                "players": PlayerSerializer(players, many=True).data,
                "dam_bidding_done": bidding_done,
                "dam_highest_value": highest_value,
                "dam_highest_bidder_id": highest_bidder_id,
                "dam_highest_bidder_name": highest_bidder_name,
                "ASGI": True,
            }
            self.send(text_data=json.dumps({"context": context}))
            return

        if not game_instance.is_started():
            context = {
                "registered": user_is_player,
                "game": game_json,
                "player": player,
                "message": message,
                "level": level,
                "players": PlayerSerializer(players, many=True).data,
                "players_count": players_count,
                "ready_to_start": ready_to_start,
                "ASGI": True,
            }
            self.send(text_data=json.dumps({"context": context}))
            return

        dam_highest_value = 100
        if game_instance.round_hour_number == 0:
            for p in players:
                if p.dam is not None and p.dam > dam_highest_value:
                    dam_highest_value = p.dam

        card_deck = game_instance.globalcarddeck_set.all().first()
        print("card_deck: ", card_deck)
        card_deck_cards = Card.objects.filter(location=card_deck.id)
        print("card_deck_cards: ", card_deck_cards)

        priority_decks = game_instance.prioritydeck_set.all()
        print("card_deck: ", card_deck)
        priority_deck1_cards = Card.objects.filter(location=priority_decks[0].id)
        print("priority_deck1_cards: ", priority_deck1_cards)
        priority_deck2_cards = []
        if len(players) == 2 and len(priority_decks) == 2:
            priority_deck2_cards = Card.objects.filter(location=priority_decks[1].id)
            print("priority_deck2_cards: ", priority_deck2_cards)

        table = game_instance.table_set.all().first()
        print("table: ", table)
        table_cards = Card.objects.filter(location=table.id)
        print("table_cards: ", table_cards)

        context = {
            "registered": user_is_player,
            "game": game_json,
            "player": player,
            "message": message,
            "level": level,
            "players": PlayerSerializer(players, many=True).data,
            "players_cards": CardSerializer(players_cards, many=True).data,
            "card_deck": CardSerializer(card_deck_cards, many=True).data,
            "prio_deck1": CardSerializer(priority_deck1_cards, many=True).data,
            "prio_deck2": CardSerializer(priority_deck2_cards, many=True).data,
            "table_deck": CardSerializer(table_cards, many=True).data,
            "players_count": players_count,
            "ready_to_start": ready_to_start,
            "dam_highest_value": dam_highest_value,
            "ASGI": True,
        }
        self.send(text_data=json.dumps({"context": context}))

    def deal_cards(
        self,
        card_deck_cards,
        players,
        prio_deck1,
        prio_deck2,
    ):
        i = 0
        p = len(players)
        d = 3
        if p == 2:
            d = 4
        while i < len(card_deck_cards):
            card = card_deck_cards[i]
            if i < d:
                if p == 2 and i >= 2:
                    card.location = prio_deck2
                else:
                    card.location = prio_deck1

            else:
                player = players[i % p]
                card.location = player

            card.save()
            i += 1

    def create_cards(self, game, location):
        # now lets create the card deck
        cards = []
        for s in EnergySource:
            for y in CardValue:
                c = Card(game=game, location=location, value=y, source=s)
                cards.append(c)
                c.save()

        return cards

    def start_game(self, acting_player, message):
        game = Game.objects.get(slug=self.game_name)
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
        prio_deck2 = None
        if players_count == 2:
            prio_deck2 = PriorityDeck(game=game)
            prio_deck2.save()

        cards = self.create_cards(game=game, location=card_deck)
        shuffle(cards)
        shuffle(cards)
        shuffle(cards)

        players = game.player_set.all()
        first_player = players.first()
        first_player.dam = 100
        first_player.save()
        game.turn_hour_player = first_player.id  # this one iterats from hour to hour
        game.turn_day_player = first_player.id  # this one iterats from day to day
        game.save()

        self.deal_cards(
            card_deck_cards=cards,
            players=players,
            prio_deck1=prio_deck1,
            prio_deck2=prio_deck2,
        )

        # add notification for other users about who started the game
        full_message = f"Er/Sie sagt: {message}"
        message = f"Das Spiel wurde von {acting_player.get('name')} gestartet. {full_message if message else ''}"
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {
                "type": "game",
                "message": message,
                "level": 1,
            },
        )

    def dam_bid(self, acting_player, value):
        game = Game.objects.get(slug=self.game_name)
        try:
            value = int(value)
        except TypeError:
            print(f"ERROR: can not parse value: {value}")
            return

        if not game.is_started():
            print(f"game {game.name} has not started yet!")
            return

        print(f"{acting_player.get('name')} is bidding {value} in game: {game.name}")
        players = game.player_set.all()
        pass_count = 0
        highest_value = 0
        highest_bidder_id = None
        highest_bidder_name = None
        for player in players:
            if player.id == acting_player.get("id"):
                player.dam = value
                player.save()
            if player.dam is not None:
                if player.dam == 0:
                    pass_count += 1
                if player.dam > highest_value:
                    highest_value = player.dam
                    highest_bidder_id = player.id
                    highest_bidder_name = player.name

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {
                "type": "game",
                "dam_bidding_done": pass_count + 1 == len(players),
                "dam_highest_value": highest_value,
                "dam_highest_bidder_id": highest_bidder_id,
                "dam_highest_bidder_name": highest_bidder_name,
            },
        )
