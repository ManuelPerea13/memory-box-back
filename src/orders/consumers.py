from channels.generic.websocket import AsyncWebsocketConsumer
import json


class OrdersConsumer(AsyncWebsocketConsumer):
    """WebSocket para actualizaciones de la tabla de pedidos (Dashboard)."""

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('orders', self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('orders', self.channel_name)

    async def orders_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'orders_update',
            'data': event.get('data', {}),
        }))


class StockConsumer(AsyncWebsocketConsumer):
    """WebSocket para actualizaciones de stock y pedidos en curso (página Stock)."""

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('stock', self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('stock', self.channel_name)

    async def stock_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stock_update',
            'data': event.get('data', {}),
        }))
