from django.db import models
from django.conf import settings


class NGO(models.Model):
    """Organizations that offer rewards to citizens."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="ngo_logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Reward(models.Model):
    """Rewards offered by NGOs, redeemable with civic_score points."""

    REWARD_TYPE_CHOICES = [
        ("certificate", "Participation Certificate"),
        ("invitation", "Invitation to Volunteer Drive"),
        ("recognition", "Recognition for Civic Work"),
        ("volunteer", "Volunteer Opportunity"),
    ]

    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name="rewards")
    title = models.CharField(max_length=200)
    description = models.TextField()
    points_required = models.PositiveIntegerField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.ngo.name})"


class RedeemedReward(models.Model):
    """Tracks when a user redeems a reward."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="redeemed_rewards"
    )
    reward = models.ForeignKey(
        Reward, on_delete=models.CASCADE, related_name="redemptions"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reward.title} ({self.status})"


class RewardNotification(models.Model):
    """In-app notification when a redeemed reward is approved or rejected."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reward_notifications"
    )
    message = models.CharField(max_length=500)
    redeemed_reward = models.ForeignKey(
        RedeemedReward, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
