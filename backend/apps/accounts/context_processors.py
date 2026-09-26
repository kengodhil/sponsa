from django.conf import settings


def site_branding(request):
    return {
        "brand": "Sponsors Connection",
        "unlock_fee": settings.UNLOCK_FEE_TZS,
        "chat_fee": settings.CHAT_FEE_TZS,
        "listing_fee": settings.LISTING_FEE_TZS,
        "snippe_sandbox": getattr(settings, "SNIPPE_SANDBOX", True),
        "selcom_sandbox": getattr(settings, "SNIPPE_SANDBOX", True),
    }
