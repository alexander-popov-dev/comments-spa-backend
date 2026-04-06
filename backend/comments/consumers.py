from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CommentConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer that broadcasts comment events to all connected clients."""

    async def connect(self):
        """Add client to the comments group on connection."""
        await self.channel_layer.group_add("comments", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Remove client from the comments group on disconnection."""
        await self.channel_layer.group_discard("comments", self.channel_name)

    async def comment_event(self, event):
        """Forward a comment event (created/updated/deleted) to the WebSocket client."""
        await self.send_json(event["data"])
