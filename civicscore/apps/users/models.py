from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    city = models.CharField(max_length=100, blank=True)
    civic_score = models.IntegerField(default=0)
    total_activities = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
