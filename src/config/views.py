from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from .models import SiteSettings, BackgroundMedia, BoxVariant, BoxVariantImage
from .serializers import (
    SiteSettingsSerializer,
    HomeBackgroundSerializer,
    BackgroundMediaSerializer,
    BoxVariantSerializer,
    BoxVariantImageSerializer,
)


def get_settings():
    """Devuelve la única instancia de SiteSettings (crea con valores por defecto si no existe)."""
    obj, _ = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            'price_mercadolibre': 35000,
            'price_sin_luz': 24000,
            'price_con_luz': 42000,
            'price_pilas': 2500,
            'transfer_alias': 'manu.perea13',
            'transfer_bank': 'Mercado Pago',
            'transfer_holder': 'Manuel Perea',
            'contact_whatsapp': '+54 9 351 392 3790',
            'contact_email': 'copiiworld@gmail.com',
            'link_mercadolibre': 'https://mercadolibre.com',
        'video_sin_luz': '/static/videos/video-navidad.mp4',
        'video_con_luz': '/static/videos/background-video-2.mp4',
        'audio_sin_luz': '/static/audio/cancion-navidad.mp3',
        'audio_con_luz': '/static/audio/background-music-2.mp3',
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


class HomeBackgroundSettingsView(APIView):
    """
    GET: devuelve video y música de fondo de la página principal (público).
    PATCH: actualiza (requiere autenticación).
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        obj = get_settings()
        return Response(HomeBackgroundSerializer(obj).data)

    def patch(self, request):
        obj = get_settings()
        serializer = HomeBackgroundSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class BackgroundMediaListCreateView(APIView):
    """GET: lista de media (opcional ?type=video|audio). POST: crear (multipart o JSON)."""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        qs = BackgroundMedia.objects.all()
        type_filter = request.query_params.get('type', '').strip().lower()
        if type_filter in ('video', 'audio'):
            qs = qs.filter(type=type_filter)
        serializer = BackgroundMediaSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = {k: v for k, v in request.data.items() if k in ('type', 'name')}
        if request.FILES.get('file'):
            data['file'] = request.FILES['file']
        serializer = BackgroundMediaSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BackgroundMediaDetailView(APIView):
    """GET: detalle. PATCH: actualizar nombre y/o archivo."""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self, pk):
        return BackgroundMedia.objects.get(pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        return Response(BackgroundMediaSerializer(obj).data)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        data = {k: v for k, v in request.data.items() if k in ('name',)}
        if request.FILES.get('file'):
            data['file'] = request.FILES['file']
        serializer = BackgroundMediaSerializer(obj, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


def _build_variants_public():
    """Formato para el front: no_light y with_light por visibilidad por tipo."""
    all_variants = BoxVariant.objects.all().order_by('order', 'code')
    no_light = []
    with_light = []
    for v in all_variants:
        if v.visible_no_light:
            imgs_no = [img.url for img in v.images.filter(box_type=BoxVariantImage.BOX_TYPE_NO_LIGHT).order_by('order') if img.url]
            no_light.append({'id': v.code, 'name': v.name, 'images': imgs_no})
        if v.visible_with_light:
            imgs_light = [img.url for img in v.images.filter(box_type=BoxVariantImage.BOX_TYPE_WITH_LIGHT).order_by('order') if img.url]
            with_light.append({'id': f'{v.code}_light', 'name': v.name, 'images': imgs_light})
    return {'no_light': no_light, 'with_light': with_light}


class VariantsPublicView(APIView):
    """GET: variantes visibles con imágenes para la página de pedido (público)."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(_build_variants_public())


class VariantsListView(APIView):
    """GET: lista completa para admin. POST: crear nueva variante (code, name)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = BoxVariant.objects.all().order_by('order', 'code')
        return Response(BoxVariantSerializer(qs, many=True).data)

    def post(self, request):
        code = (request.data.get('code') or '').strip().lower().replace(' ', '_')
        name = (request.data.get('name') or '').strip()
        if not code:
            return Response({'code': ['Code is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not name:
            return Response({'name': ['Name is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if BoxVariant.objects.filter(code=code).exists():
            return Response({'code': ['A variant with this code already exists.']}, status=status.HTTP_400_BAD_REQUEST)
        order = BoxVariant.objects.count()
        obj = BoxVariant.objects.create(code=code, name=name, visible=True, order=order)
        return Response(BoxVariantSerializer(obj).data, status=status.HTTP_201_CREATED)


class VariantDetailView(APIView):
    """PATCH: update name, visible, visible_no_light, visible_with_light, order."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return BoxVariant.objects.get(pk=pk)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        allowed = ('name', 'visible', 'visible_no_light', 'visible_with_light', 'order')
        data = {k: v for k, v in request.data.items() if k in allowed}
        serializer = BoxVariantSerializer(obj, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(BoxVariantSerializer(obj).data)


class VariantImageListCreateView(APIView):
    """GET: imágenes de una variante (query ?variant_id=). POST: crear (multipart o JSON)."""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        variant_id = request.query_params.get('variant_id')
        if not variant_id:
            return Response({'detail': 'variant_id required'}, status=status.HTTP_400_BAD_REQUEST)
        qs = BoxVariantImage.objects.filter(variant_id=variant_id).order_by('box_type', 'order')
        return Response(BoxVariantImageSerializer(qs, many=True).data)

    def post(self, request):
        if not request.FILES.get('file'):
            return Response({'file': ['A file must be uploaded. External URL is not used.']}, status=status.HTTP_400_BAD_REQUEST)
        data = {k: v for k, v in request.data.items() if k in ('variant', 'box_type', 'order')}
        data['file'] = request.FILES['file']
        if 'order' not in data:
            data['order'] = 0
        serializer = BoxVariantImageSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VariantImageDetailView(APIView):
    """PATCH: update. DELETE: remove."""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self, pk):
        return BoxVariantImage.objects.get(pk=pk)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        data = {k: v for k, v in request.data.items() if k in ('box_type', 'order')}
        if request.FILES.get('file'):
            data['file'] = request.FILES['file']
        serializer = BoxVariantImageSerializer(obj, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


