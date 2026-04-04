from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RedeemedReward, RewardNotification
from .utils import send_reward_status_email


@receiver(post_save, sender=RedeemedReward)
def reward_status_handler(sender, instance, created, **kwargs):

    user = instance.user
    reward = instance.reward
    status = instance.status

    # Send email
    send_reward_status_email(user, reward, status)

    # Create in-app notification
    message = f"Your reward '{reward.title}' is now {status}."

    RewardNotification.objects.create(
        user=user,
        message=message,
        redeemed_reward=instance
    )