from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Sector, Area, SubArea, Route

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
        return User.objects.create_user(**validated_data)

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