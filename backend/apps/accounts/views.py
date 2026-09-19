from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LadyEnterForm, PhoneAuthForm, SponsorJoinForm
from .models import User


def adult_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get("adult_ok") or (
            request.user.is_authenticated and request.user.is_adult_confirmed
        ):
            return view_func(request, *args, **kwargs)
        return redirect("accounts:gate")

    return wrapper


class PhoneLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = PhoneAuthForm

    def get_success_url(self):
        user = self.request.user
        if user.role == User.Role.ADMIN or user.is_staff:
            return reverse_lazy("staff:dashboard")
        if user.role == User.Role.SPONSOR:
            return reverse_lazy("sponsors:my_listing")
        return reverse_lazy("sponsors:browse")


class PhoneLogoutView(LogoutView):
    next_page = reverse_lazy("home")


def age_gate(request):
    if request.method == "POST":
        if request.POST.get("is_adult"):
            request.session["adult_ok"] = True
            if request.user.is_authenticated:
                request.user.is_adult_confirmed = True
                request.user.save(update_fields=["is_adult_confirmed"])
            return redirect(request.GET.get("next") or "home")
        messages.error(request, "You must be 18 or older to enter this site.")
    return render(request, "accounts/age_gate.html")


def join_lady(request):
    if request.user.is_authenticated:
        if request.user.role == User.Role.LADY:
            return redirect("sponsors:browse")
        return redirect("home")
    form = LadyEnterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        user = User.objects.filter(phone=phone).first()
        if user and user.role != User.Role.LADY:
            form.add_error("phone", "This number is already used as a sponsor or staff account.")
        else:
            if not user:
                user = User.objects.create_user(
                    phone=phone,
                    password=None,
                    role=User.Role.LADY,
                    is_adult_confirmed=True,
                )
            else:
                user.is_adult_confirmed = True
                user.save(update_fields=["is_adult_confirmed"])
            request.session["adult_ok"] = True
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("sponsors:browse")
    return render(request, "accounts/join.html", {"form": form, "join_role": "lady"})


def join_sponsor(request):
    if request.user.is_authenticated:
        return redirect("sponsors:my_listing")
    form = SponsorJoinForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.role = User.Role.SPONSOR
        user.is_adult_confirmed = True
        user.save()
        request.session["adult_ok"] = True
        login(request, user)
        messages.success(request, "Create your sponsor card, then pay to go live.")
        return redirect("sponsors:edit_listing")
    return render(request, "accounts/join.html", {"form": form, "join_role": "sponsor"})


@login_required
def my_number(request):
    return render(request, "accounts/my_number.html")
