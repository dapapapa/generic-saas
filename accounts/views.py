from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import SignupForm


class LoginViewCustom(LoginView):
    template_name = "accounts/login.html"


class LogoutViewCustom(LogoutView):
    next_page = reverse_lazy("home")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # IMPORTANT:
            # Workspace is created by accounts/signals.py (post_save on User)
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})
