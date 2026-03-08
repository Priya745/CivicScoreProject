from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.core.models import CivicScore
from apps.activities.models import Activity


@login_required
def dashboard(request):
    civicscore, _ = CivicScore.objects.get_or_create(user=request.user)
    activities = Activity.objects.filter(user=request.user).order_by("-created_at")
    approved_count = activities.filter(status="approved").count()
    recent_activities = activities[:5]

    context = {
        "civicscore": civicscore,
        "total_points": civicscore.total_points,
        "activities_count": activities.count(),
        "approved_count": approved_count,
        "recent_activities": recent_activities,
    }
    return render(request, "dashboard/dashboard.html", context)
  
