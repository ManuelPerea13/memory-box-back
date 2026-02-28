import io
import json
import logging
import math
import qrcode
import urllib.request
import urllib.error
from PIL import Image
from django.conf import settings
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.core.files.base import ContentFile
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

logger = logging.getLogger(__name__)

from .models import (
    Order, ImageCrop, OrderStatus, Stock, STOCK_VARIANTS, BoxType, PackagingStock,
)
from .serializers import (
    OrderSerializer, OrderListSerializer, ImageCropSerializer, StockSerializer,
    PackagingStockSerializer, PurchaseSerializer,
)
from .websocket_utils import send_orders_update, send_stock_update
from config.views import get_settings
from expenses.views import get_cost_settings
from expenses.models import Purchase, PurchaseCategory

REQUIRED_IMAGE_COUNT = 10

# Mapeo variant del pedido -> nombre variante para PLA (Grafito, Madera, etc.)
ORDER_VARIANT_TO_PLA_VARIANTE = {
    'graphite': 'Grafito',
    'wood': 'Madera',
    'black': 'Negro',
    'marble': 'Mármol',
    'graphite_light': 'Grafito',
    'wood_light': 'Madera',
    'black_light': 'Negro',
    'marble_light': 'Mármol',
}


def _get_packaging_unit_costs():
    """
    Costo unitario de caja de cartón y bolsa ecommerce desde la última compra de cada tipo.
    unit_cost = total_cost / quantity (o unit_cost del registro si está definido).
    """
    result = {'caja_carton': 0.0, 'bolsa_ecommerce': 0.0}
    for category in (PurchaseCategory.CAJA_CARTON, PurchaseCategory.BOLSA_ECOMMERCE):
        last = Purchase.objects.filter(category=category).order_by('-date', '-id').first()
        if last and last.quantity and last.quantity > 0:
            total = float(last.total_cost or 0)
            if last.unit_cost is not None:
                result[category] = float(last.unit_cost)
            else:
                result[category] = total / last.quantity
    return result


def _compute_order_cost_snapshot(order):
    """
    Calcula el snapshot de costos del pedido con los valores actuales (referencia + PLA + empaque).
    Se guarda al finalizar; así si después cambian precios/PLA/empaque, este pedido mantiene su costo.
    - Sin luz: cost_pla = caja base = 63g × (precio rollo PLA/1000) según variante; cost_caja = 0 (todo el costo de caja es PLA).
    - Con luz: cost_caja = suma de componentes de referencia; cost_pla = 0 (no entra en la fórmula).
    - Empaque: 1 caja de cartón + 1 bolsa a costo unitario (total compra / cantidad) de la última compra.
    """
    cost_data = get_cost_settings().data or {}
    cost_caja = 0
    cost_pla = 0

    if order.box_type == BoxType.WITH_LIGHT:
        componentes = cost_data.get('cost_con_luz_componentes') or []
        cost_caja = sum(
            float(c.get('valor') or c.get('value') or 0)
            for c in componentes
        )
        # Con luz: no se incluye PLA en la fórmula (solo cost_caja = componentes + empaque + troqueles).
    else:
        # Sin luz: toda la caja base = 63g × (precio rollo/1000); no se desglosa PLA por separado
        variante_name = ORDER_VARIANT_TO_PLA_VARIANTE.get(
            (order.variant or '').strip().lower(),
            (order.variant or '').strip()
        )
        if variante_name:
            pla_purchase = (
                Purchase.objects.filter(
                    category=PurchaseCategory.PLA_ROLL,
                    variant__iexact=variante_name,
                )
                .order_by('-date', '-id')
                .first()
            )
            if pla_purchase:
                cost_per_gram = pla_purchase.pla_cost_per_gram()
                if cost_per_gram is not None:
                    variant_grams_map = cost_data.get('variant_grams') or {}
                    grams = cost_data.get('grams_caja_sin_luz')
                    if grams is None or grams == '':
                        grams = variant_grams_map.get(variante_name)
                    if grams is not None and grams != '':
                        grams = float(grams)
                    else:
                        grams = 63  # default for no-light box
                    if grams > 0:
                        base_cost = float(cost_per_gram) * grams
                        # Para sin luz el costo de la caja base es 100% PLA; guardamos en cost_pla para desglose.
                        cost_pla = base_cost
                        cost_caja = 0
        # (si no hubo variante/PLA, cost_pla y cost_caja siguen en 0)

    packaging_units = _get_packaging_unit_costs()
    cost_empaque = packaging_units['caja_carton'] + packaging_units['bolsa_ecommerce']

    # Troqueles: costo fijo por cajita (aplica a con luz y sin luz)
    cost_troqueles = float(cost_data.get('cost_troqueles_por_cajita') or 0)

    # Redondear hacia arriba, sin decimales (igual que en el front)
    cost_caja_int = int(math.ceil(cost_caja))
    cost_pla_int = int(math.ceil(cost_pla))
    cost_empaque_int = int(math.ceil(cost_empaque))
    cost_troqueles_int = int(math.ceil(cost_troqueles))
    total = cost_caja_int + cost_pla_int + cost_empaque_int + cost_troqueles_int
    return {
        'cost_caja': cost_caja_int,
        'cost_pla': cost_pla_int,
        'cost_empaque': cost_empaque_int,
        'cost_troqueles': cost_troqueles_int,
        'total': total,
    }


def _compute_order_price_snapshot(order):
    """Precio de venta al finalizar (desde SiteSettings) para estadísticas."""
    site = get_settings()
    if order.box_type == BoxType.WITH_LIGHT:
        precio = (site.price_con_luz or 0) + (site.price_pilas or 0)
    else:
        precio = site.price_sin_luz or 0
    return {'precio_venta': float(precio)}


def _notify_n8n_new_order(order):
    """POST to n8n webhook when order goes IN_PROGRESS (WhatsApp/Telegram). No-op if N8N_WEBHOOK_URL not set."""
    url = getattr(settings, 'N8N_WEBHOOK_URL', None)
    logger.info('n8n notify order %s: N8N_WEBHOOK_URL=%s', order.id, 'SET' if url else 'NOT SET')
    if not url:
        logger.warning('n8n notify order %s: skipped (N8N_WEBHOOK_URL not configured)', order.id)
        return
    order.refresh_from_db()
    payload = {
        'order_id': order.id,
        'client_name': order.client_name or '',
        'phone': order.phone or '',
        'box_type': order.box_type or '',
        'led_type': order.led_type or '',
        'variant': order.variant or '',
        'shipping_option': order.shipping_option or '',
        'status': order.status,
        'created_at': order.created_at.isoformat() if order.created_at else None,
    }
    logger.info('n8n payload for order %s: %s', order.id, payload)
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        logger.info('n8n notify order %s: POST %s', order.id, url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8', errors='replace') if resp else ''
            logger.info('n8n notify order %s: response %s %s', order.id, resp.status, body[:200] if body else '')
            if resp.status not in (200, 201):
                logger.warning('n8n webhook returned status %s for order %s', resp.status, order.id)
    except urllib.error.URLError as e:
        logger.warning('n8n webhook failed for order %s: %s', order.id, e)
    except Exception as e:
        logger.exception('n8n webhook error for order %s: %s', order.id, e)


def _notify_n8n_order_finalized(order):
    """
    POST to n8n webhook when order goes to Finalized (processing).
    Sends first_name, phone, saldo_pendiente for WhatsApp to client.
    Saldo = precio total del tipo de cajita - seña (seña = mitad: con luz (con_luz+pilas)/2, sin luz sin_luz/2).
    """
    logger.info('n8n order finalized: start order_id=%s', order.id)
    url = getattr(settings, 'N8N_WEBHOOK_FINALIZED_URL', None)
    if not url:
        logger.warning('n8n order finalized %s: skipped (N8N_WEBHOOK_FINALIZED_URL not set)', order.id)
        return
    logger.info('n8n order finalized %s: POST url=%s', order.id, url)
    order.refresh_from_db()
    first_name = (order.client_name or '').strip().split()[0] or 'Cliente'
    raw_phone = (order.phone or '').strip()
    if not raw_phone:
        logger.warning('n8n order finalized %s: no phone, skip webhook', order.id)
        return
    # Normalize phone to E.164 for Twilio (Argentina: 10 digits -> +549...; 11 with leading 0 -> strip 0 then +549)
    digits = ''.join(c for c in raw_phone if c.isdigit())
    if raw_phone.startswith('+'):
        phone = raw_phone
    elif len(digits) == 11 and digits.startswith('0'):
        phone = '+549' + digits[1:]
    elif len(digits) == 10:
        phone = '+549' + digits
    elif digits:
        phone = '+' + digits
    else:
        phone = raw_phone
    logger.info('n8n order finalized %s: phone raw=%r normalized=%s', order.id, raw_phone, phone)
    try:
        site = get_settings()
        if order.box_type == BoxType.WITH_LIGHT:
            total = (site.price_con_luz or 0) + (site.price_pilas or 0)
        else:
            total = site.price_sin_luz or 0
        senia = total // 2
        saldo_pendiente = total - senia
    except Exception as e:
        logger.warning('n8n order finalized %s: could not get prices: %s', order.id, e)
        saldo_pendiente = 0
    # Formato Argentina: miles con punto (22.250)
    saldo_formatted = f'{saldo_pendiente:,}'.replace(',', '.')
    payload = {
        'order_id': order.id,
        'first_name': first_name,
        'phone': phone,
        'saldo_pendiente': saldo_pendiente,
        'saldo_pendiente_formatted': saldo_formatted,
    }
    logger.info('n8n order finalized payload for %s: %s', order.id, payload)
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        logger.info('n8n order finalized %s: sending POST body=%s', order.id, data.decode('utf-8'))
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8', errors='replace') if resp else ''
            logger.info('n8n order finalized %s: response status=%s body=%s', order.id, resp.status, body[:500] if body else '')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace') if e.fp else ''
        logger.warning(
            'n8n finalized webhook HTTP error for order %s: code=%s reason=%s body=%s',
            order.id, e.code, e.reason, body[:500] if body else '',
        )
    except urllib.error.URLError as e:
        logger.warning('n8n finalized webhook URLError for order %s: reason=%s err=%s', order.id, getattr(e, 'reason', None), e)
    except Exception as e:
        logger.exception('n8n finalized webhook error for order %s: %s', order.id, e)


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD for orders. List/retrieve require auth; create can be AllowAny for public flow."""
    queryset = Order.objects.all()
    parser_classes = (MultiPartParser, JSONParser)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            if self.request.query_params.get('include_hidden') != '1':
                qs = qs.filter(active=True)
            qs = qs.order_by('-id')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ('create', 'retrieve', 'update', 'partial_update', 'send_order', 'submit_images'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save(session_key=self.request.session.session_key)
        send_orders_update()

    def perform_update(self, serializer):
        instance = serializer.instance
        old_status = instance.status
        serializer.save()
        new_status = instance.status
        will_notify = old_status != OrderStatus.PROCESSING and new_status == OrderStatus.PROCESSING
        logger.info(
            'order perform_update id=%s old_status=%s new_status=%s will_notify_finalized=%s',
            instance.id, old_status, new_status, will_notify,
        )
        if not will_notify and new_status != OrderStatus.PROCESSING:
            logger.debug('order id=%s: no finalized webhook (new_status=%s, need processing)', instance.id, new_status)
        if will_notify:
            logger.info('order id=%s: calling _notify_n8n_order_finalized', instance.id)
            _notify_n8n_order_finalized(instance)
            # Descontar 1 caja de cartón y 1 bolsa ecommerce por pedido finalizado.
            for item_type in (PackagingStock.CAJA_CARTON, PackagingStock.BOLSA_ECOMMERCE):
                try:
                    stock = PackagingStock.objects.get(item_type=item_type)
                    if stock.quantity > 0:
                        stock.quantity -= 1
                        stock.save(update_fields=['quantity'])
                        logger.info('order id=%s: packaging %s decremented to %s', instance.id, item_type, stock.quantity)
                    else:
                        logger.warning('order id=%s: packaging %s already 0, not decremented', instance.id, item_type)
                except PackagingStock.DoesNotExist:
                    pass
            # Snapshot de costos y precio de venta (no se recalculan si después cambian precios/PLA).
            try:
                instance.cost_snapshot = _compute_order_cost_snapshot(instance)
                instance.price_snapshot = _compute_order_price_snapshot(instance)
                instance.save(update_fields=['cost_snapshot', 'price_snapshot'])
                logger.info('order id=%s: cost_snapshot total=%s price_snapshot=%s', instance.id, instance.cost_snapshot.get('total'), instance.price_snapshot.get('precio_venta'))
            except Exception as e:
                logger.warning('order id=%s: could not save cost/price snapshot: %s', instance.id, e)
        send_orders_update()
        send_stock_update()

    def perform_destroy(self, instance):
        instance.delete()
        send_orders_update()
        send_stock_update()

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def send_order(self, request, pk=None):
        """Set order to In Progress, generate QR code, and optionally trigger n8n webhook."""
        order = self.get_object()
        order.status = OrderStatus.IN_PROGRESS

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
        variant_display = (order.get_variant_display() or order.variant or '').strip()
        with_light = order.box_type == BoxType.WITH_LIGHT
        # status='in_progress' so front shows bell notification (In Progress only)
        send_orders_update(
            order_id=order.id,
            client_name=order.client_name or '',
            variant=variant_display,
            with_light=with_light,
            status=order.status,
        )
        send_stock_update()
        logger.info('send_order: calling n8n webhook for order %s', order.id)
        _notify_n8n_new_order(order)
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

        # Create or update ImageCrop for each slot: apply crop (exact position sent),
        # resize to 685x685, export PNG at 300 DPI
        CROP_OUTPUT_SIZE = 685
        CROP_OUTPUT_DPI = (300, 300)

        for i, data in enumerate(images_data):
            img_file = data['file']
            crop_data = data['crop_data']
            x = int(crop_data.get('x', 0))
            y = int(crop_data.get('y', 0))
            w = int(crop_data.get('width') or crop_data.get('w', 0))
            h = int(crop_data.get('height') or crop_data.get('h', 0))

            img = Image.open(img_file).convert('RGB')
            img_w, img_h = img.size
            # Clamp crop to image bounds (position unchanged, only clamp to edges)
            left = max(0, min(x, img_w - 1))
            top = max(0, min(y, img_h - 1))
            right = max(left + 1, min(x + w, img_w))
            bottom = max(top + 1, min(y + h, img_h))
            cropped = img.crop((left, top, right, bottom))
            resized = cropped.resize((CROP_OUTPUT_SIZE, CROP_OUTPUT_SIZE), Image.LANCZOS)

            buffer = io.BytesIO()
            resized.save(buffer, format='PNG', dpi=CROP_OUTPUT_DPI)
            buffer.seek(0)
            name = getattr(img_file, 'name', f'crop_{i}.png') or f'crop_{i}.png'
            if not name.lower().endswith('.png'):
                name = f'{name.rsplit(".", 1)[0] if "." in name else name}_crop.png'

            obj, created = ImageCrop.objects.update_or_create(
                order=order,
                slot=i,
                defaults={
                    'display_order': i,
                    'crop_data': crop_data,
                }
            )
            obj.image.save(name, ContentFile(buffer.read()), save=True)

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


class StockViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Stock por variante (4 variantes). List requiere auth; add_stock suma cantidad."""
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def list(self, request):
        for v in STOCK_VARIANTS:
            Stock.objects.get_or_create(variant=v, defaults={'quantity': 0})
        items = Stock.objects.filter(variant__in=STOCK_VARIANTS).order_by('variant')
        return Response(StockSerializer(items, many=True).data)

    @action(detail=False, methods=['post'])
    def add_stock(self, request):
        variant = request.data.get('variant')
        amount = request.data.get('amount', 0)
        if variant not in STOCK_VARIANTS:
            return Response(
                {'error': f'variant must be one of: {STOCK_VARIANTS}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            amount = int(amount)
            if amount < 0:
                return Response({'error': 'amount must be >= 0'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'amount must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        stock, _ = Stock.objects.get_or_create(variant=variant, defaults={'quantity': 0})
        stock.quantity += amount
        stock.save()
        send_stock_update()
        send_orders_update()
        return Response(StockSerializer(stock).data)

    @action(detail=False, methods=['post'])
    def set_stock(self, request):
        """Fija el stock físico de una variante (reemplaza el valor actual)."""
        variant = request.data.get('variant')
        quantity = request.data.get('quantity', 0)
        if variant not in STOCK_VARIANTS:
            return Response(
                {'error': f'variant must be one of: {STOCK_VARIANTS}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            quantity = int(quantity)
            if quantity < 0:
                return Response({'error': 'quantity must be >= 0'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'quantity must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        stock, _ = Stock.objects.get_or_create(variant=variant, defaults={'quantity': 0})
        stock.quantity = quantity
        stock.save()
        send_stock_update()
        send_orders_update()
        return Response(StockSerializer(stock).data)


class PackagingStockViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Stock de cajas de cartón y bolsas ecommerce. Se descuenta al finalizar pedidos."""
    permission_classes = [IsAuthenticated]
    serializer_class = PackagingStockSerializer
    queryset = PackagingStock.objects.all()

    def list(self, request, *args, **kwargs):
        # Asegurar que existan ambos tipos
        for item_type in (PackagingStock.CAJA_CARTON, PackagingStock.BOLSA_ECOMMERCE):
            PackagingStock.objects.get_or_create(item_type=item_type, defaults={'quantity': 0})
        return super().list(request, *args, **kwargs)


class PurchaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List, create, update and delete purchases/expenses (including PLA rolls)."""
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseSerializer
    queryset = Purchase.objects.all()


STATUS_VENTA = [OrderStatus.PROCESSING, OrderStatus.DELIVERED]


def _precio_venta_for_order(order):
    """Precio de venta: price_snapshot si existe, sino desde SiteSettings actual."""
    if order.price_snapshot and 'precio_venta' in order.price_snapshot:
        return float(order.price_snapshot['precio_venta'])
    site = get_settings()
    if order.box_type == BoxType.WITH_LIGHT:
        return float((site.price_con_luz or 0) + (site.price_pilas or 0))
    return float(site.price_sin_luz or 0)


def _costo_prod_for_order(order):
    """Costo de producción desde cost_snapshot."""
    if not order.cost_snapshot or 'total' not in order.cost_snapshot:
        return 0.0
    return float(order.cost_snapshot['total'])


class EstadisticasView(APIView):
    """
    GET: estadísticas para la sección Estadísticas del admin.
    Query params: days=30, months=12.
    Devuelve sales_by_day, sales_by_month, summary (cantidad_ventas, total_ventas, total_costos),
    detail (lista de ventas con id, date, box_type, precio_venta, costo_prod, margen).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = min(365, max(1, int(request.query_params.get('days', 30))))
        months = min(24, max(1, int(request.query_params.get('months', 12))))

        since_date = timezone.now().date() - timezone.timedelta(days=days)
        ventas_qs = (
            Order.objects.filter(status__in=STATUS_VENTA, updated_at__date__gte=since_date)
            .order_by('-updated_at')
        )
        ventas_list = list(ventas_qs)

        # Ventas por día (últimos N días)
        per_day = (
            Order.objects.filter(status__in=STATUS_VENTA, updated_at__date__gte=since_date)
            .annotate(day=TruncDate('updated_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        day_map = {str(item['day']): item['count'] for item in per_day if item['day']}
        sales_by_day = []
        for i in range(days):
            d = timezone.now().date() - timezone.timedelta(days=days - 1 - i)
            key = d.isoformat()
            sales_by_day.append({'date': key, 'count': day_map.get(key, 0)})

        # Ventas por mes (últimos N meses)
        per_month = (
            Order.objects.filter(status__in=STATUS_VENTA)
            .annotate(month=TruncMonth('updated_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        month_map = {}
        for item in per_month:
            if item['month']:
                key = item['month'].strftime('%Y-%m')
                month_map[key] = item['count']
        sales_by_month = []
        today = timezone.now().date()
        for i in range(months):
            offset = months - 1 - i  # 0 = mes actual, 1 = hace un mes, ...
            y, m = today.year, today.month - offset
            while m <= 0:
                m += 12
                y -= 1
            key = f'{y}-{m:02d}'
            sales_by_month.append({'month': key, 'count': month_map.get(key, 0)})

        total_ventas = sum(_precio_venta_for_order(o) for o in ventas_list)
        total_costos = sum(_costo_prod_for_order(o) for o in ventas_list)

        def _int_cost(x):
            """Valor de costo como entero (snapshot ya viene redondeado hacia arriba)."""
            v = float(x) if x is not None else 0
            return int(round(v))

        detail = []
        for o in ventas_list:
            precio = _precio_venta_for_order(o)
            costo = _costo_prod_for_order(o)
            snap = o.cost_snapshot or {}
            detail.append({
                'id': o.id,
                'date': (o.updated_at or o.created_at).isoformat() if (o.updated_at or o.created_at) else None,
                'box_type': o.box_type or '',
                'precio_venta': _int_cost(precio),
                'costo_prod': _int_cost(costo),
                'margen': _int_cost(precio - costo),
                'cost_breakdown': {
                    'cost_caja': _int_cost(snap.get('cost_caja')),
                    'cost_pla': _int_cost(snap.get('cost_pla')),
                    'cost_empaque': _int_cost(snap.get('cost_empaque')),
                    'cost_troqueles': _int_cost(snap.get('cost_troqueles')),
                } if snap else None,
            })

        return Response({
            'sales_by_day': sales_by_day,
            'sales_by_month': sales_by_month,
            'summary': {
                'cantidad_ventas': len(ventas_list),
                'total_ventas': _int_cost(total_ventas),
                'total_costos': _int_cost(total_costos),
            },
            'detail': detail,
        })
