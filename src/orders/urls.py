from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ImageCropViewSet, StockViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'image-crops', ImageCropViewSet, basename='image-crop')
router.register(r'stock', StockViewSet, basename='stock')

urlpatterns = [
    path('', include(router.urls)),
]
