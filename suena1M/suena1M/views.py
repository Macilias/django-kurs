from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.forms.models import model_to_dict
from random import shuffle

from .models import (
    CardValue,
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


def index(request):
    context = {"games": Game.objects.all()}
    return render(request=request, template_name="suena1M/index.html", context=context)


class GameDetailView(generic.DetailView):
    model = Game
    template_name = "suena1M/game.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_is_player = False
        if "registered_for_games" in self.request.session:
            if context["object"].id in self.request.session["registered_for_games"]:
                user_is_player = True

        context["registered"] = user_is_player
        # context["players"] = model_to_dict(context["game"])
        return context


def game(request, slug):
    game = get_object_or_404(Game, slug=slug)
    template_name = "suena1M/game.html"
    user_is_player = False
    if "registered_for_games" in request.session:
        if game.id in request.session["registered_for_games"]:
            user_is_player = True

    player = None
    # players_cards = []
    if "player" in request.session:
        player = request.session["player"]
        # players_cards = Card.objects.filter(location=player["id"])

    context = {
        "registered": user_is_player,
        "not_registered": not user_is_player,
        "object": game,
        "player": player,
        # "players": game.player_set.all(),
        # "players_cards": players_cards,
        # "card_deck": game.globalcarddeck_set.all(),
        # "prio_deck": game.prioritydeck_set.all(),
        # "table": game.table_set.all(),
        # "cards": game.card_set.all(),
    }
    return render(request=request, template_name=template_name, context=context)


class ResultsDetailView(generic.DetailView):
    model = Game
    template_name = "suena1M/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_is_player = False
        if "registered_for_games" in self.request.session:
            if context["object"].id in self.request.session["registered_for_games"]:
                user_is_player = True

        context["access"] = user_is_player
        return context


def new_game(request):
    name = request.POST["name"]
    print(f"creating new game called {name}")
    encoded_string = name.encode("ascii", "ignore")
    decode_string = encoded_string.decode()
    slug = "-".join(decode_string.split())
    game = Game(name=name, slug=slug)
    game.save()
    return HttpResponseRedirect(reverse("game", args=(game.slug,)))


def create_cards(game, location):
    # now lets create the card deck
    cards = []
    for s in EnergySource:
        for y in CardValue:
            c = Card(game=game, location=location, value=y, source=s)
            cards.append(c)
            c.save()

    return cards


# def start_game(request, slug):
#     return
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
#     players_count = game.player_set.count()
#     cards = create_cards(game=game, location=card_deck)
#     shuffle(cards)
#     if players_count == 2:
#         prio_deck2 = PriorityDeck(game=game)
#         prio_deck2.save()

#     # add notification for other users about who started the game
#     full_message = f"Er sagt: {message}"
#     messages.info(
#         request,
#         f"Das Spiel wurde von {player.get('name')} gestartet. "
#         f"{full_message if message else ''}",
#     )

#     return HttpResponseRedirect(reverse("game", args=(game.slug,)))


def register(request, slug):
    game = get_object_or_404(Game, slug=slug)
    name = request.POST["name"]
    new_player = Player(game=game, name=name)
    new_player.save()
    players_collected_deck = PlayersCollectedDeck(user=new_player)
    players_collected_deck.save()
    request.session["registered"] = True
    request.session["player"] = model_to_dict(new_player)

    if "registered_for_games" in request.session:
        if type(request.session["registered_for_games"]) == list:
            registered_for_games = request.session["registered_for_games"]
            registered_for_games.append(game.id)
            request.session["registered_for_games"] = registered_for_games
        else:
            request.session["registered_for_games"] = [game.id]
    else:
        request.session["registered_for_games"] = [game.id]

    return HttpResponseRedirect(reverse("game", args=(game.slug,)))
