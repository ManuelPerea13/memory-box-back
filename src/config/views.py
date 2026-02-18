from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import SiteSettings
from .serializers import SiteSettingsSerializer


def get_settings():
    """Devuelve la única instancia de SiteSettings (crea con valores por defecto si no existe)."""
    obj, _ = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            'price_mercadolibre': 35000,
            'price_sin_luz': 24000,
            'price_con_luz': 42000,
            'price_pilas': 2500,
            'deposit_amount': 12000,
            'transfer_alias': 'manu.perea13',
            'transfer_bank': 'Mercado Pago',
            'transfer_holder': 'Manuel Perea',
            'contact_whatsapp': '+54 9 351 392 3790',
            'contact_email': 'copiiworld@gmail.com',
            'link_mercadolibre': 'https://mercadolibre.com',
        }
    )
    return obj


class PricesSettingsView(APIView):
    """
    GET: devuelve precios y datos de pago (público para Home y modal de pedido).
    PATCH: actualiza (requiere autenticación).
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        obj = get_settings()
        return Response(SiteSettingsSerializer(obj).data)

    def patch(self, request):
        obj = get_settings()
        serializer = SiteSettingsSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
