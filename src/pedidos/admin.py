from django.contrib import admin
from .models import Pedido, RecorteImagen


class RecorteImagenInline(admin.TabularInline):
    model = RecorteImagen
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email', 'status', 'creado')
    list_filter = ('status',)
    search_fields = ('nombre_cliente', 'email')
    inlines = [RecorteImagenInline]


@admin.register(RecorteImagen)
class RecorteImagenAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'slot', 'orden', 'creado')
    list_filter = ('pedido',)
