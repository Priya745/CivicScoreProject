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