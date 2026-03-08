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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.activity_type}"


# POINTS CALCULATION FUNCTION
def calculate_points(activity_type):

    points_map = {

        "tree": 10,
        "clean": 8,
        "blood": 12,
        "volunteer": 6,
        "teaching": 7,
        "others": 5,

    }

    return points_map.get(activity_type, 0)