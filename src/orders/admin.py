from django.contrib import admin
from .models import Order, ImageCrop


class ImageCropInline(admin.TabularInline):
    model = ImageCrop
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('client_name', 'email')
    inlines = [ImageCropInline]


@admin.register(ImageCrop)
class ImageCropAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'slot', 'display_order', 'created_at')
    list_filter = ('order',)
