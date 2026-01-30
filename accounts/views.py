from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages


def register(request):
    if request.method == "POST":
        user_first_name = request.POST.get("first_name")
        user_last_name = request.POST.get("last_name")
        user_username = request.POST.get("username")
        user_email = request.POST.get("email")
        user_password = request.POST.get("password")

        User.objects.create_user(
            username=user_username,
            first_name=user_first_name,
            last_name=user_last_name,
            email=user_email,
            password=user_password
        )

        messages.success(request, "Account created successfully")
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth.login(request, user)

            # ✅ redirect after login
            return redirect("timeline:dashboard")

        messages.error(request, "Invalid credentials")
        return redirect("accounts:login")

    return render(request, "accounts/login.html")


def logout_view(request):
    auth.logout(request)
    return redirect("/")
