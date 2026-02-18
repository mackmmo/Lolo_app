# guide/views.py
from rest_framework import generics
from .models import Sector
from .serializers import SectorSerializer
from django.http import JsonResponse
from django.http import JsonResponse
from django.views import View

class SectorListView(View):
    def get(self, request):
        return JsonResponse({"message": "Sectors view works"})
def db_debug(request):
    try:
        sector_count = Sector.objects.count()
        return JsonResponse({"status": "ok", "sector_count": sector_count})
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)})