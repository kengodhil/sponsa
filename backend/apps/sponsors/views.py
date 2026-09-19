from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from apps.accounts.models import User
from apps.accounts.views import adult_required

from .forms import SponsorFilterForm, SponsorProfileForm
from .models import SponsorProfile, Unlock


def home(request):
    live_count = SponsorProfile.objects.filter(status=SponsorProfile.Status.LIVE).count()
    return render(request, "pages/home.html", {"live_count": live_count})


@adult_required
@login_required
def browse(request):
    if request.user.role == User.Role.SPONSOR:
        return redirect("sponsors:my_listing")
    form = SponsorFilterForm(request.GET or None)
    profiles = SponsorProfile.objects.filter(status=SponsorProfile.Status.LIVE)
    city = request.user.city
    min_age = 21
    max_age = 80
    preference = ""
    if form.is_valid():
        city = form.cleaned_data.get("city") or request.user.city
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
        )
    if city:
        profiles = profiles.annotate(
            nearby=Case(
                When(city__iexact=city, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("nearby", "age")
    unlocked_ids = set(
        Unlock.objects.filter(lady=request.user).values_list("sponsor_id", flat=True)
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
    if request.user.role == User.Role.LADY:
        unlocked = Unlock.objects.filter(lady=request.user, sponsor=profile).exists()
    elif request.user.is_staff or request.user.role == User.Role.ADMIN:
        unlocked = True
    elif request.user.get_listing() and request.user.get_listing().pk == profile.pk:
        unlocked = True
    return render(
        request,
        "sponsors/detail.html",
        {"profile": profile, "unlocked": unlocked},
    )


@login_required
def my_listing(request):
    if request.user.role != User.Role.SPONSOR and not request.user.is_staff:
        return redirect("sponsors:browse")
    profile = request.user.get_listing()
    return render(request, "sponsors/my_listing.html", {"profile": profile})


@login_required
def edit_listing(request):
    if request.user.role != User.Role.SPONSOR:
        messages.error(request, "Only sponsor men can publish a card.")
        return redirect("home")
    profile = request.user.get_listing()
    form = SponsorProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        listing = form.save(commit=False)
        listing.owner = request.user
        if not listing.status or listing.status == SponsorProfile.Status.DRAFT:
            listing.status = SponsorProfile.Status.DRAFT
        listing.save()
        messages.success(request, "Profile saved. Pay the listing fee to appear for ladies.")
        return redirect("sponsors:my_listing")
    return render(request, "sponsors/edit.html", {"form": form, "profile": profile})
