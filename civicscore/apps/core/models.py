from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CivicScore(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)   #user is a ForeignKey field,  It connects CivicScore → User

    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} Score"
