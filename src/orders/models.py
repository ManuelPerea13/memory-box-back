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


class Order(models.Model):
    """Order (client data + status)."""
    # Ephemeral session/token to associate crops before submitting (optional)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    # Client data
    client_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} - {self.client_name}"


class ImageCrop(models.Model):
    """Image crop associated with an order (slot 0-9, display order)."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='image_crops')
    slot = models.PositiveSmallIntegerField(help_text='Slot index (0-9)')
    display_order = models.PositiveSmallIntegerField(default=0, help_text='Display order')
    image = models.ImageField(upload_to='crops/%Y/%m/%d/', blank=True, null=True)
    # Crop data in JSON (x, y, width, height, etc. per Cropper.js)
    crop_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'display_order', 'slot']
        unique_together = [['order', 'slot']]

    def __str__(self):
        return f"ImageCrop order={self.order_id} slot={self.slot}"
