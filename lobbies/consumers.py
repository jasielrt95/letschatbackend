from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_id = self.scope["url_route"]["kwargs"]["lobby_id"]
        self.lobby_group_name = f"lobby_{self.lobby_id}"
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.lobby_group_name, {"type": "lobby_message", "message": "recivido compai'"}
        )

    async def lobby_message(self, event):
        action = event["action"]
        data = event["data"]
        await self.send(text_data=json.dumps({"action": action, "data": data}))