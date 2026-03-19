from django.contrib import admin
from .models import Activity, calculate_points
from apps.core.models import CivicScore


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = ("user", "activity_type", "status", "points", "created_at", "is_points_awarded")
    list_editable = ("status",)
    list_filter = ("status", "is_geo_verified", "is_points_awarded")
    readonly_fields = ("is_points_awarded", "latitude", "longitude")
