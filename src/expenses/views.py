from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CostSettings


def get_cost_settings():
    """Return the single CostSettings instance (create if missing)."""
    obj, _ = CostSettings.objects.get_or_create(pk=1, defaults={'data': {}})
    return obj


class CostSettingsView(APIView):
    """
    GET: return reference costs (JSON).
    PATCH: update (authenticated).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        obj = get_cost_settings()
        return Response(obj.data)

    def patch(self, request):
        obj = get_cost_settings()
        if not isinstance(request.data, dict):
            return Response({'detail': 'Expected a JSON object.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.data = request.data
        obj.save(update_fields=['data'])
        return Response(obj.data)
