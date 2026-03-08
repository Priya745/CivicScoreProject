from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.contrib import messages

# from apps.users.models import CustomUser

from django.contrib.auth import logout


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
            return redirect('dashboard')

        return render(request,
                      "accounts/login.html",
                      {"error": "Invalid credentials"})

    return render(request, "accounts/login.html")
  

# @login_required
# def dashboard(request):
#     return render(request, "dashboard.html")

def register_view(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
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

        # Create User
        user = User.objects.create_user(
        username=username,
        email=email,
        password=password1
       )

        # Save full name
        user.first_name = name   #update
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "accounts/register.html")



def logout_view(request):
    logout(request)
    return redirect('login')
