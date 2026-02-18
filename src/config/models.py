from django.db import models


class SiteSettings(models.Model):
    """
    Configuración única del sitio: precios, seña, datos de transferencia y contacto.
    Solo debe existir una fila (singleton); se usa id=1.
    """
    # Precios
    price_mercadolibre = models.PositiveIntegerField(default=35000)
    price_sin_luz = models.PositiveIntegerField(default=24000)
    price_con_luz = models.PositiveIntegerField(default=42000)
    price_pilas = models.PositiveIntegerField(default=2500)
    deposit_amount = models.PositiveIntegerField(default=12000)
    # Transferencia
    transfer_alias = models.CharField(max_length=100, default='manu.perea13')
    transfer_bank = models.CharField(max_length=100, default='Mercado Pago')
    transfer_holder = models.CharField(max_length=200, default='Manuel Perea')
    # Contacto
    contact_whatsapp = models.CharField(max_length=50, default='+54 9 351 392 3790')
    contact_email = models.CharField(max_length=254, default='copiiworld@gmail.com')
    link_mercadolibre = models.URLField(max_length=500, blank=True)

    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'

    def __str__(self):
        return 'Configuración precios y datos de pago'
