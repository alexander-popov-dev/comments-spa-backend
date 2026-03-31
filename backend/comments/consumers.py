from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CommentConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer that broadcasts new comments to all connected clients."""

    async def connect(self):
        """Add client to the comments group on connection."""
        await self.channel_layer.group_add("comments", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Remove client from the comments group on disconnection."""
        await self.channel_layer.group_discard("comments", self.channel_name)

    async def new_comment(self, event):
        """Send new comment data to the WebSocket client."""
        await self.send_json(event["data"])
