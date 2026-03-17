from django.urls import path
from . import views

urlpatterns = [
    path("", views.rewards_list, name="rewards_list"),
    path("redeem/<int:reward_id>/", views.redeem_reward, name="redeem_reward"),
    path("my-rewards/", views.my_rewards, name="my_rewards"),
    path(
        "notification/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
]
