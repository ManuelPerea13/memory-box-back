from django.urls import path
from .views import CostSettingsView

urlpatterns = [
    path('costs/', CostSettingsView.as_view(), name='expenses-cost-settings'),
]
