from django.urls import path
from .views import (
    PricesSettingsView,
    HomeBackgroundSettingsView,
    BackgroundMediaListCreateView,
    BackgroundMediaDetailView,
    VariantsPublicView,
    VariantsListView,
    VariantDetailView,
    VariantImageListCreateView,
    VariantImageDetailView,
)
from expenses.views import CostSettingsView

urlpatterns = [
    path('prices/', PricesSettingsView.as_view(), name='settings-prices'),
    path('costs/', CostSettingsView.as_view(), name='settings-costs'),
    path('home-background/', HomeBackgroundSettingsView.as_view(), name='settings-home-background'),
    path('background-media/', BackgroundMediaListCreateView.as_view(), name='settings-background-media-list'),
    path('background-media/<int:pk>/', BackgroundMediaDetailView.as_view(), name='settings-background-media-detail'),
    path('variants/public/', VariantsPublicView.as_view(), name='settings-variants-public'),
    path('variants/', VariantsListView.as_view(), name='settings-variants-list'),
    path('variants/<int:pk>/', VariantDetailView.as_view(), name='settings-variant-detail'),
    path('variant-images/', VariantImageListCreateView.as_view(), name='settings-variant-images-list'),
    path('variant-images/<int:pk>/', VariantImageDetailView.as_view(), name='settings-variant-images-detail'),
]
