from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages as flash

from apps.accounts.models import User
from apps.sponsors.models import SponsorProfile, Unlock

from .forms import MessageForm
from .models import Message


def _can_thread(user, profile):
    if user.is_staff or user.role == User.Role.ADMIN:
        return True
    if user.role == User.Role.SPONSOR and user.get_listing() == profile:
        return True
    if user.role == User.Role.LADY:
        return Unlock.objects.filter(lady=user, sponsor=profile).exists()
    return False


@login_required
def inbox(request):
    if request.user.role == User.Role.SPONSOR:
        profile = request.user.get_listing()
        ladies = []
        if profile:
            lady_ids = (
                Message.objects.filter(sponsor=profile)
                .exclude(sender=request.user)
                .values_list("sender_id", "sender__display_name", "sender__phone")
                .distinct()
            )
            ladies = [{"id": row[0], "name": row[1] or row[2], "phone": row[2]} for row in lady_ids]
        return render(
            request,
            "messaging/inbox.html",
            {"mode": "sponsor", "profile": profile, "ladies": ladies},
        )
    unlocks = Unlock.objects.filter(lady=request.user).select_related("sponsor")
    return render(request, "messaging/inbox.html", {"mode": "lady", "unlocks": unlocks})


@login_required
def thread(request, pk):
    profile = get_object_or_404(SponsorProfile, pk=pk)
    if not _can_thread(request.user, profile):
        flash.error(request, "Pay to unlock this profile before you can message.")
        return redirect("sponsors:detail", pk=pk)
    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        msg = form.save(commit=False)
        msg.sender = request.user
        msg.sponsor = profile
        msg.save()
        flash.success(request, "Message sent.")
        return redirect("messaging:thread", pk=pk)
    chat = Message.objects.filter(sponsor=profile)
    if request.user.role == User.Role.LADY:
        chat = chat.filter(Q(sender=request.user) | Q(sender=profile.owner_id))
    return render(
        request,
        "messaging/thread.html",
        {"profile": profile, "form": form, "chat": chat},
    )
