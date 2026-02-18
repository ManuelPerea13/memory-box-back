from rest_framework import serializers
from .models import Order, ImageCrop, BoxType, LedType, Variant, ShippingOption, Stock, STOCK_VARIANTS


class ImageCropSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCrop
        fields = ['id', 'order', 'slot', 'display_order', 'image', 'crop_data', 'created_at']
        read_only_fields = ['created_at']


class OrderSerializer(serializers.ModelSerializer):
    image_crops = ImageCropSerializer(many=True, read_only=True)
    box_type = serializers.ChoiceField(choices=BoxType.choices, required=False, allow_blank=True)
    led_type = serializers.ChoiceField(choices=LedType.choices, required=False, allow_blank=True)
    variant = serializers.ChoiceField(choices=Variant.choices, required=False, allow_blank=True)
    shipping_option = serializers.ChoiceField(choices=ShippingOption.choices, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            'id', 'session_key', 'client_name', 'phone',
            'box_type', 'led_type', 'variant', 'shipping_option',
            'status', 'deposit', 'active', 'qr_code', 'created_at', 'updated_at', 'image_crops'
        ]
        read_only_fields = ['created_at', 'updated_at', 'qr_code']


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'client_name', 'phone', 'box_type', 'led_type', 'variant',
            'shipping_option', 'status', 'deposit', 'active', 'created_at', 'updated_at'
        ]


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'variant', 'quantity']
        read_only_fields = ['variant']
