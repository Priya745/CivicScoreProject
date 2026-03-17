from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.core.models import CivicScore
from .models import Reward, RedeemedReward, RewardNotification


def _get_user_points(user):
    """Points come from CivicScore (same as dashboard), not CustomUser.civic_score."""
    if not user.is_authenticated:
        return 0
    civicscore, _ = CivicScore.objects.get_or_create(user=user)
    return civicscore.total_points


def rewards_list(request):
    """Show all active rewards with NGO name, points required, and redeem button."""
    rewards = Reward.objects.filter(is_active=True).select_related("ngo").order_by("-created_at")
    user_points = _get_user_points(request.user)
    context = {
        "rewards": rewards,
        "user_points": user_points,
    }
    return render(request, "rewards/rewards_list.html", context)


@login_required
def redeem_reward(request, reward_id):
    """
    Check points (CivicScore), deduct from CivicScore and CustomUser.civic_score,
    create RedeemedReward with status pending.
    """
    reward = get_object_or_404(Reward, pk=reward_id, is_active=True)
    user = request.user
    civicscore, _ = CivicScore.objects.get_or_create(user=user)
    user_points = civicscore.total_points

    if user_points < reward.points_required:
        messages.error(
            request,
            f"You need {reward.points_required} points. You have {user_points} points.",
        )
        return redirect("rewards_list")

    # Deduct from CivicScore (source of truth, matches dashboard)
    civicscore.total_points -= reward.points_required
    civicscore.save(update_fields=["total_points"])
    # Keep CustomUser.civic_score in sync
    user.civic_score = max(0, (user.civic_score or 0) - reward.points_required)
    user.save(update_fields=["civic_score"])
    RedeemedReward.objects.create(user=user, reward=reward, status="pending")
    messages.success(
        request,
        f"Reward '{reward.title}' redeemed. Your request is pending approval by {reward.ngo.name}.",
    )
    return redirect("my_rewards")


@login_required
def my_rewards(request):
    """Show rewards redeemed by the logged-in user and their status."""
    redemptions = (
        RedeemedReward.objects.filter(user=request.user)
        .select_related("reward", "reward__ngo")
        .order_by("-redeemed_at")
    )
    notifications = RewardNotification.objects.filter(user=request.user, is_read=False).order_by("-created_at")[:10]
    context = {
        "redemptions": redemptions,
        "notifications": notifications,
    }
    return render(request, "rewards/my_rewards.html", context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read and optionally redirect."""
    notification = get_object_or_404(RewardNotification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("my_rewards")
