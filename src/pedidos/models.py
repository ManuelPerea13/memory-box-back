from django.db import models


class BoxType(models.TextChoices):
    NO_LIGHT = 'no_light', 'No light'
    WITH_LIGHT = 'with_light', 'With light'


class LedType(models.TextChoices):
    WARM = 'warm_led', 'Warm LED'
    WHITE = 'white_led', 'White LED'


class Variant(models.TextChoices):
    # No light
    GRAPHITE = 'graphite', 'Graphite'
    WOOD = 'wood', 'Wood'
    BLACK = 'black', 'Black'
    MARBLE = 'marble', 'Marble'
    # With light
    GRAPHITE_LIGHT = 'graphite_light', 'Graphite (with light)'
    WOOD_LIGHT = 'wood_light', 'Wood (with light)'
    BLACK_LIGHT = 'black_light', 'Black (with light)'
    MARBLE_LIGHT = 'marble_light', 'Marble (with light)'


class ShippingOption(models.TextChoices):
    PICKUP_UBER = 'pickup_uber', 'Pickup / Uber'
    SHIPPING_PROVINCE = 'shipping_province', 'Shipping to other province'


class OrderStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SENT = 'sent', 'Sent'
    PROCESSING = 'processing', 'Processing'
    DELIVERED = 'delivered', 'Delivered'


class Pedido(models.Model):
    """Order (client data + status). API and DB use English; front displays in Spanish."""
    # Sesión/token efímero para asociar recortes antes de enviar (opcional)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    # Datos del cliente
    nombre_cliente = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    direccion = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    # Box options (from client form)
    box_type = models.CharField(
        max_length=20, blank=True, choices=BoxType.choices,
        help_text='no_light | with_light'
    )
    led_type = models.CharField(
        max_length=20, blank=True, choices=LedType.choices,
        help_text='Only if box_type=with_light'
    )
    variant = models.CharField(
        max_length=50, blank=True, choices=Variant.choices,
        help_text='graphite, wood, black, marble, *_light'
    )
    shipping_option = models.CharField(
        max_length=30, blank=True, choices=ShippingOption.choices,
        help_text='pickup_uber | shipping_province'
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"Pedido #{self.pk} - {self.nombre_cliente}"


class RecorteImagen(models.Model):
    """Un recorte de imagen asociado a un pedido (slot 0-9, orden, imagen)."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='recortes')
    slot = models.PositiveSmallIntegerField(help_text='Índice del slot (0-9)')
    orden = models.PositiveSmallIntegerField(default=0, help_text='Orden de visualización')
    imagen = models.ImageField(upload_to='recortes/%Y/%m/%d/', blank=True, null=True)
    # Datos del crop en JSON (x, y, width, height, etc. según Cropper.js)
    crop_data = models.JSONField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pedido', 'orden', 'slot']
        unique_together = [['pedido', 'slot']]

    def __str__(self):
        return f"Recorte pedido={self.pedido_id} slot={self.slot}"
