from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, ImageCropViewSet, StockViewSet,
    PackagingStockViewSet, PurchaseViewSet,
    EstadisticasView,
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'image-crops', ImageCropViewSet, basename='image-crop')
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'packaging', PackagingStockViewSet, basename='packaging')
router.register(r'purchases', PurchaseViewSet, basename='purchase')

urlpatterns = [
    path('estadisticas/', EstadisticasView.as_view(), name='estadisticas'),
    path('', include(router.urls)),
]
