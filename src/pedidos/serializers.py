from rest_framework import serializers
from .models import Pedido, RecorteImagen, BoxType, LedType, Variant, ShippingOption


class RecorteImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecorteImagen
        fields = ['id', 'pedido', 'slot', 'orden', 'imagen', 'crop_data', 'creado']
        read_only_fields = ['creado']


class PedidoSerializer(serializers.ModelSerializer):
    recortes = RecorteImagenSerializer(many=True, read_only=True)
    box_type = serializers.ChoiceField(choices=BoxType.choices, required=False, allow_blank=True)
    led_type = serializers.ChoiceField(choices=LedType.choices, required=False, allow_blank=True)
    variant = serializers.ChoiceField(choices=Variant.choices, required=False, allow_blank=True)
    shipping_option = serializers.ChoiceField(choices=ShippingOption.choices, required=False, allow_blank=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'session_key', 'nombre_cliente', 'email', 'telefono',
            'direccion', 'notas', 'box_type', 'led_type', 'variant', 'shipping_option',
            'status', 'creado', 'actualizado', 'recortes'
        ]
        read_only_fields = ['creado', 'actualizado']


class PedidoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            'id', 'nombre_cliente', 'email', 'box_type', 'variant', 'status', 'creado', 'actualizado'
        ]
