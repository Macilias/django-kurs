import json
from ssl import SSLSession
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class GameConsumer_sync(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = "game_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        player_name = text_data_json["player_name"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
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


class GameConsumer(GameConsumer_sync):
    pass
