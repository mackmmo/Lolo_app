# guide/views.py
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Sector

# Example DRF view you already have
from .serializers import SectorSerializer
from rest_framework import generics

class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all().order_by('sector_id')
    serializer_class = SectorSerializer


# Add this db_debug view
def db_debug(request):
    """
    Simple view to check DB connection and list sector count.
    """
    try:
        sector_count = Sector.objects.count()
        return JsonResponse({"status": "ok", "sector_count": sector_count})
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)})