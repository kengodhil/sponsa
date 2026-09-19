from django.conf import settings


def site_branding(request):
    return {
        "brand": "Sponsa",
        "unlock_fee": settings.UNLOCK_FEE_TZS,
        "listing_fee": settings.LISTING_FEE_TZS,
        "selcom_sandbox": settings.SELCOM_SANDBOX,
    }
