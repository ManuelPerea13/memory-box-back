from django.urls import path
from .views import PricesSettingsView

urlpatterns = [
    path('prices/', PricesSettingsView.as_view(), name='settings-prices'),
]
