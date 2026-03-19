# from django.shortcuts import render

# # Create your views here.
# def activities(request):
#   return render(request, 'activities/add_activity.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ActivityForm
from .models import Activity


@login_required
def activities(request):

    if request.method == "POST":

        form = ActivityForm(request.POST, request.FILES)         #builds ActivityForm  -> linked to Activity model

        if form.is_valid():

            activity = form.save(commit=False)

            activity.user = request.user
            activity.status = "pending"

            activity.save()          #saves to database

            return redirect("dashboard")            #redirects to dashboard

    else:
        form = ActivityForm()

    return render(
        request,
        "activities/add_activity.html",
        {"form": form}
    )
    
    
@login_required
def my_activities(request):

    activities = Activity.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request, "activities/my_activities.html",
        {"activities": activities}
    )