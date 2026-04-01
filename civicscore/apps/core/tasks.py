from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


def _send(subject, message, recipient_email):
    """Internal helper that actually calls Django's send_mail."""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )


@shared_task
def send_welcome_email(username, recipient_email):
    """Triggered when a new user registers."""
    subject = "Welcome to CivicScore! 🎉"
    message = (
        f"Hi {username},\n\n"
        "Welcome to CivicScore! Your account has been created successfully.\n\n"
        "Start logging your civic activities to earn points and climb the leaderboard.\n\n"
        "– The CivicScore Team"
    )
    _send(subject, message, recipient_email)


@shared_task
def send_activity_status_email(username, recipient_email, activity_type, status):
    """Triggered when an admin approves or rejects an activity."""
    status_label = status.capitalize()
    subject = f"Your Activity has been {status_label} – CivicScore"
    if status == "approved":
        message = (
            f"Hi {username},\n\n"
            f"Great news! Your '{activity_type}' activity has been APPROVED by our team.\n"
            "Your civic points have been added to your account.\n\n"
            "Keep up the great work!\n\n"
            "– The CivicScore Team"
        )
    else:
        message = (
            f"Hi {username},\n\n"
            f"Unfortunately, your '{activity_type}' activity has been REJECTED.\n"
            "This may be due to insufficient proof or activity details.\n\n"
            "You are welcome to submit again with clearer evidence.\n\n"
            "– The CivicScore Team"
        )
    _send(subject, message, recipient_email)


@shared_task
def send_redemption_status_email(username, recipient_email, reward_name, status):
    """Triggered when an admin changes the status of a redeemed reward."""
    status_label = status.capitalize()
    subject = f"Your Reward Redemption is {status_label} – CivicScore"
    if status == "approved":
        detail = "Your redemption request has been APPROVED. The reward will be processed shortly."
    elif status == "completed":
        detail = "Your redemption has been marked as COMPLETED. Enjoy your reward!"
    else:  # rejected
        detail = "Unfortunately, your redemption request has been REJECTED. Please contact support if you think this is an error."

    message = (
        f"Hi {username},\n\n"
        f"Update on your redemption request for '{reward_name}':\n\n"
        f"{detail}\n\n"
        "– The CivicScore Team"
    )
    _send(subject, message, recipient_email)
