from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import SiteSettings, BackgroundMedia, BoxVariant, BoxVariantImage
from .views import get_settings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'price_sin_luz', 'price_con_luz', 'price_pilas')
    fieldsets = (
        ('Prices', {
            'fields': (
                'price_mercadolibre', 'price_sin_luz', 'price_con_luz',
                'price_pilas',
            )
        }),
        ('Transfer', {
            'fields': ('transfer_alias', 'transfer_bank', 'transfer_holder')
        }),
        ('Contact', {
            'fields': ('contact_whatsapp', 'contact_email')
        }),
        ('Links', {
            'fields': ('link_mercadolibre',)
        }),
        ('Main page background (video & audio)', {
            'fields': ('video_sin_luz', 'video_con_luz', 'audio_sin_luz', 'audio_con_luz')
        }),
    )


@admin.register(BackgroundMedia)
class BackgroundMediaAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'source_display', 'used_as_display')
    list_filter = ('type',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('type', 'name', 'file', 'created_at')
        }),
    )
    actions = [
        'set_as_sin_luz_video',
        'set_as_con_luz_video',
        'set_as_sin_luz_audio',
        'set_as_con_luz_audio',
    ]

    def source_display(self, obj):
        return 'Uploaded file' if obj.file else '—'
    source_display.short_description = 'Source'

    def used_as_display(self, obj):
        url = (obj.url or '').strip()
        if not url:
            return '—'
        site = get_settings()
        labels = []
        if site.video_sin_luz and site.video_sin_luz.strip() == url:
            labels.append('No light video')
        if site.video_con_luz and site.video_con_luz.strip() == url:
            labels.append('With light video')
        if site.audio_sin_luz and site.audio_sin_luz.strip() == url:
            labels.append('No light audio')
        if site.audio_con_luz and site.audio_con_luz.strip() == url:
            labels.append('With light audio')
        return ', '.join(labels) if labels else '—'
    used_as_display.short_description = 'Used on main page'

    def set_as_sin_luz_video(self, request, queryset):
        videos = queryset.filter(type=BackgroundMedia.TYPE_VIDEO)
        if not videos.exists():
            self.message_user(request, 'Select at least one Video item.', messages.WARNING)
            return
        obj = videos.first()
        url = obj.url
        if not url:
            self.message_user(request, 'This item has no URL (upload a file or set external URL).', messages.ERROR)
            return
        site = get_settings()
        site.video_sin_luz = url
        site.save(update_fields=['video_sin_luz'])
        self.message_user(request, f'No light video updated: {obj.name}', messages.SUCCESS)
    set_as_sin_luz_video.short_description = 'Set as No light video on main page'

    def set_as_con_luz_video(self, request, queryset):
        videos = queryset.filter(type=BackgroundMedia.TYPE_VIDEO)
        if not videos.exists():
            self.message_user(request, 'Select at least one Video item.', messages.WARNING)
            return
        obj = videos.first()
        url = obj.url
        if not url:
            self.message_user(request, 'This item has no URL.', messages.ERROR)
            return
        site = get_settings()
        site.video_con_luz = url
        site.save(update_fields=['video_con_luz'])
        self.message_user(request, f'With light video updated: {obj.name}', messages.SUCCESS)
    set_as_con_luz_video.short_description = 'Set as With light video on main page'

    def set_as_sin_luz_audio(self, request, queryset):
        audios = queryset.filter(type=BackgroundMedia.TYPE_AUDIO)
        if not audios.exists():
            self.message_user(request, 'Select at least one Audio item.', messages.WARNING)
            return
        obj = audios.first()
        url = obj.url
        if not url:
            self.message_user(request, 'This item has no URL.', messages.ERROR)
            return
        site = get_settings()
        site.audio_sin_luz = url
        site.save(update_fields=['audio_sin_luz'])
        self.message_user(request, f'No light audio updated: {obj.name}', messages.SUCCESS)
    set_as_sin_luz_audio.short_description = 'Set as No light audio on main page'

    def set_as_con_luz_audio(self, request, queryset):
        audios = queryset.filter(type=BackgroundMedia.TYPE_AUDIO)
        if not audios.exists():
            self.message_user(request, 'Select at least one Audio item.', messages.WARNING)
            return
        obj = audios.first()
        url = obj.url
        if not url:
            self.message_user(request, 'This item has no URL.', messages.ERROR)
            return
        site = get_settings()
        site.audio_con_luz = url
        site.save(update_fields=['audio_con_luz'])
        self.message_user(request, f'With light audio updated: {obj.name}', messages.SUCCESS)
    set_as_con_luz_audio.short_description = 'Set as With light audio on main page'


class BoxVariantImageInline(admin.TabularInline):
    model = BoxVariantImage
    extra = 0
    fields = ('box_type', 'file', 'order')


@admin.register(BoxVariant)
class BoxVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'visible_no_light', 'visible_with_light', 'order')
    list_editable = ('visible_no_light', 'visible_with_light', 'order')
    inlines = [BoxVariantImageInline]


@admin.register(BoxVariantImage)
class BoxVariantImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'box_type', 'order', 'url_display')
    list_filter = ('variant', 'box_type')

    def url_display(self, obj):
        return obj.url or '—'
    url_display.short_description = 'URL'
