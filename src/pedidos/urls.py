from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, RecorteImagenViewSet

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'recortes', RecorteImagenViewSet, basename='recorte')

urlpatterns = [
    path('', include(router.urls)),
]
