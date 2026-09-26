from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages as flash

from apps.accounts.models import User
from apps.sponsors.models import ChatAccess, SponsorProfile, Unlock

from .forms import MessageForm
from .models import Message


def _can_thread(user, profile):
    if user.is_staff or user.role == User.Role.ADMIN:
        return True
    return ChatAccess.objects.filter(user=user, sponsor=profile).exists()


@login_required
def inbox(request):
    if request.user.role == User.Role.SPONSOR:
        return redirect("sponsors:browse")
    chats = ChatAccess.objects.filter(user=request.user).select_related("sponsor")
    return render(request, "messaging/inbox.html", {"mode": "lady", "unlocks": chats})


@login_required
def thread(request, pk):
    profile = get_object_or_404(SponsorProfile, pk=pk)
    if not _can_thread(request.user, profile):
        if Unlock.objects.filter(user=request.user, sponsor=profile).exists():
            flash.error(request, "Pay chat fee to message this sponsor.")
        else:
            flash.error(request, "Unlock the profile first.")
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
    if request.user.role != User.Role.ADMIN and not request.user.is_staff:
        chat = chat.filter(Q(sender=request.user) | Q(sender=profile.owner_id))
    return render(
        request,
        "messaging/thread.html",
        {"profile": profile, "form": form, "chat": chat},
    )
