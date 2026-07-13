from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import AccountAuthenticationForm, AccountCreationForm


def register_view(request):
    if request.method == "POST":
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
    else:
        form = AccountCreationForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AccountAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("blog:home")
    else:
        form = AccountAuthenticationForm()
    return render(request, "registration/login.html", {"form": form})
