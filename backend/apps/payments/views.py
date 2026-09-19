import json
import secrets
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.accounts.phone import normalize_tz_phone
from apps.sponsors.models import SponsorProfile, Unlock

from .models import Payment
from .selcom import SelcomClient, SelcomError
from .services import apply_paid_payment


def _new_order_id():
    return secrets.token_hex(6)


def _new_transid():
    return "T" + uuid.uuid4().hex[:12].upper()


def _webhook_url(request):
    return settings.PUBLIC_BASE_URL.rstrip("/") + reverse("payments:webhook")


@login_required
@require_POST
def start_unlock(request, pk):
    if request.user.role != User.Role.LADY:
        messages.error(request, "Only ladies can pay to unlock a profile.")
        return redirect("sponsors:detail", pk=pk)
    profile = get_object_or_404(SponsorProfile, pk=pk, status=SponsorProfile.Status.LIVE)
    if Unlock.objects.filter(lady=request.user, sponsor=profile).exists():
        return redirect("messaging:thread", pk=profile.pk)
    payment = Payment.objects.create(
        user=request.user,
        sponsor=profile,
        purpose=Payment.Purpose.UNLOCK,
        amount=settings.UNLOCK_FEE_TZS,
        msisdn=normalize_tz_phone(request.user.phone),
        order_id=_new_order_id(),
        transid=_new_transid(),
        status=Payment.Status.PENDING,
    )
    return _send_to_selcom(request, payment, f"Unlock {profile.public_name}")


@login_required
@require_POST
def start_listing(request):
    if request.user.role != User.Role.SPONSOR:
        messages.error(request, "Only sponsor men pay to be posted.")
        return redirect("home")
    profile = request.user.get_listing()
    if not profile:
        messages.error(request, "Fill your profile first.")
        return redirect("sponsors:edit_listing")
    if profile.status == SponsorProfile.Status.LIVE:
        return redirect("sponsors:my_listing")
    payment = Payment.objects.create(
        user=request.user,
        sponsor=profile,
        purpose=Payment.Purpose.LISTING,
        amount=settings.LISTING_FEE_TZS,
        msisdn=normalize_tz_phone(request.user.phone),
        order_id=_new_order_id(),
        transid=_new_transid(),
        status=Payment.Status.PENDING,
    )
    profile.status = SponsorProfile.Status.PENDING_PAY
    profile.save(update_fields=["status"])
    return _send_to_selcom(request, payment, f"Post card {profile.public_name}")


def _send_to_selcom(request, payment, remarks):
    client = SelcomClient()
    try:
        order = client.create_order(
            order_id=payment.order_id,
            buyer_name=payment.user.get_display_label(),
            buyer_phone=payment.msisdn,
            amount=payment.amount,
            webhook=_webhook_url(request),
            remarks=remarks,
        )
        push = client.wallet_push(payment.transid, payment.order_id, payment.msisdn)
        payment.raw_response = {"order": order, "wallet": push}
        payment.selcom_reference = str(order.get("reference") or "")
        payment.selcom_result = str(push.get("result") or order.get("result") or "")
        payment.selcom_message = str(push.get("message") or order.get("message") or "")
        payment.save()
    except SelcomError as exc:
        payment.status = Payment.Status.FAILED
        payment.selcom_message = str(exc)
        payment.save()
        messages.error(request, "Payment could not start. Try again.")
        return redirect("payments:status", order_id=payment.order_id)
    return redirect("payments:status", order_id=payment.order_id)


@login_required
def payment_status(request, order_id):
    payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
    if payment.status != Payment.Status.PAID:
        _refresh_from_selcom(payment)
    return render(request, "payments/status.html", {"payment": payment, "sandbox": SelcomClient().sandbox})


@login_required
@require_POST
def demo_confirm(request, order_id):
    payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
    if not SelcomClient().sandbox:
        messages.error(request, "Demo confirm is only available before live keys are set.")
        return redirect("payments:status", order_id=order_id)
    apply_paid_payment(payment, message="Demo payment confirmed")
    messages.success(request, "Payment confirmed. Full profile and chat are open.")
    if payment.purpose == Payment.Purpose.UNLOCK and payment.sponsor_id:
        return redirect("sponsors:detail", pk=payment.sponsor_id)
    return redirect("sponsors:my_listing")


@csrf_exempt
@require_POST
def selcom_webhook(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = request.POST.dict()
    order_id = payload.get("order_id") or payload.get("orderId")
    result = str(payload.get("result") or payload.get("payment_status") or "").upper()
    if not order_id:
        return JsonResponse({"ok": False}, status=400)
    payment = Payment.objects.filter(order_id=order_id).first()
    if not payment:
        return JsonResponse({"ok": False, "reason": "unknown order"}, status=404)
    payment.raw_response = {**(payment.raw_response or {}), "webhook": payload}
    payment.save(update_fields=["raw_response"])
    if result in {"SUCCESS", "PAID", "COMPLETED", "000"}:
        apply_paid_payment(payment, message=str(payload.get("message") or "Webhook paid"))
    return JsonResponse({"ok": True})


def _refresh_from_selcom(payment):
    client = SelcomClient()
    if client.sandbox:
        return
    try:
        data = client.order_status(payment.order_id)
    except SelcomError:
        return
    payment.raw_response = {**(payment.raw_response or {}), "status": data}
    result = str(data.get("result") or "").upper()
    payment.selcom_result = result
    payment.selcom_message = str(data.get("message") or "")
    payment.save()
    if result in {"SUCCESS", "PAID", "COMPLETED"}:
        apply_paid_payment(payment, message=payment.selcom_message)


@login_required
def health(_request):
    return HttpResponse("ok")
