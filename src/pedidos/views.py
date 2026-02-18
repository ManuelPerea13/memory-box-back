from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Pedido, RecorteImagen, OrderStatus
from .serializers import PedidoSerializer, PedidoListSerializer, RecorteImagenSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    """CRUD de pedidos. List/retrieve requieren auth; create puede ser AllowAny para flujo público."""
    queryset = Pedido.objects.all()
    parser_classes = (MultiPartParser, JSONParser)

    def get_serializer_class(self):
        if self.action == 'list':
            return PedidoListSerializer
        return PedidoSerializer

    def get_permissions(self):
        if self.action in ('create', 'retrieve', 'enviar_pedido'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(session_key=self.request.session.session_key)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def enviar_pedido(self, request, pk=None):
        """Marca el pedido como enviado (y opcionalmente dispara webhook n8n)."""
        pedido = self.get_object()
        pedido.status = OrderStatus.SENT
        pedido.save()
        # TODO: llamar a servicio n8n si está configurado
        return Response(PedidoSerializer(pedido).data)


class RecorteImagenViewSet(viewsets.ModelViewSet):
    """CRUD de recortes asociados a un pedido (save_crop / get_existing_crops)."""
    serializer_class = RecorteImagenSerializer
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = [AllowAny]  # En flujo público se asocia por session/pedido_id

    def get_queryset(self):
        pedido_id = self.request.query_params.get('pedido_id') or self.request.data.get('pedido_id')
        if pedido_id:
            return RecorteImagen.objects.filter(pedido_id=pedido_id)
        return RecorteImagen.objects.none()

    def perform_create(self, serializer):
        pedido_id = self.request.data.get('pedido_id')
        if not pedido_id:
            raise ValueError('pedido_id requerido')
        serializer.save(pedido_id=pedido_id)
