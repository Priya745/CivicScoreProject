from django.contrib import admin
from django.contrib import messages

from .models import NGO, Reward, RedeemedReward, RewardNotification


@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "website", "created_at")
    search_fields = ("name", "email")


class RewardInline(admin.TabularInline):       #This allows editing rewards inside NGO page (like nested data)
    model = Reward
    extra = 0
    fields = ("title", "reward_type", "points_required", "is_active")


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("title", "ngo", "reward_type", "points_required", "is_active", "created_at")
    list_filter = ("ngo", "reward_type", "is_active")
    search_fields = ("title", "ngo__name")
    list_editable = ("is_active",)
    inlines = []  # Optional: add RewardInline to NGO for editing rewards from NGO page


@admin.register(RedeemedReward)
class RedeemedRewardAdmin(admin.ModelAdmin):
    list_display = ("user", "reward", "reward_ngo", "status", "redeemed_at")
    list_filter = ("status", "reward__ngo")
    search_fields = ("user__username", "reward__title")
    list_editable = ("status",)
    readonly_fields = ("redeemed_at",)

    def reward_ngo(self, obj):                #Fetches NGO name from: RedeemedReward → Reward → NGO
        return obj.reward.ngo.name

    reward_ngo.short_description = "NGO"       #Sets column title in admin

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            old_obj = RedeemedReward.objects.get(pk=obj.pk) if obj.pk else None
            if old_obj and old_obj.status != obj.status:
                if obj.status == "approved":
                    RewardNotification.objects.create(
                        user=obj.user,
                        message=f"Your reward '{obj.reward.title}' has been approved by {obj.reward.ngo.name}.",
                        redeemed_reward=obj,
                    )
                elif obj.status == "rejected":
                    RewardNotification.objects.create(
                        user=obj.user,
                        message=f"Your reward request '{obj.reward.title}' was not approved.",
                        redeemed_reward=obj,
                    )
        super().save_model(request, obj, form, change)


@admin.register(RewardNotification)
class RewardNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("user__username", "message")
