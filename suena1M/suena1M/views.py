from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.forms.models import model_to_dict

from .models import Card, CardHolder, GlobalCardDeck, Game, Player, Round, Table


def index(request):
    context = {"games": Game.objects.all()}
    return render(request=request, template_name="suena1M/index.html", context=context)


class GameDetailView(generic.DetailView):
    model = Game
    template_name = "suena1M/field.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_is_player = False
        if "registered_for_games" in self.request.session:
            if context["object"].id in self.request.session["registered_for_games"]:
                user_is_player = True

        context["registered"] = user_is_player
        return context


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


def start_game(request, slug):
    game = get_object_or_404(Game, slug=slug)
    player = request.session["player"]
    message = request.POST["message"]
    if not game.is_started():
        print(f"starting new game called {game.name} by {player.get('name')}")
        game.started = True
        game.save()
        # add notification for other users about who started the game
        full_message = f"Er sagt: {message}"
        messages.info(
            request,
            f"Das Spiel wurde von {player.get('name')} gestartet. {full_message if message else ''}",
        )

    return HttpResponseRedirect(reverse("game", args=(game.slug,)))


def register(request, slug):
    game = get_object_or_404(Game, slug=slug)
    name = request.POST["name"]
    new_player = Player(game=game, name=name)
    new_player.save()
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


def play(request, slug):
    game = get_object_or_404(Game, slug=slug)
    card = Card.objects.get(pk=request.POST["choice"])
    player = Player.objects.get(pk=request.POST["player"].pk)
    try:
        selected = player.card_set.get(card)
    except (KeyError, Card.DoesNotExist):
        messages.error(
            request, "Fehler: es wurde keine bzw. eine ungültige Karte ausgeählt!"
        )
        return HttpResponseRedirect(reverse("game", args=(game.slug,)))

    else:
        pass
        # selected.votes += 1
        # selected.save()
        #
        return HttpResponseRedirect(reverse("suena1M:results", args=(game.slug,)))
