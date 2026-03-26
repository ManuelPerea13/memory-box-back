from django.db import models


class SiteSettings(models.Model):
    """
    Single site configuration: prices, deposit, transfer and contact data (client-facing).
    Singleton: only one row, use id=1.
    """
    # Prices
    price_mercadolibre = models.PositiveIntegerField(default=35000)
    price_sin_luz = models.PositiveIntegerField(default=24000)
    price_con_luz = models.PositiveIntegerField(default=42000)
    price_pilas = models.PositiveIntegerField(default=2500)
    # Transfer
    transfer_alias = models.CharField(max_length=100, default='manu.perea13')
    transfer_bank = models.CharField(max_length=100, default='Mercado Pago')
    transfer_holder = models.CharField(max_length=200, default='Manuel Perea')
    # Contact
    contact_whatsapp = models.CharField(max_length=50, default='+54 9 351 392 3790')
    contact_email = models.CharField(max_length=254, default='copiiworld@gmail.com')
    link_mercadolibre = models.URLField(max_length=500, blank=True)
    # Main page background video/audio (paths or URLs)
    video_sin_luz = models.CharField(max_length=500, default='/static/videos/video-navidad.mp4', blank=True)
    video_con_luz = models.CharField(max_length=500, default='/static/videos/background-video-2.mp4', blank=True)
    audio_sin_luz = models.CharField(max_length=500, default='/static/audio/cancion-navidad.mp3', blank=True)
    audio_con_luz = models.CharField(max_length=500, default='/static/audio/background-music-2.mp3', blank=True)

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return 'Prices and payment details'


class BackgroundMedia(models.Model):
    """
    Video (MP4) and audio (MP3) files for the main page background.
    Uses the uploaded file only.
    """
    TYPE_VIDEO = 'video'
    TYPE_AUDIO = 'audio'
    TYPE_CHOICES = [
        (TYPE_VIDEO, 'Video (MP4)'),
        (TYPE_AUDIO, 'Audio (MP3)'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200, help_text='Name to identify in admin')
    file = models.FileField(
        upload_to='background_media/%Y/%m/',
        blank=True,
        null=True,
        help_text='Upload MP4 or MP3 file.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Background media'
        verbose_name_plural = 'Background media'
        ordering = ['type', 'name']

    def __str__(self):
        return f'{self.get_type_display()}: {self.name}'

    @property
    def url(self):
        """URL of the uploaded file."""
        return self.file.url if self.file else None


class BoxVariant(models.Model):
    """
    Box variant (client-facing catalog). Defines name, code (slug) and visibility on front.
    Visibility per box type: No light and With light separately.
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    visible = models.BooleanField(default=True, help_text='Legacy: used if per-type visibility is not used')
    visible_no_light = models.BooleanField(default=True, help_text='Show on order page (No light type)')
    visible_with_light = models.BooleanField(default=True, help_text='Show on order page (With light type)')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Box variant'
        verbose_name_plural = 'Box variants'
        ordering = ['order', 'code']

    def __str__(self):
        return f'{self.name} ({self.code})'


class BoxVariantImage(models.Model):
    """Image for a variant for No light or With light type. Multiple images per variant/type (gallery)."""
    BOX_TYPE_NO_LIGHT = 'no_light'
    BOX_TYPE_WITH_LIGHT = 'with_light'
    BOX_TYPE_CHOICES = [
        (BOX_TYPE_NO_LIGHT, 'No light'),
        (BOX_TYPE_WITH_LIGHT, 'With light'),
    ]
    variant = models.ForeignKey(BoxVariant, on_delete=models.CASCADE, related_name='images')
    box_type = models.CharField(max_length=20, choices=BOX_TYPE_CHOICES)
    file = models.ImageField(
        upload_to='variant_images/%Y/%m/',
        blank=True,
        null=True,
    )
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Box variant image'
        verbose_name_plural = 'Box variant images'
        ordering = ['variant', 'box_type', 'order']

    @property
    def url(self):
        return self.file.url if self.file else None

