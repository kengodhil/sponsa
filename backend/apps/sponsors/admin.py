from django.contrib import admin

from .models import ChatAccess, SponsorProfile, Unlock


@admin.register(SponsorProfile)
class SponsorProfileAdmin(admin.ModelAdmin):
    list_display = ("public_name", "gender", "age", "city", "badge", "status", "created_at")
    list_filter = ("status", "gender", "badge", "city")
    search_fields = ("public_name", "city", "teaser")
    list_editable = ("status", "badge")
    fields = (
        "public_name",
        "gender",
        "age",
        "city",
        "lifestyle",
        "preference",
        "teaser",
        "full_bio",
        "photo",
        "badge",
        "status",
        "owner",
    )


@admin.register(Unlock)
class UnlockAdmin(admin.ModelAdmin):
    list_display = ("user", "sponsor", "created_at")
    raw_id_fields = ("user", "sponsor", "payment")


@admin.register(ChatAccess)
class ChatAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "sponsor", "created_at")
    raw_id_fields = ("user", "sponsor", "payment")
