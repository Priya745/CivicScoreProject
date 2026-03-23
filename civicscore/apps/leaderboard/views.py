from django.core.paginator import Paginator
from django.shortcuts import render

from apps.core.models import CivicScore


def leaderboard(request):
    leaderboard_data = (
        CivicScore.objects.select_related("user")
        .order_by("-total_points")
    )
    paginator = Paginator(leaderboard_data, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    context = {"leaderboard": page_obj.object_list, "page_obj": page_obj}
    return render(request, "leaderboard/leaderboard.html", context)