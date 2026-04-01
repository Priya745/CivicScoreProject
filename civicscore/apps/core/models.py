from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CivicScore(models.Model):               
    """
    Model to track civic points for each user.
    Each user can have only one CivicScore.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)          #If user is deleted, delete the score too

    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} Score"
