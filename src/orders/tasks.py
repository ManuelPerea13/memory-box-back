import logging

from celery import shared_task

from .models import Order

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def notify_n8n_new_order_task(self, order_id):
    """Notifica a n8n (nuevo pedido In Progress) de forma asíncrona.

    Reintenta hasta 3 veces si el webhook falla. La lógica del POST vive en
    orders.views._notify_n8n_new_order (importada acá para evitar import circular).
    """
    from .views import _notify_n8n_new_order

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning('notify_n8n_new_order_task: order %s no existe', order_id)
        return
    _notify_n8n_new_order(order)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def notify_n8n_order_finalized_task(self, order_id):
    """Notifica a n8n (pedido finalizado) de forma asíncrona."""
    from .views import _notify_n8n_order_finalized

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning('notify_n8n_order_finalized_task: order %s no existe', order_id)
        return
    _notify_n8n_order_finalized(order)


@shared_task(bind=True)
def process_order_images_task(self, order_id, items):
    """Procesa (recorta + redimensiona a cuadrado) las imágenes de un pedido.

    Corre en el worker para no bloquear la respuesta HTTP. `items` es una lista de
    dicts JSON-serializables: {'slot', 'path' (archivo temporal en MEDIA), 'crop_norm', 'name'}.
    Reporta progreso vía update_state(meta={'done', 'total'}).
    """
    import io
    import os

    from PIL import Image, ImageOps
    from django.core.files.base import ContentFile

    from .models import ImageCrop
    from .views import CROP_OUTPUT_PX, CROP_OUTPUT_DPI
    from .websocket_utils import send_orders_update, send_stock_update

    total = len(items)
    self.update_state(state='PROGRESS', meta={'done': 0, 'total': total})

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning('process_order_images_task: order %s no existe', order_id)
        return {'error': 'order no existe', 'done': 0, 'total': total}

    cleanup_paths = []
    for idx, item in enumerate(items):
        slot = item['slot']
        path = item['path']
        norm = item['crop_norm']
        name = item.get('name') or f'crop_{slot}.png'
        cleanup_paths.append(path)

        x, y, w, h = norm['x'], norm['y'], norm['width'], norm['height']
        with open(path, 'rb') as fh:
            img = Image.open(fh)
            img.load()
        img = img.convert('RGB')
        img = ImageOps.exif_transpose(img)
        img_w, img_h = img.size
        left = max(0, min(x, img_w - 1))
        top = max(0, min(y, img_h - 1))
        right = max(left + 1, min(x + w, img_w))
        bottom = max(top + 1, min(y + h, img_h))
        cropped = img.crop((left, top, right, bottom))
        cw, ch = cropped.size

        if cw > 0 and ch > 0:
            # reducing_gap acelera mucho el downscale grande→685 con LANCZOS sin pérdida visible.
            final = cropped.resize((CROP_OUTPUT_PX, CROP_OUTPUT_PX), Image.LANCZOS, reducing_gap=2.0)
        else:
            final = Image.new('RGB', (CROP_OUTPUT_PX, CROP_OUTPUT_PX), (0, 0, 0))

        buffer = io.BytesIO()
        # JPEG q95: ~13x más rápido de codificar que PNG y ~4x más chico para fotos,
        # conservando los 300 DPI. subsampling=0 (4:4:4) = sin pérdida de croma para impresión.
        final.save(buffer, format='JPEG', dpi=CROP_OUTPUT_DPI, quality=95, subsampling=0)
        buffer.seek(0)
        base = name.rsplit('.', 1)[0] if '.' in name else name
        name = f'{base}.jpg'

        obj, _ = ImageCrop.objects.update_or_create(
            order=order,
            slot=slot,
            defaults={'display_order': slot, 'crop_data': norm},
        )
        obj.image.save(name, ContentFile(buffer.read()), save=True)
        self.update_state(state='PROGRESS', meta={'done': idx + 1, 'total': total})

    # Limpiar archivos temporales subidos.
    for p in cleanup_paths:
        try:
            os.remove(p)
        except OSError:
            pass
    if cleanup_paths:
        d = os.path.dirname(cleanup_paths[0])
        try:
            if d and not os.listdir(d):
                os.rmdir(d)
        except OSError:
            pass

    send_orders_update()
    send_stock_update()
    logger.info('process_order_images_task: order %s procesadas %s imágenes', order_id, total)
    return {'done': total, 'total': total}
