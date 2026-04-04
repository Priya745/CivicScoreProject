from django.core.mail import send_mail
from django.conf import settings


def send_reward_status_email(user, reward, status):

    if status == "pending":
        subject = "Reward Redemption Request Submitted"
        message = f"""
Hello {user.username},

Your reward '{reward.title}' has been successfully redeemed.

Status: Pending approval from {reward.ngo.name}

Points required: {reward.points_required}
"""

    elif status == "approved":
        subject = "Reward Approved"
        message = f"""
Hello {user.username},

Good news! Your reward '{reward.title}' has been approved by {reward.ngo.name}.

You will receive a call shortly by our team. Congratulations!!
"""

    elif status == "completed":
        subject = "Reward Completed"
        message = f"""
Hello {user.username},

Your reward '{reward.title}' has been completed.

Thank you for your civic participation!
"""

    elif status == "rejected":
        subject = "Reward Rejected"
        message = f"""
Hello {user.username},

Unfortunately your reward '{reward.title}' was rejected by {reward.ngo.name}.
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )