from rest_framework import serializers
from .models import SiteSettings, BackgroundMedia, BoxVariant, BoxVariantImage


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'price_mercadolibre',
            'price_sin_luz',
            'price_con_luz',
            'price_pilas',
            'transfer_alias',
            'transfer_bank',
            'transfer_holder',
            'contact_whatsapp',
            'contact_email',
            'link_mercadolibre',
        ]


class HomeBackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'video_sin_luz',
            'video_con_luz',
            'audio_sin_luz',
            'audio_con_luz',
        ]


class BackgroundMediaSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = BackgroundMedia
        fields = ['id', 'type', 'name', 'file', 'url', 'created_at']
        read_only_fields = ['url', 'created_at']

    def get_url(self, obj):
        return obj.url


class BoxVariantImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = BoxVariantImage
        fields = ['id', 'variant', 'box_type', 'file', 'url', 'order', 'created_at']
        read_only_fields = ['url', 'created_at']

    def get_url(self, obj):
        return obj.url


class BoxVariantSerializer(serializers.ModelSerializer):
    images_no_light = serializers.SerializerMethodField()
    images_with_light = serializers.SerializerMethodField()

    class Meta:
        model = BoxVariant
        fields = [
            'id', 'code', 'name', 'visible', 'visible_no_light', 'visible_with_light',
            'order', 'images_no_light', 'images_with_light',
        ]

    def get_images_no_light(self, obj):
        return [{'id': img.id, 'url': img.url} for img in obj.images.filter(box_type=BoxVariantImage.BOX_TYPE_NO_LIGHT).order_by('order') if img.url]

    def get_images_with_light(self, obj):
        return [{'id': img.id, 'url': img.url} for img in obj.images.filter(box_type=BoxVariantImage.BOX_TYPE_WITH_LIGHT).order_by('order') if img.url]
