from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import PhoneAuthForm
from apps.accounts.models import User
from apps.payments.models import Payment
from apps.sponsors.forms import SponsorProfileForm
from apps.sponsors.models import SponsorProfile

from .forms import AdminChangePasswordForm, AdminCreateForm


def staff_only(user):
    """Only authenticated staff or admin role."""
    return bool(
        user
        and user.is_authenticated
        and user.is_active
        and (user.is_staff or getattr(user, "role", None) == User.Role.ADMIN)
    )


staff_required = user_passes_test(staff_only, login_url="staff:login")


def admin_login(request):
    """Admin-only login. Rejects regular users even with valid password."""
    if request.user.is_authenticated and staff_only(request.user):
        return redirect("staff:dashboard")

    fails = request.session.get("admin_login_fails", 0)
    form = PhoneAuthForm(request, data=request.POST or None)

    if request.method == "POST":
        if fails >= 8:
            messages.error(request, "Too many attempts. Try again later.")
            return render(request, "staff/admin_login.html", {"form": form})

        if form.is_valid():
            user = form.get_user()
            if not staff_only(user):
                request.session["admin_login_fails"] = fails + 1
                messages.error(request, "Not an admin account.")
                return render(request, "staff/admin_login.html", {"form": form})
            request.session.cycle_key()
            request.session.pop("admin_login_fails", None)
            login(request, user)
            return redirect("staff:dashboard")

        request.session["admin_login_fails"] = fails + 1
        messages.error(request, "Invalid phone or password.")

    return render(request, "staff/admin_login.html", {"form": form})


@staff_required
@require_http_methods(["POST"])
def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out.")
    return redirect("staff:login")


@staff_required
def dashboard(request):
    return render(
        request,
        "staff/dashboard.html",
        {
            "profiles": SponsorProfile.objects.all().order_by("-created_at"),
            "payments": Payment.objects.select_related("user", "sponsor")[:25],
            "admins": User.objects.filter(
                is_active=True,
            )
            .filter(models_q_staff_or_admin())
            .order_by("display_name", "phone"),
        },
    )


def models_q_staff_or_admin():
    from django.db.models import Q

    return Q(is_staff=True) | Q(role=User.Role.ADMIN)


@staff_required
def create_profile(request):
    form = SponsorProfileForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        if not profile.status:
            profile.status = SponsorProfile.Status.LIVE
        profile.save()
        messages.success(request, f"{profile.public_name} saved.")
        return redirect("staff:dashboard")
    return render(
        request,
        "staff/profile_form.html",
        {"form": form, "title": "Add sponsor", "profile": None},
    )


@staff_required
def edit_profile(request, pk):
    profile = get_object_or_404(SponsorProfile, pk=pk)
    form = SponsorProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sponsor updated.")
        return redirect("staff:dashboard")
    return render(
        request,
        "staff/profile_form.html",
        {"form": form, "title": "Edit sponsor", "profile": profile},
    )


@staff_required
@require_http_methods(["POST"])
def delete_profile(request, pk):
    profile = get_object_or_404(SponsorProfile, pk=pk)
    name = profile.public_name
    profile.delete()
    messages.success(request, f"{name} removed.")
    return redirect("staff:dashboard")


@staff_required
def change_password(request):
    form = AdminChangePasswordForm(request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated successfully.")
        return redirect("staff:dashboard")
    return render(
        request,
        "staff/change_password.html",
        {"form": form},
    )


@staff_required
def add_admin(request):
    form = AdminCreateForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(
            request,
            f"Admin created: {user.get_display_label()} ({user.phone}).",
        )
        return redirect("staff:dashboard")
    return render(
        request,
        "staff/add_admin.html",
        {"form": form},
    )
