from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Sector, Area, SubArea, Route, RouteLog, RouteComment, RouteTodo, UserDataPermissions, CompetitionSend

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['sector_id', 'name', 'description','boundary', 'centroid']

class RouteSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source="area.name", read_only=True)
    subarea_name = serializers.CharField(source="subarea.name", read_only=True)
    
    class Meta:
        model = Route
        fields = ['route_id',
                  'area_name',
                  'subarea_name',
                  'area',
                  'crag_order', 
                  'centroid', 
                  'name', 
                  'type', 
                  'description', 
                  'grade', 
                  'subarea',    
                  'danger_rating', 
                  'star_rating', 
                  'centroid', 
                  'height', 
                  'first_ascencionist', 
                  'fa_year',
                  'pro']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['area_id', 'sector', 'boundary', 'centroid', 'name', 'description', 'directions', 'approach_time', 'drive_time', 'aspect']

class SubAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubArea
        fields = ['subarea_id', 'area', 'centroid', 'name', 'description', 'aspect']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        UserDataPermissions.objects.create(user=user)
        return user

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

class RouteLogSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(
        source="route.name",
        read_only=True
    )
    grade = serializers.CharField(
        source="route.grade",
        read_only=True
    )

    class Meta:
        model = RouteLog
        fields = [
            "log_id",
            "route",
            "route_name",
            "grade",
            "status",
            "send_style",
            "attempts",
            "date_sent",
            "beta",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "log_id",
            "created_at",
            "updated_at",
        ]

    def validate_date_sent(self, value):
        from .competition import competition_today
        if value and value > competition_today():
            raise serializers.ValidationError("A send cannot be dated in the future.")
        return value

class RouteTodoSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source="route.name", read_only=True)
    grade = serializers.CharField(source="route.grade", read_only=True)

    class Meta:
        model = RouteTodo
        fields = [
            "todo_id",
            "route",
            "route_name",
            "grade",
            "created_at",
        ]
        read_only_fields = [
            "todo_id",
            "created_at",
        ]


class RouteCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)
    grade = serializers.CharField(source="route.grade", read_only=True)

    class Meta:
        model = RouteComment
        fields = [
            "comment_id",
            "route",
            "route_name",
            "grade",
            "username",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "comment_id",
            "username",
            "created_at",
            "updated_at",
        ]



class CommunityFeedSerializer(serializers.Serializer):

    route_id = serializers.IntegerField(source="route.route_id", read_only=True)

    username = serializers.CharField(source="user.username", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)
    grade = serializers.CharField(source="route.grade", read_only=True)
    send_style = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    date_sent = serializers.DateField(read_only=True)



class DataPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDataPermissions
        fields = ["publish_feed", "publish_leaderboards"]


class CompetitionSendSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source="route.name", read_only=True)
    grade = serializers.CharField(source="route.grade", read_only=True)

    class Meta:
        model = CompetitionSend
        fields = ["id", "route", "route_name", "grade", "year", "date_sent", "send_style", "recorded_at"]
        read_only_fields = ["id", "year", "recorded_at"]

    def validate(self, attrs):
        from .competition import competition_today
        if self.instance and "route" in attrs and attrs["route"].pk != self.instance.route_id:
            raise serializers.ValidationError({"route": "Choose the route when creating a send. It cannot be changed afterwards."})
        date_sent = attrs.get("date_sent", getattr(self.instance, "date_sent", None))
        if date_sent and date_sent > competition_today():
            raise serializers.ValidationError({"date_sent": "A send cannot be dated in the future."})
        return attrs
