from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

from apps.activities.models import Activity
from apps.core.models import CivicScore
from apps.rewards.models import NGO, RedeemedReward, Reward, RewardNotification
from .admin_forms import NGOForm, RewardForm, RewardNotificationForm

User = get_user_model()


def _staff_only_or_home(request):
    if not request.user.is_staff:
        return redirect("/home")
    return None


@login_required
def admin_dashboard(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    context = {
        "active_tab": "dashboard",
        "total_users": User.objects.count(),
        "total_activities": Activity.objects.count(),
        "pending_activities": Activity.objects.filter(status="pending").count(),
        "approved_activities": Activity.objects.filter(status="approved").count(),
        "rejected_activities": Activity.objects.filter(status="rejected").count(),
    }
    return render(request, "admin_dashboard/dashboard.html", context)


@login_required
def admin_activities(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    activities = Activity.objects.select_related("user").order_by("-created_at")
    return render(
        request,
        "admin_dashboard/activities.html",
        {"activities": activities, "active_tab": "activities"},
    )


@login_required
@require_POST
def approve_activity(request, activity_id):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    activity = get_object_or_404(Activity, pk=activity_id)
    activity.status = "approved"
    activity.save()
    messages.success(request, "Activity approved successfully.")
    return redirect("admin_activities")


@login_required
@require_POST
def reject_activity(request, activity_id):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    activity = get_object_or_404(Activity, pk=activity_id)
    activity.status = "rejected"
    activity.save(update_fields=["status"])
    messages.success(request, "Activity rejected successfully.")
    return redirect("admin_activities")


@login_required
def admin_users(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    users = User.objects.order_by("-date_joined")
    return render(
        request,
        "admin_dashboard/users.html",
        {"users": users, "active_tab": "users"},
    )


@login_required
def admin_leaderboard(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    leaderboard = CivicScore.objects.select_related("user").order_by("-total_points")
    return render(
        request,
        "admin_dashboard/leaderboard.html",
        {"leaderboard": leaderboard, "active_tab": "leaderboard"},
    )


@login_required
def admin_ngos(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    ngos = NGO.objects.order_by("-created_at")
    return render(
        request,
        "admin_dashboard/ngos.html",
        {"ngos": ngos, "active_tab": "ngos"},
    )


@login_required
def create_ngo(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    if request.method == "POST":
        form = NGOForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "NGO created successfully.")
            return redirect("admin_ngos")
    else:
        form = NGOForm()

    return render(
        request,
        "admin_dashboard/ngo_form.html",
        {"form": form, "active_tab": "ngos", "form_title": "Add NGO"},
    )


@login_required
def edit_ngo(request, ngo_id):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    ngo = get_object_or_404(NGO, pk=ngo_id)
    if request.method == "POST":
        form = NGOForm(request.POST, request.FILES, instance=ngo)
        if form.is_valid():
            form.save()
            messages.success(request, "NGO updated successfully.")
            return redirect("admin_ngos")
    else:
        form = NGOForm(instance=ngo)

    return render(
        request,
        "admin_dashboard/ngo_form.html",
        {"form": form, "active_tab": "ngos", "form_title": "Edit NGO"},
    )


@login_required
@require_POST
def delete_ngo(request, ngo_id):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    ngo = get_object_or_404(NGO, pk=ngo_id)
    ngo.delete()
    messages.success(request, "NGO deleted successfully.")
    return redirect("admin_ngos")


@login_required
def admin_rewards(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    rewards = Reward.objects.select_related("ngo").order_by("-created_at")
    return render(
        request,
        "admin_dashboard/rewards.html",
        {"rewards": rewards, "active_tab": "rewards"},
    )


@login_required
def create_reward(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    if request.method == "POST":
        form = RewardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reward created successfully.")
            return redirect("admin_rewards")
    else:
        form = RewardForm()

    return render(
        request,
        "admin_dashboard/reward_form.html",
        {"form": form, "active_tab": "rewards", "form_title": "Add Reward"},
    )


@login_required
def edit_reward(request, reward_id):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    reward = get_object_or_404(Reward, pk=reward_id)
    if request.method == "POST":
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            messages.success(request, "Reward updated successfully.")
            return redirect("admin_rewards")
    else:
        form = RewardForm(instance=reward)

    return render(
        request,
        "admin_dashboard/reward_form.html",
        {"form": form, "active_tab": "rewards", "form_title": "Edit Reward"},
    )


@login_required
@require_POST
def delete_reward(request, reward_id):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    reward = get_object_or_404(Reward, pk=reward_id)
    reward.delete()
    messages.success(request, "Reward deleted successfully.")
    return redirect("admin_rewards")


@login_required
def admin_redeemed_rewards(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    redemptions = (
        RedeemedReward.objects.select_related("user", "reward", "reward__ngo")
        .order_by("-redeemed_at")
    )
    return render(
        request,
        "admin_dashboard/redeemed_rewards.html",
        {"redemptions": redemptions, "active_tab": "redeemed_rewards"},
    )


@login_required
@require_POST
def update_redeemed_reward_status(request, redemption_id, status):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    allowed_statuses = {"approved", "rejected", "completed"}
    if status not in allowed_statuses:
        messages.error(request, "Invalid status update.")
        return redirect("admin_redeemed_rewards")

    redemption = get_object_or_404(RedeemedReward, pk=redemption_id)
    redemption.status = status
    redemption.save(update_fields=["status"])
    messages.success(request, f"Redemption marked as {status}.")
    # Send redemption status email directly to user
    if redemption.user.email:
        status_messages = {
            "approved": "Your redemption request has been APPROVED. The reward will be processed shortly.",
            "completed": "Your redemption has been marked as COMPLETED. Enjoy your reward!",
            "rejected": "Unfortunately, your redemption request has been REJECTED. Please contact support if you think this is an error.",
        }
        try:
            send_mail(
                subject=f"Your Reward Redemption is {status.capitalize()} \u2013 CivicScore",
                message=(
                    f"Hi {redemption.user.username},\n\n"
                    f"Update on your redemption for '{redemption.reward.name}':\n\n"
                    f"{status_messages.get(status, '')}\n\n"
                    "\u2013 The CivicScore Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[redemption.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"EMAIL ERROR: {e}")
    return redirect("admin_redeemed_rewards")



@login_required
def admin_reward_notifications(request):
    denied = _staff_only_or_home(request)
    if denied:
        return denied

    if request.method == "POST":
        form = RewardNotificationForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data["message"]
            user = form.cleaned_data["user"]
            notify_all = form.cleaned_data["notify_all_users"]

            if notify_all:
                users = User.objects.filter(is_active=True)
                RewardNotification.objects.bulk_create(
                    [RewardNotification(user=u, message=message) for u in users]
                )
                messages.success(request, "Notification sent to all active users.")
            else:
                RewardNotification.objects.create(user=user, message=message)
                messages.success(request, f"Notification sent to {user.username}.")
            return redirect("admin_reward_notifications")
    else:
        form = RewardNotificationForm()

    notifications = RewardNotification.objects.select_related("user").order_by("-created_at")
    return render(
        request,
        "admin_dashboard/reward_notifications.html",
        {
            "form": form,
            "notifications": notifications,
            "active_tab": "reward_notifications",
        },
    )
