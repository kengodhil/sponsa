from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from apps.accounts.models import User
from apps.accounts.views import adult_required

from .forms import SponsorFilterForm, SponsorProfileForm
from .models import ChatAccess, SponsorProfile, Unlock


def home(request):
    live = SponsorProfile.objects.filter(status=SponsorProfile.Status.LIVE)
    return render(
        request,
        "pages/home.html",
        {
            "live_count": live.count(),
            "featured": live[:8],
        },
    )


@adult_required
@login_required
def browse(request):
    form = SponsorFilterForm(request.GET or None)
    profiles = SponsorProfile.objects.filter(status=SponsorProfile.Status.LIVE)
    city = ""
    min_age = 21
    max_age = 80
    preference = ""
    if form.is_valid():
        city = (form.cleaned_data.get("city") or "").strip()
        min_age = form.cleaned_data.get("min_age") or 21
        max_age = form.cleaned_data.get("max_age") or 80
        preference = (form.cleaned_data.get("preference") or "").strip()
    profiles = profiles.filter(age__gte=min_age, age__lte=max_age)
    if preference:
        profiles = profiles.filter(
            Q(lifestyle__icontains=preference)
            | Q(preference__icontains=preference)
            | Q(teaser__icontains=preference)
            | Q(city__icontains=preference)
            | Q(public_name__icontains=preference)
        )
    if city:
        profiles = profiles.filter(city__icontains=city)
    unlocked_ids = set(
        Unlock.objects.filter(user=request.user).values_list("sponsor_id", flat=True)
    )
    return render(
        request,
        "sponsors/browse.html",
        {
            "form": form,
            "profiles": profiles,
            "unlocked_ids": unlocked_ids,
            "focus_city": city,
        },
    )


@adult_required
@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(SponsorProfile, pk=pk, status=SponsorProfile.Status.LIVE)
    unlocked = False
    can_chat = False
    if request.user.is_staff or request.user.role == User.Role.ADMIN:
        unlocked = True
        can_chat = True
    else:
        unlocked = Unlock.objects.filter(user=request.user, sponsor=profile).exists()
        can_chat = ChatAccess.objects.filter(user=request.user, sponsor=profile).exists()
    return render(
        request,
        "sponsors/detail.html",
        {
            "profile": profile,
            "unlocked": unlocked,
            "can_chat": can_chat,
        },
    )


@login_required
def my_listing(request):
    messages.info(request, "Only admin can add sponsors.")
    return redirect("sponsors:browse")


@login_required
def edit_listing(request):
    messages.info(request, "Only admin can add sponsors.")
    return redirect("sponsors:browse")
