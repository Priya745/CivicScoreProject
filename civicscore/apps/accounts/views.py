from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.contrib import messages

# from apps.users.models import CustomUser

from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            if user.is_superuser:
                return redirect("/admin")
            if user.is_staff:
                return redirect("admin_dashboard")
            return redirect("/home")

        return render(request,
                      "accounts/login.html",
                      {"error": "Invalid credentials"})

    return render(request, "accounts/login.html")
  


def register_view(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        city = request.POST.get("city")
        phone_number = request.POST.get("phone_number")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        # Username exists check (read)
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        # Phone number required
        if not (phone_number or "").strip():
            messages.error(request, "Phone number is required")
            return redirect("register")

        # Create User
        user = User.objects.create_user(
        username=username,
        email=email,
        password=password1
       )

        # Save full name
        name_parts = (name or "").strip().split()
        user.first_name = name_parts[0] if name_parts else ""
        user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        user.city = city
        user.phone_number = phone_number.strip()
        user.save()

        messages.success(request, "Account created successfully!")
        # Send welcome email directly (synchronous, no Celery needed)
        if user.email:
            try:
                send_mail(
                    subject="Welcome to CivicScore! 🎉",
                    message=(
                        f"Hi {user.username},\n\n"
                        "Welcome to CivicScore! Your account has been created successfully.\n\n"
                        "Start logging your civic activities to earn points and climb the leaderboard.\n\n"
                        "– The CivicScore Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Don't block registration if email fails
        return redirect("login")


    return render(request, "accounts/register.html")



def logout_view(request):
    logout(request)
    return redirect('login')
