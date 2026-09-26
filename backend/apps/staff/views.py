import csv
import io

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.forms import PhoneAuthForm
from apps.accounts.models import User
from apps.payments.models import Payment
from apps.sponsors.forms import SponsorProfileForm, SponsorUploadForm
from apps.sponsors.models import ChatAccess, SponsorProfile, Unlock


def staff_only(user):
    return user.is_authenticated and (user.is_staff or user.role == User.Role.ADMIN)


staff_required = user_passes_test(staff_only, login_url="staff:login")


def admin_login(request):
    """Simple admin login — phone/admin + password."""
    if request.user.is_authenticated and staff_only(request.user):
        return redirect("staff:dashboard")
    form = PhoneAuthForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not (user.is_staff or user.role == User.Role.ADMIN):
            messages.error(request, "Not an admin account.")
            return render(request, "staff/admin_login.html", {"form": form})
        login(request, user)
        return redirect("staff:dashboard")
    return render(request, "staff/admin_login.html", {"form": form})


@staff_required
def dashboard(request):
    return render(
        request,
        "staff/dashboard.html",
        {
            "profiles": SponsorProfile.objects.all().order_by("-created_at"),
            "payments": Payment.objects.select_related("user", "sponsor")[:30],
            "unlocks": Unlock.objects.select_related("user", "sponsor")[:30],
            "chats": ChatAccess.objects.select_related("user", "sponsor")[:30],
        },
    )


@staff_required
def user_detail(request, pk):
    person = get_object_or_404(User, pk=pk)
    return render(request, "staff/user_detail.html", {"person": person})


@staff_required
def create_profile(request):
    form = SponsorProfileForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.status = SponsorProfile.Status.LIVE
        profile.save()
        messages.success(request, f"{profile.public_name} is live.")
        return redirect("staff:dashboard")
    return render(request, "staff/profile_form.html", {"form": form, "title": "Add sponsor"})


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
def csv_upload(request):
    form = SponsorUploadForm(request.POST or None, request.FILES or None)
    created = 0
    if request.method == "POST" and form.is_valid():
        raw = form.cleaned_data["csv_file"].read()
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            name = (row.get("public_name") or row.get("name") or "").strip()
            if not name:
                continue
            gender = (row.get("gender") or "man").strip().lower()
            if gender not in ("man", "woman"):
                gender = "man"
            badge = (row.get("badge") or "").strip().lower()
            SponsorProfile.objects.create(
                public_name=name,
                gender=gender,
                age=int(row.get("age") or 40),
                city=(row.get("city") or "Dar es Salaam").strip(),
                lifestyle=(row.get("lifestyle") or "").strip(),
                preference=(row.get("preference") or "").strip(),
                teaser=(row.get("teaser") or "Private sponsor.").strip(),
                full_bio=(row.get("full_bio") or row.get("bio") or "Full profile.").strip(),
                badge=badge,
                status=SponsorProfile.Status.LIVE,
            )
            created += 1
        messages.success(request, f"Uploaded {created} sponsors.")
        return redirect("staff:dashboard")
    return render(request, "staff/csv_upload.html", {"form": form})
