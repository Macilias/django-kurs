import json
from ssl import SSLSession
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from random import shuffle
from django.contrib import messages
from django.forms.models import model_to_dict
from time import sleep

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
    RoundPurpose,
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
            deckId = None
            if "deckId" in payload:
                deckId = payload["deckId"]
                self.prio_pick(highest_bidder_id=acting_player.get("id"), deckId=deckId)
            else:
                print("could not find deckId in payload")

        if action == Action.PRIO_SPLIT.label:
            print(Action.PRIO_SPLIT.label, payload)
            splitted_cards_count = 0
            card_to_pass_id = None
            if "splitted_cards_count" not in payload:
                splitted_cards_count = payload["splitted_cards_count"]
            else:
                print("could not find splitted_cards_count in payload")

            if "card" not in payload:
                card_to_pass_id = payload["card"]
            else:
                print("could not find card in payload")

            self.prio_split(
                card_to_pass_id=card_to_pass_id,
                highest_bidder_id=acting_player.get("id"),
                splitted_cards_count=splitted_cards_count,
            )

        if action == Action.IDM_BID.label:
            print(Action.IDM_BID.label, payload)
            pass

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
        if (
            game_instance.round_hour_number == RoundPurpose.DAM_BID
            and "dam_highest_value" in payload
        ):
            bidding_done = payload["dam_bidding_done"]
            highest_bidder_id = payload["dam_highest_bidder_id"]
            highest_value = payload["dam_highest_value"]
            highest_bidder_name = payload["dam_highest_bidder_name"]
            context = {
                "registered": user_is_player,
                "game": game_json,
                "player": player,
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
            if players_count > 2:
                selected_prio_deck = 1
                self.prio_pick(
                    deckId=selected_prio_deck, highest_bidder_id=highest_bidder_id
                )
            return

        selected_prio_deck = 0
        if "selected_prio_deck" in payload:
            selected_prio_deck = payload["selected_prio_deck"]

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
        if game_instance.round_hour_number == RoundPurpose.DAM_BID.value:
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
        round_players = Player.objects.get(id=game_instance.round_hour_number)
        round_players_name = round_players.name
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
            "round_players_name": round_players_name,
            "ready_to_start": ready_to_start,
            "dam_highest_value": dam_highest_value,
            "selected_prio_deck": selected_prio_deck,
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
            if player.dam is not None and player.dam > highest_value:
                highest_value = player.dam
                highest_bidder_id = player.id
                highest_bidder_name = player.name

        if value == 0 and highest_bidder_id == game.turn_day_player:
            context = {
                "message": "Du kannst nicht passen, du bist diese Runde drann und es hat dich noch keiner überboten.",
                "level": 3,
                "messageOnly": True,
            }
            self.send(text_data=json.dumps({"context": context}))
            return

        if value == 0 and highest_bidder_id == acting_player.get("id"):
            context = {
                "message": "Du kannst nicht passen, du bist aktuell der Meistbietende!",
                "level": 3,
                "messageOnly": True,
            }
            self.send(text_data=json.dumps({"context": context}))
            return

        for player in players:
            if player.id == acting_player.get("id"):
                player.dam = value
                player.save()
            if player.dam is not None:
                if player.dam == 0:
                    pass_count += 1

        dam_bidding_done = pass_count + 1 == len(players)
        if dam_bidding_done:
            game.turn_hour_player = highest_bidder_id
            game.round_hour_number = RoundPurpose.PRIO_PICK.value
            game.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {
                "type": "game",
                "dam_bidding_done": dam_bidding_done,
                "dam_highest_value": highest_value,
                "dam_highest_bidder_id": highest_bidder_id,
                "dam_highest_bidder_name": highest_bidder_name,
            },
        )

    def prio_pick(self, deckId, highest_bidder_id):
        game = Game.objects.get(slug=self.game_name)
        deckId = int(deckId)
        if deckId != 1 and deckId != 2:
            print(f"prio_pick received bad value {deckId}!")
            return

        if not game.is_started():
            print(f"game {game.name} has not started yet!")
            return

        print(f"plyer with id {highest_bidder_id} picked {deckId} in game: {game.name}")
        game.round_hour_number = RoundPurpose.PRIO_SHOW.value
        game.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {
                "type": "game",
                "selected_prio_deck": deckId,
            },
        )

        print("wait for 5 seconds before consuming the picked priority deck")
        sleep(5)
        print("ok, now consume the deck")

        self.prio_consume(
            game=game, dam_player_id=highest_bidder_id, selected_prio_deck=deckId
        )

    def prio_consume(self, game, dam_player_id, selected_prio_deck):

        priority_decks = game.prioritydeck_set.all()
        priority_deck_cards = Card.objects.filter(
            location=priority_decks[selected_prio_deck - 1].id
        )
        player = Player.objects.get(id=dam_player_id)
        for card in priority_deck_cards:
            card.location = player
            card.save()

        if len(priority_decks) == 2:
            card_deck = game.globalcarddeck_set.first()
            other_deck = 1 if selected_prio_deck == 2 else 2
            other_deck_cards = Card.objects.filter(
                location=priority_decks[other_deck - 1].id
            )
            for card in other_deck_cards:
                card.location = card_deck
                card.save()

        game.round_hour_number = RoundPurpose.PRIO_SPLIT.value
        game.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.game_group_name,
            {
                "type": "game",
                "splitted_cards_count": 0,
            },
        )

    def prio_split(self, card_to_pass_id, highest_bidder_id, splitted_cards_count):
        game = Game.objects.get(slug=self.game_name)

    def get_next_player(self, game, day=False) -> Player:
        players = list(game.player_set.all())
        if day:
            hour_day_player_id = game.turn_day_player
            for i in range(len(players)):
                if players[i].id == hour_day_player_id:
                    j = (i + 1) % len(players)
                    return players[j]

        hour_round_player_id = game.turn_hour_player
        for i in range(len(players)):
            if players[i].id == hour_round_player_id:
                j = (i + 1) % len(players)
                return players[j]
