"""Helpers para enviar notificaciones WebSocket a clientes (Dashboard y Stock)."""


def send_orders_update(order_id=None, client_name=None):
    """Notifica a los clientes conectados a ws/orders/. Si order_id/client_name se pasan, se muestran en la notificación de nuevo pedido."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        if channel_layer:
            data = {}
            if order_id is not None:
                data['order_id'] = order_id
            if client_name is not None:
                data['client_name'] = client_name
            async_to_sync(channel_layer.group_send)(
                'orders',
                {'type': 'orders_update', 'data': data},
            )
    except Exception:
        pass


def send_stock_update():
    """Notifica a los clientes conectados a ws/stock/ que recarguen stock y pedidos."""
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
