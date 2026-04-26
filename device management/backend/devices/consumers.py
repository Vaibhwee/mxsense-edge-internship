import json
import re

from channels.generic.websocket import AsyncWebsocketConsumer


def device_group_name(device_id: str) -> str:
    safe_device_id = re.sub(r"[^0-9A-Za-z_.-]", "_", device_id)
    return f"device_{safe_device_id}"[:99]


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("dashboard", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    async def telemetry(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]
        self.group_name = device_group_name(self.device_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def telemetry(self, event):
        await self.send(text_data=json.dumps(event["data"]))
