from django.db import transaction
from django.utils import timezone

from apps.sponsors.models import SponsorProfile, Unlock

from .models import Payment


def apply_paid_payment(payment, message="Paid"):
    with transaction.atomic():
        locked = Payment.objects.select_for_update().get(pk=payment.pk)
        if locked.status == Payment.Status.PAID:
            return locked
        locked.mark_paid(message=message)
        if locked.purpose == Payment.Purpose.UNLOCK and locked.sponsor_id:
            Unlock.objects.get_or_create(
                lady=locked.user,
                sponsor=locked.sponsor,
                defaults={"payment": locked},
            )
        if locked.purpose == Payment.Purpose.LISTING and locked.sponsor_id:
            profile = locked.sponsor
            profile.status = SponsorProfile.Status.LIVE
            profile.listing_paid_at = timezone.now()
            profile.save(update_fields=["status", "listing_paid_at", "updated_at"])
        return locked
