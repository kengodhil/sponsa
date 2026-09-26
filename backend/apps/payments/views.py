import json
import secrets
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.accounts.phone import normalize_tz_phone, phone_is_valid
from apps.sponsors.models import ChatAccess, SponsorProfile, Unlock

from .models import Payment
from .services import apply_paid_payment
from .snippe import SnippeClient, SnippeError


def _new_order_id():
    return secrets.token_hex(6)


def _webhook_url(request):
    return settings.PUBLIC_BASE_URL.rstrip("/") + reverse("payments:webhook")


def _ensure_user_from_phone(request, raw_phone):
    """Create or fetch user by phone and sign them in — no separate login page."""
    phone = normalize_tz_phone(raw_phone)
    if not phone_is_valid(phone):
        return None
    if request.user.is_authenticated:
        if normalize_tz_phone(request.user.phone) == phone:
            return request.user
    user, created = User.objects.get_or_create(
        phone=phone,
        defaults={
            "role": User.Role.LADY,
            "is_adult_confirmed": True,
            "display_name": phone[-4:],
        },
    )
    if not user.is_adult_confirmed:
        user.is_adult_confirmed = True
        user.save(update_fields=["is_adult_confirmed"])
    request.session["adult_ok"] = True
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return user


def _send_to_snippe(request, payment, remarks):
    client = SnippeClient()
    name = payment.user.get_display_label() or "User"
    parts = name.split(None, 1)
    first = parts[0] if parts else "User"
    last = parts[1] if len(parts) > 1 else "Customer"
    try:
        result = client.create_mobile_payment(
            amount=payment.amount,
            phone=payment.msisdn,
            firstname=first,
            lastname=last,
            webhook_url=_webhook_url(request),
            metadata={
                "order_id": payment.order_id,
                "purpose": payment.purpose,
                "sponsor_id": payment.sponsor_id,
                "remarks": remarks,
            },
        )
        data = result.get("data") or result
        ref = str(data.get("reference") or "")
        payment.raw_response = result
        payment.provider_reference = ref
        payment.selcom_reference = ref
        payment.provider_result = str(data.get("status") or "pending")
        payment.selcom_result = payment.provider_result
        payment.provider_message = remarks
        payment.selcom_message = remarks
        payment.transid = ref or payment.transid
        payment.save()
    except SnippeError as exc:
        payment.status = Payment.Status.FAILED
        payment.provider_message = str(exc)
        payment.selcom_message = str(exc)
        payment.save()
        messages.error(request, "Payment could not start. Try again.")
        return redirect("payments:status", order_id=payment.order_id)
    return redirect("payments:status", order_id=payment.order_id)


@require_POST
def start_unlock(request, pk):
    """First payment: 10,000 TZS — unlock full profile. Auto-login from phone."""
    profile = get_object_or_404(SponsorProfile, pk=pk, status=SponsorProfile.Status.LIVE)
    phone = request.POST.get("phone") or (request.user.phone if request.user.is_authenticated else "")
    user = _ensure_user_from_phone(request, phone)
    if not user:
        messages.error(request, "Enter a valid Tanzania phone number.")
        return redirect("sponsors:detail", pk=pk)
    if Unlock.objects.filter(user=user, sponsor=profile).exists():
        return redirect("sponsors:detail", pk=pk)
    payment = Payment.objects.create(
        user=user,
        sponsor=profile,
        purpose=Payment.Purpose.UNLOCK,
        amount=settings.UNLOCK_FEE_TZS,
        msisdn=normalize_tz_phone(phone),
        order_id=_new_order_id(),
        transid="T" + uuid.uuid4().hex[:12].upper(),
        status=Payment.Status.PENDING,
    )
    return _send_to_snippe(request, payment, f"Unlock {profile.public_name}")


@require_POST
def start_chat(request, pk):
    """Second payment: 5,000 TZS — open chat. Auto-login from phone if needed."""
    profile = get_object_or_404(SponsorProfile, pk=pk, status=SponsorProfile.Status.LIVE)
    phone = request.POST.get("phone") or (request.user.phone if request.user.is_authenticated else "")
    user = _ensure_user_from_phone(request, phone)
    if not user:
        messages.error(request, "Enter a valid Tanzania phone number.")
        return redirect("sponsors:detail", pk=pk)
    if not Unlock.objects.filter(user=user, sponsor=profile).exists():
        messages.error(request, "Unlock the profile first.")
        return redirect("sponsors:detail", pk=pk)
    if ChatAccess.objects.filter(user=user, sponsor=profile).exists():
        return redirect("messaging:thread", pk=pk)
    payment = Payment.objects.create(
        user=user,
        sponsor=profile,
        purpose=Payment.Purpose.CHAT,
        amount=settings.CHAT_FEE_TZS,
        msisdn=normalize_tz_phone(phone),
        order_id=_new_order_id(),
        transid="T" + uuid.uuid4().hex[:12].upper(),
        status=Payment.Status.PENDING,
    )
    return _send_to_snippe(request, payment, f"Chat {profile.public_name}")


@login_required
def payment_status(request, order_id):
    payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
    if payment.status != Payment.Status.PAID:
        _refresh_from_snippe(payment)
    client = SnippeClient()
    return render(
        request,
        "payments/status.html",
        {"payment": payment, "sandbox": client.sandbox and not client.api_key},
    )


@login_required
@require_POST
def demo_confirm(request, order_id):
    payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
    client = SnippeClient()
    if not (client.sandbox and not client.api_key):
        messages.error(request, "Demo confirm only works in sandbox without live keys.")
        return redirect("payments:status", order_id=order_id)
    apply_paid_payment(payment, message="Demo payment confirmed")
    messages.success(request, "Payment confirmed.")
    if payment.purpose == Payment.Purpose.UNLOCK and payment.sponsor_id:
        return redirect("sponsors:detail", pk=payment.sponsor_id)
    if payment.purpose == Payment.Purpose.CHAT and payment.sponsor_id:
        return redirect("messaging:thread", pk=payment.sponsor_id)
    return redirect("sponsors:browse")


@csrf_exempt
@require_POST
def snippe_webhook(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = request.POST.dict()
    data = payload.get("data") or payload
    reference = data.get("reference") or payload.get("reference")
    status = str(data.get("status") or payload.get("status") or "").lower()
    meta = data.get("metadata") or payload.get("metadata") or {}
    order_id = meta.get("order_id")
    payment = None
    if order_id:
        payment = Payment.objects.filter(order_id=order_id).first()
    if not payment and reference:
        payment = Payment.objects.filter(provider_reference=reference).first()
        if not payment:
            payment = Payment.objects.filter(selcom_reference=reference).first()
    if not payment:
        return JsonResponse({"ok": False, "reason": "unknown"}, status=404)
    payment.raw_response = {**(payment.raw_response or {}), "webhook": payload}
    payment.save(update_fields=["raw_response"])
    if status in {"completed", "success", "paid"}:
        apply_paid_payment(payment, message=str(data.get("message") or "Webhook paid"))
    return JsonResponse({"ok": True})


def _refresh_from_snippe(payment):
    client = SnippeClient()
    ref = payment.provider_reference or payment.selcom_reference
    if not ref or (client.sandbox and not client.api_key):
        return
    try:
        result = client.get_payment(ref)
    except SnippeError:
        return
    data = result.get("data") or result
    payment.raw_response = {**(payment.raw_response or {}), "status": result}
    st = str(data.get("status") or "").lower()
    payment.provider_result = st
    payment.selcom_result = st
    payment.save()
    if st in {"completed", "success", "paid"}:
        apply_paid_payment(payment, message="Status poll paid")


@login_required
def health(_request):
    return HttpResponse("ok")
