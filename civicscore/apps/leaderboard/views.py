from django.shortcuts import render

from apps.core.models import CivicScore


def leaderboard(request):
    leaderboard_data = (
        CivicScore.objects.select_related("user")
        .order_by("-total_points")[:20]
    )
    context = {"leaderboard": leaderboard_data}
    return render(request, "leaderboard/leaderboard.html", context)