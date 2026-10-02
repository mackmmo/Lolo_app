from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from guide.views import (
    RouteDetailView,
    RegisterView,
    SectorListView,
    AreaListView,
    SubAreaListView,
    RouteListView,
    area_label_tiles,
    area_tiles,
    road_tiles,
    trail_tiles,
    poi_tiles,
    trailhead_tiles,
    gate_tiles,
    profile_view,
    change_password,
    RouteLogListCreateView,
    RouteLogDetailView,
    password_reset_request,
    password_reset_confirm,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/profile/', profile_view, name='profile'),
    path('api/profile/password/', change_password, name='change-password'),
    path("api/password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("api/password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    
    path("api/logbook/", RouteLogListCreateView.as_view(), name="route-log-list"),
    path("api/logbook/<int:log_id>/", RouteLogDetailView.as_view(), name="route-log-detail"),
    
    path('sectors/', SectorListView.as_view(), name='sector-list'),
    path('areas/', AreaListView.as_view(), name='area-list'),
    path('api/', include('api.urls')),  # include API URLs
    path('subareas/', SubAreaListView.as_view(), name='subarea-list'),
    path('routes/', RouteListView.as_view(), name='route-list'),
    path('routes/<int:pk>/', RouteDetailView.as_view(), name='route-detail'),
    
    path("tiles/area-labels/<int:z>/<int:x>/<int:y>.mvt", area_label_tiles, name="area-label-tiles"),
    path("tiles/areas/<int:z>/<int:x>/<int:y>.mvt", area_tiles, name="area-tiles"),
    path("tiles/roads/<int:z>/<int:x>/<int:y>.mvt", road_tiles, name="road-tiles"),
    path("tiles/trails/<int:z>/<int:x>/<int:y>.mvt", trail_tiles, name="trail-tiles"),
    path("tiles/pois/<int:z>/<int:x>/<int:y>.mvt", poi_tiles, name="poi-tiles"),
    path("tiles/trailheads/<int:z>/<int:x>/<int:y>.mvt", trailhead_tiles, name="trailhead-tiles"),
    path("tiles/gates/<int:z>/<int:x>/<int:y>.mvt", gate_tiles, name="gate-tiles"),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]

