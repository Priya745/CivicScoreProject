from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Activity(models.Model):

    ACTIVITY_CHOICES = [
        ("tree", "Tree Plantation"),
        ("clean", "Cleanliness Drive"),
        ("blood", "Blood Donation"),
        ("volunteer", "Volunteering"),
        ("teaching", "Teaching / Mentoring"),
        ("others", "Others"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("manual_review", "Manual Review"),   # Submitted without GPS — needs admin check
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_CHOICES
    )

    description = models.TextField()

    proof = models.FileField(upload_to="activity_proofs/")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    points = models.IntegerField(default=0)

    # ── Geo-location fields (populated from EXIF GPS metadata) ───────────
    latitude       = models.FloatField(null=True, blank=True)
    longitude      = models.FloatField(null=True, blank=True)
    is_geo_verified = models.BooleanField(
        default=False,
        help_text="True when the proof image contained valid GPS EXIF data.",
    )

    is_points_awarded = models.BooleanField(
        default=False,
        help_text="True when points for this activity have been added to the user's total score.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def save(self, *args, **kwargs):
        status_changed = False
        if self.pk is not None and self.status != self._original_status:
            status_changed = True

        super().save(*args, **kwargs)

        if status_changed and self.user.email and self.status in ["approved", "rejected"]:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"Your Activity has been {self.status.capitalize()} \u2013 CivicScore"
            if self.status == "approved":
                message = (
                    f"Hi {self.user.username},\n\n"
                    f"Great news! Your '{self.get_activity_type_display()}' activity has been APPROVED.\n"
                    "Your civic points have been added to your account.\n\n"
                    "Keep up the great work!\n\n"
                    "\u2013 The CivicScore Team"
                )
            else:
                message = (
                    f"Hi {self.user.username},\n\n"
                    f"Unfortunately, your '{self.get_activity_type_display()}' activity has been REJECTED.\n"
                    "This may be due to insufficient proof or activity details.\n\n"
                    "You are welcome to submit again with clearer evidence.\n\n"
                    "\u2013 The CivicScore Team"
                )
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"EMAIL ERROR: {e}")

        # Update the original status after save
        self._original_status = self.status

    def __str__(self):
        return f"{self.user} - {self.activity_type}"


# POINTS CALCULATION FUNCTION
def calculate_points(activity_type):

    points_map = {
        "tree":      15,
        "clean":     10,
        "blood":     20,
        "volunteer": 12,
        "teaching":  14,
        "others":     5,
    }

    return points_map.get(activity_type, 0)