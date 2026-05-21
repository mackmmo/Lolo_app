from django.contrib import admin
from django.urls import path, include

from guide.views import (
    RouteDetailView,
    SectorListView,
    AreaListView,
    SubAreaListView,
    RouteListView,
    area_tiles,
    road_tiles,
    trail_tiles,
    poi_tiles,
    trailhead_tiles,
    gate_tiles,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('sectors/', SectorListView.as_view(), name='sector-list'),
    path('areas/', AreaListView.as_view(), name='area-list'),
    path('api/', include('api.urls')),  # include API URLs
    path('subareas/', SubAreaListView.as_view(), name='subarea-list'),
    path('routes/', RouteListView.as_view(), name='route-list'),
    path('routes/<int:pk>/', RouteDetailView.as_view(), name='route-detail'),
    
    path("tiles/areas/<int:z>/<int:x>/<int:y>.mvt", area_tiles, name="area-tiles"),
    path("tiles/roads/<int:z>/<int:x>/<int:y>.mvt", road_tiles, name="road-tiles"),
    path("tiles/trails/<int:z>/<int:x>/<int:y>.mvt", trail_tiles, name="trail-tiles"),
    path("tiles/pois/<int:z>/<int:x>/<int:y>.mvt", poi_tiles, name="poi-tiles"),
    path("tiles/trailheads/<int:z>/<int:x>/<int:y>.mvt", trailhead_tiles, name="trailhead-tiles"),
    path("tiles/gates/<int:z>/<int:x>/<int:y>.mvt", gate_tiles, name="gate-tiles"),
]