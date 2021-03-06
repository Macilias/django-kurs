from django.shortcuts import render


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    player = request.session["player"]
    print(f"ROOM_NAME: {room_name}, player: {player}")
    return render(
        request,
        "chat/room.html",
        {"room_name": room_name, "player_name": player["name"]},
    )
