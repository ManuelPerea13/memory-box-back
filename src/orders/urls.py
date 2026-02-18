from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ImageCropViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'image-crops', ImageCropViewSet, basename='image-crop')

urlpatterns = [
    path('', include(router.urls)),
]
