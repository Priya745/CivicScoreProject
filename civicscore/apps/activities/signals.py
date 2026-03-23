from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Activity, calculate_points
from apps.core.models import CivicScore

@receiver(post_save, sender=Activity)
def handle_activity_points(sender, instance, created, **kwargs):
    """
    Automatically increments CivicScore and User.civic_score when an
    activity's status is changed to 'approved'.
    """
    # Only proceed if status is approved and points haven't been awarded yet
    if instance.status == "approved" and not instance.is_points_awarded:
        
        # 1. Ensure points are calculated for this activity if not already set
        if not instance.points or instance.points == 0:
            instance.points = calculate_points(instance.activity_type)
        
        # 2. Update CivicScore (OneToOne model)
        civic_score, _ = CivicScore.objects.get_or_create(user=instance.user)
        civic_score.total_points += instance.points
        civic_score.save()
        
        # 3. Update CustomUser.civic_score (Redundant but kept for sync)
        user = instance.user
        user.civic_score = (user.civic_score or 0) + instance.points
        user.save(update_fields=["civic_score"])
        
        # 4. Mark as awarded to prevent double-counting on future edits
        instance.is_points_awarded = True
        
        # Use update_fields to avoid triggering post_save again (infinite recursion)
        instance.save(update_fields=["is_points_awarded", "points"])


