from django.contrib import admin
from .models import CostSettings, Purchase


@admin.register(CostSettings)
class CostSettingsAdmin(admin.ModelAdmin):
    list_display = ('id',)
    list_display_links = None

    def has_add_permission(self, request):
        return not CostSettings.objects.exists()


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'variant', 'brand', 'date', 'quantity',
        'grams_per_roll', 'unit_cost', 'total_cost', 'days', 'created_at',
    )
    list_filter = ('category', 'date')
    search_fields = ('notes', 'variant', 'brand')
    ordering = ('-date', '-id')
