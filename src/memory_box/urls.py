from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.views import CustomTokenObtainPairViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Memory Box API",
        default_version='v1',
        description="API for orders and image editor",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

api_patterns = [
    path('api-token-auth/', CustomTokenObtainPairViewSet.as_view(), name='token_obtain_pair'),
    path('', include('orders.urls')),
    path('settings/', include('config.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    path('docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
