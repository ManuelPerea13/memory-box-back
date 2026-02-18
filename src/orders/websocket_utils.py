"""Helpers to send WebSocket notifications to clients (Dashboard and Stock)."""


def send_orders_update(order_id=None, client_name=None, variant=None, with_light=None, status=None):
    """Notify clients connected to ws/orders/. Bell notification payload (order_id, etc.) is only sent when status='in_progress'; otherwise only table refresh."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        data = {}
        if status is not None:
            data['status'] = status
        if status == 'in_progress':
            if order_id is not None:
                data['order_id'] = order_id
            if client_name is not None:
                data['client_name'] = client_name
            if variant is not None:
                data['variant'] = variant
            if with_light is not None:
                data['with_light'] = with_light
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'orders',
                {'type': 'orders_update', 'data': data},
            )
    except Exception:
        pass


def send_stock_update():
    """Notify clients connected to ws/stock/ to reload stock and orders."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'stock',
                {'type': 'stock_update', 'data': {}},
            )
    except Exception:
        pass
