from django.contrib import admin
from .models import Activity, calculate_points
from apps.core.models import CivicScore


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):

    list_display = ("user", "activity_type", "status", "points", "created_at")
    list_editable = ("status",)

    def save_model(self, request, obj, form, change):

        points_added = False

        # If admin approves activity
        if obj.status == "approved" and obj.points == 0:

            points = calculate_points(obj.activity_type)

            obj.points = points

            civicscore, created = CivicScore.objects.get_or_create(
                user=obj.user
            )

            civicscore.total_points += points
            civicscore.save()
            # Keep CustomUser.civic_score in sync for reward redemption
            obj.user.civic_score = (obj.user.civic_score or 0) + points
            obj.user.save(update_fields=["civic_score"])
            points_added = True

        super().save_model(request, obj, form, change)

        # Persist points: super() uses update_fields=form.changed_data, so our
        # obj.points update is not saved. Explicitly save points.
        if points_added:
            obj.save(update_fields=["points"])
