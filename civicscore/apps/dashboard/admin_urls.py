from django.urls import path

from . import admin_views


urlpatterns = [
    path("", admin_views.admin_dashboard, name="admin_dashboard"),
    path("activities/", admin_views.admin_activities, name="admin_activities"),
    path("activities/<int:activity_id>/approve/", admin_views.approve_activity, name="approve_activity"),
    path("activities/<int:activity_id>/reject/", admin_views.reject_activity, name="reject_activity"),
    path("users/", admin_views.admin_users, name="admin_users"),
    path("ngos/", admin_views.admin_ngos, name="admin_ngos"),
    path("ngos/create/", admin_views.create_ngo, name="create_ngo"),
    path("ngos/<int:ngo_id>/edit/", admin_views.edit_ngo, name="edit_ngo"),
    path("ngos/<int:ngo_id>/delete/", admin_views.delete_ngo, name="delete_ngo"),
    path("rewards/", admin_views.admin_rewards, name="admin_rewards"),
    path("rewards/create/", admin_views.create_reward, name="create_reward"),
    path("rewards/<int:reward_id>/edit/", admin_views.edit_reward, name="edit_reward"),
    path("rewards/<int:reward_id>/delete/", admin_views.delete_reward, name="delete_reward"),
    path("redeemed-rewards/", admin_views.admin_redeemed_rewards, name="admin_redeemed_rewards"),
    path(
        "redeemed-rewards/<int:redemption_id>/<str:status>/",
        admin_views.update_redeemed_reward_status,
        name="update_redeemed_reward_status",
    ),
    path(
        "reward-notifications/",
        admin_views.admin_reward_notifications,
        name="admin_reward_notifications",
    ),
    path("leaderboard/", admin_views.admin_leaderboard, name="admin_leaderboard"),
]
