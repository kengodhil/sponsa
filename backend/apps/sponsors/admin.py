from django.contrib import admin

from .models import SponsorProfile, Unlock


@admin.register(SponsorProfile)
class SponsorProfileAdmin(admin.ModelAdmin):
    list_display = ("public_name", "age", "city", "status", "owner", "listing_paid_at")
    list_filter = ("status", "city")
    search_fields = ("public_name", "lifestyle", "preference", "full_bio")


@admin.register(Unlock)
class UnlockAdmin(admin.ModelAdmin):
    list_display = ("lady", "sponsor", "created_at")
    search_fields = ("lady__phone", "sponsor__public_name")
