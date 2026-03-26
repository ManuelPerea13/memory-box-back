from rest_framework import serializers
from .models import (
    Order, ImageCrop, BoxType, LedType, ShippingOption, Stock, STOCK_VARIANTS,
    PackagingStock,
)
from expenses.models import Purchase, PurchaseCategory


class ImageCropSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCrop
        fields = ['id', 'order', 'slot', 'display_order', 'image', 'crop_data', 'created_at']
        read_only_fields = ['created_at']


class OrderSerializer(serializers.ModelSerializer):
    image_crops = ImageCropSerializer(many=True, read_only=True)
    box_type = serializers.ChoiceField(choices=BoxType.choices, required=False, allow_blank=True)
    led_type = serializers.ChoiceField(choices=LedType.choices, required=False, allow_blank=True)
    variant = serializers.CharField(max_length=50, required=False, allow_blank=True)
    shipping_option = serializers.ChoiceField(choices=ShippingOption.choices, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            'id', 'session_key', 'client_name', 'phone',
            'box_type', 'led_type', 'variant', 'shipping_option',
            'status', 'deposit', 'active', 'qr_code', 'cost_snapshot', 'price_snapshot',
            'created_at', 'updated_at', 'image_crops'
        ]
        read_only_fields = ['created_at', 'updated_at', 'qr_code', 'cost_snapshot', 'price_snapshot']


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'client_name', 'phone', 'box_type', 'led_type', 'variant',
            'shipping_option', 'status', 'deposit', 'active', 'cost_snapshot', 'price_snapshot',
            'created_at', 'updated_at'
        ]


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'variant', 'box_type', 'quantity']
        read_only_fields = ['variant', 'box_type']


class PackagingStockSerializer(serializers.ModelSerializer):
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)

    class Meta:
        model = PackagingStock
        fields = ['id', 'item_type', 'item_type_display', 'quantity']


class PurchaseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'category', 'category_display', 'date', 'quantity',
            'unit_cost', 'total_cost', 'days', 'notes', 'created_at',
            'variant', 'brand', 'grams_per_roll',
        ]
