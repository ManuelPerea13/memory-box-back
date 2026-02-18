from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'price_sin_luz', 'price_con_luz', 'price_pilas')
    fieldsets = (
        ('Precios', {
            'fields': (
                'price_mercadolibre', 'price_sin_luz', 'price_con_luz',
                'price_pilas',
            )
        }),
        ('Transferencia', {
            'fields': ('transfer_alias', 'transfer_bank', 'transfer_holder')
        }),
        ('Contacto', {
            'fields': ('contact_whatsapp', 'contact_email')
        }),
        ('Enlaces', {
            'fields': ('link_mercadolibre',)
        }),
    )
