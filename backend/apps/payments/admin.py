from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "purpose", "amount", "msisdn", "status", "created_at")
    list_filter = ("purpose", "status")
    search_fields = ("order_id", "msisdn", "user__phone", "transid")
