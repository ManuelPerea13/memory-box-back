from rest_framework import serializers
from .models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'price_mercadolibre',
            'price_sin_luz',
            'price_con_luz',
            'price_pilas',
            'deposit_amount',
            'transfer_alias',
            'transfer_bank',
            'transfer_holder',
            'contact_whatsapp',
            'contact_email',
            'link_mercadolibre',
        ]
