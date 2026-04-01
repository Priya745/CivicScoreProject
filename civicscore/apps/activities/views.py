"""
views.py — Activity submission and listing views.

Geo-validation flow:
--------------------
When a user submits an activity with a proof image the view calls
utils.extract_gps_info() to inspect the image's EXIF data.

  • GPS data found  → status stays "pending", is_geo_verified=True,
                      lat/lon stored in DB.
                      ✅ success message shown to user.

  • No GPS data     → status set to "manual_review", is_geo_verified=False.
                      ⚠️ warning message shown; activity is still saved so
                      the user doesn't lose their submission. An admin will
                      verify it manually.

  • Processing error (corrupted / non-image file) →
                      ⚠️ warning message; activity saved for manual review.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from .forms import ActivityForm
from .models import Activity, calculate_points
from .utils import extract_gps_info

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Submit Activity
# ---------------------------------------------------------------------------

@never_cache
@login_required
def activities(request):
    """
    GET  → render the empty submission form.
    POST → validate form, inspect proof image for GPS EXIF, save activity.
    """

    if request.method == "POST":

        form = ActivityForm(request.POST, request.FILES)

        if form.is_valid():

            activity        = form.save(commit=False)
            activity.user   = request.user
            activity.points = calculate_points(activity.activity_type)

            # ----------------------------------------------------------------
            # GPS / EXIF validation
            # ----------------------------------------------------------------
            proof_file = request.FILES.get("proof")

            if proof_file:
                try:
                    geo = extract_gps_info(proof_file)

                    if geo["has_gps"]:
                        # Valid GPS — store coordinates, mark verified
                        activity.latitude       = geo["latitude"]
                        activity.longitude      = geo["longitude"]
                        activity.is_geo_verified = True
                        activity.status         = "pending"

                        messages.success(
                            request,
                            "Activity submitted successfully with verified "
                            f"location ({geo['latitude']:.5f}, "
                            f"{geo['longitude']:.5f}).",
                        )

                    else:
                        #  No GPS tag — allow submission but flag for review
                        activity.is_geo_verified = False
                        activity.status         = "manual_review"

                        messages.warning(
                            request,
                            " Your proof image does not contain GPS location "
                            "data. Your submission has been saved and will be "
                            "reviewed manually by our team. "
                            "Tip: Upload a photo taken directly from your phone "
                            "camera (not a screenshot or edited image).",
                        )

                except Exception as exc:                   # noqa: BLE001
                    # Unexpected error — log it, still save for manual review
                    logger.exception(
                        "Geo-validation failed for user %s, file '%s': %s",
                        request.user,
                        getattr(proof_file, "name", "<unknown>"),
                        exc,
                    )
                    activity.is_geo_verified = False
                    activity.status         = "manual_review"

                    messages.warning(
                        request,
                        " We could not read location data from your image. "
                        "Your submission has been saved for manual review.",
                    )

            else:
                # No file at all (shouldn't happen if form is_valid, but be safe)
                activity.is_geo_verified = False
                activity.status         = "manual_review"

                messages.warning(
                    request,
                    "No proof file was detected. Submission saved for "
                    "manual review.",
                )

            # ----------------------------------------------------------------
            # Persist to database
            # ----------------------------------------------------------------
            activity.save()
            return redirect("dashboard")

    else:
        form = ActivityForm()

    return render(
        request,
        "activities/add_activity.html",
        {"form": form},
    )



@never_cache
@login_required
def my_activities(request):
    """Display all activities submitted by the current user, newest first."""

    activities_qs = Activity.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "activities/my_activities.html",
        {"activities": activities_qs},
    )