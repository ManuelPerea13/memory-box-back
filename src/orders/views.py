import io
import json
import qrcode
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.files.base import ContentFile

from .models import Order, ImageCrop, OrderStatus
from .serializers import OrderSerializer, OrderListSerializer, ImageCropSerializer

REQUIRED_IMAGE_COUNT = 10


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD for orders. List/retrieve require auth; create can be AllowAny for public flow."""
    queryset = Order.objects.all()
    parser_classes = (MultiPartParser, JSONParser)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ('create', 'retrieve', 'update', 'partial_update', 'send_order', 'submit_images'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(session_key=self.request.session.session_key)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def send_order(self, request, pk=None):
        """Mark the order as sent, generate QR code, and optionally trigger n8n webhook."""
        order = self.get_object()
        order.status = OrderStatus.SENT

        # Generate QR code with frontend URL (same size as images ~400px)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        qr_url = f'{frontend_url.rstrip("/")}/pedido/{order.id}'
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        img = img.resize((400, 400))

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        filename = f'order_{order.id}_qr.png'
        order.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        order.save()

        # TODO: call n8n service if configured
        return Response(OrderSerializer(order, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def submit_images(self, request, pk=None):
        """
        Submit 10 images with crop_data. Creates/updates ImageCrop records.
        Expects multipart/form-data: image_0..image_9, crop_data_0..crop_data_9 (JSON strings).
        """
        order = self.get_object()

        # Validate we have all 10 images and crop_data
        images_data = []
        for i in range(REQUIRED_IMAGE_COUNT):
            img_file = request.FILES.get(f'image_{i}')
            crop_str = request.data.get(f'crop_data_{i}')
            if not img_file:
                return Response(
                    {'error': f'Missing image_{i}. Exactly {REQUIRED_IMAGE_COUNT} images required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not crop_str:
                return Response(
                    {'error': f'Missing crop_data_{i} for image {i + 1}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                crop_data = json.loads(crop_str) if isinstance(crop_str, str) else crop_str
            except (json.JSONDecodeError, TypeError):
                return Response(
                    {'error': f'Invalid crop_data_{i}: must be valid JSON.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Normalize keys (accept x,y,w,h or x,y,width,height)
            if 'w' in crop_data and 'width' not in crop_data:
                crop_data['width'] = crop_data['w']
            if 'h' in crop_data and 'height' not in crop_data:
                crop_data['height'] = crop_data['h']
            images_data.append({'file': img_file, 'crop_data': crop_data})

        # Create or update ImageCrop for each slot
        for i, data in enumerate(images_data):
            obj, created = ImageCrop.objects.update_or_create(
                order=order,
                slot=i,
                defaults={
                    'display_order': i,
                    'image': data['file'],
                    'crop_data': data['crop_data'],
                }
            )

        return Response(OrderSerializer(order).data)


class ImageCropViewSet(viewsets.ModelViewSet):
    """CRUD for image crops associated with an order (save_crop / get_existing_crops)."""
    serializer_class = ImageCropSerializer
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = [AllowAny]  # In public flow, associated by session/order_id

    def get_queryset(self):
        order_id = self.request.query_params.get('order_id') or self.request.data.get('order_id')
        if order_id:
            return ImageCrop.objects.filter(order_id=order_id)
        return ImageCrop.objects.none()

    def perform_create(self, serializer):
        order_id = self.request.data.get('order_id')
        if not order_id:
            raise ValueError('order_id required')
        serializer.save(order_id=order_id)
