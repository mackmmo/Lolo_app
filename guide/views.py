from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import django_filters
from django.http import HttpResponse
from django.db import connection
from .models import Sector, Area, SubArea, Route, RouteLog, RouteComment, RouteTodo
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count


from .serializers import (
    SectorSerializer,
    AreaSerializer,
    SubAreaSerializer,
    RouteSerializer,
    RouteLogSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    RouteCommentSerializer,
    RouteTodoSerializer,
)

from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response

@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get("email", "").strip()

    # Always return the same response so we don't reveal
    # whether an email address has an account.
    response_message = {
        "detail": "If an account exists for that email, a password reset link has been sent."
    }

    if not email:
        return Response(response_message)

    user = User.objects.filter(
        email__iexact=email,
        is_active=True
    ).first()

    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = (
            f"{settings.FRONTEND_URL}"
            f"?reset_uid={uid}&reset_token={token}"
        )

        subject = "Reset your Lolo Guide password"

        message = (
            f"Hi {user.username},\n\n"
            "We received a request to reset your Lolo Guide password.\n\n"
            f"Reset your password here:\n{reset_url}\n\n"
            "If you didn't request this, you can ignore this email.\n"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    return Response(response_message)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not uid or not token or not new_password:
        return Response(
            {"detail": "uid, token, and new_password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"detail": "Invalid or expired password reset link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(user, token):
        return Response(
            {"detail": "Invalid or expired password reset link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        return Response(
            {"new_password": list(exc.messages)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return Response({
        "detail": "Password reset successfully."
    })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

@api_view(["GET"])
def profile_view(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email,
    })

@api_view(["POST"])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    request.user.set_password(serializer.validated_data["new_password"])
    request.user.save(update_fields=["password"])
    return Response({"detail": "Password updated successfully."})

class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all().order_by('sector_id')
    serializer_class = SectorSerializer

class AreaListView(generics.ListAPIView):
    queryset = Area.objects.all().order_by('area_id')
    serializer_class = AreaSerializer

class SubAreaListView(generics.ListAPIView):
    queryset = SubArea.objects.all().order_by('subarea_id')
    serializer_class = SubAreaSerializer

class RouteDetailView(generics.RetrieveAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class RouteFilter(django_filters.FilterSet):
    min_grade = django_filters.NumberFilter(field_name="grade_index", lookup_expr="gte")
    max_grade = django_filters.NumberFilter(field_name="grade_index", lookup_expr="lte")
    sector = django_filters.NumberFilter(field_name="area__sector__sector_id")
    area = django_filters.NumberFilter(field_name="area__area_id")
    subarea = django_filters.NumberFilter(field_name="subarea__subarea_id")
    type = django_filters.CharFilter(field_name="type", lookup_expr="iexact")

    class Meta:
        model = Route
        fields = ["sector", "area", "subarea", "type"]

class RouteListView(generics.ListAPIView):
    queryset = Route.objects.all().order_by("route_id")
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RouteFilter
    search_fields = ["name", "grade", "type", "area__name", "subarea__name"]
    ordering_fields = ["name", "grade", "grade_index", "type", "star_rating", "height", "crag_order"]

# Vector tile endpoint for areas
def area_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                area_id,
                name,
                description,
                drive_time,
                approach_time,
                aspect,
                ST_AsText(centroid) AS centroid_wkt,
                ST_X(ST_Transform(centroid, 4326)) AS lon,
                ST_Y(ST_Transform(centroid, 4326)) AS lat,
                ST_AsMVTGeom(
                  boundary,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM area
              WHERE boundary && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'areas', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )
# area label endpoint
def area_label_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                area_id,
                name,
                ST_AsMVTGeom(
                  centroid,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM area
              WHERE centroid && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'area_labels', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for roads
def road_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                road_id,
                roadname,
                ST_AsMVTGeom(
                  ST_Transform(ST_Force2D(wkb_geometry), 3857),
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM roads
              WHERE ST_Transform(wkb_geometry, 3857) && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'roads', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for trails
def trail_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                trail_id,
                approach,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM trails
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'trails', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for pois
def poi_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                poi_id,
                name,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM poi
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'poi', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for trailheads
def trailhead_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                trailhead_id,
                name,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM trailheads
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'trailheads', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for gates
def gate_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                gate_id,
                name,
                description,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM gates
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'gates', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

@api_view(['POST'])
def verify_google_token(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=400)

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name')

        return Response({'userid': userid, 'email': email, 'name': name})

    except ValueError:
        # Invalid token
        return Response({'error': 'Invalid token'}, status=400)

class RouteLogListCreateView(generics.ListCreateAPIView):
    serializer_class = RouteLogSerializer

    def get_queryset(self):
        return (
            RouteLog.objects
            .filter(user=self.request.user)
            .select_related("route")
            .order_by("-updated_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RouteLogSerializer
    lookup_field = "log_id"

    def get_queryset(self):
        return (
            RouteLog.objects
            .filter(user=self.request.user)
            .select_related("route")
        )

class RouteTodoListCreateView(generics.ListCreateAPIView):
    serializer_class = RouteTodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            RouteTodo.objects
            .filter(user=self.request.user)
            .select_related("route")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteTodoDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = RouteTodoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "todo_id"

    def get_queryset(self):
        return (
            RouteTodo.objects
            .filter(user=self.request.user)
            .select_related("route")
        )


class RouteCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = RouteCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            RouteComment.objects
            .select_related("user", "route")
            .order_by("-created_at")
        )

        route_id = self.request.query_params.get("route")

        if route_id:
            queryset = queryset.filter(route_id=route_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RouteCommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "comment_id"

    def get_queryset(self):
        # A user can only edit/delete their OWN comments.
        return RouteComment.objects.filter(user=self.request.user)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def route_community_stats(request, route_id):
    # Make sure the route actually exists.
    try:
        route = Route.objects.get(pk=route_id)
    except Route.DoesNotExist:
        return Response(
            {"detail": "Route not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    sent_logs = RouteLog.objects.filter(
        route=route,
        status="sent",
    )

    send_counts = {
        row["send_style"]: row["count"]
        for row in (
            sent_logs
            .exclude(send_style__isnull=True)
            .values("send_style")
            .annotate(count=Count("log_id"))
        )
    }

    return Response({
        "route": route.route_id,
        "total_sends": sent_logs.count(),
        "onsight": send_counts.get("onsight", 0),
        "flash": send_counts.get("flash", 0),
        "redpoint": send_counts.get("redpoint", 0),
    })