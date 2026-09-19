from django.conf import settings
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    class Purpose(models.TextChoices):
        UNLOCK = "unlock", "Unlock one sponsor"
        LISTING = "listing", "Post sponsor card"

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PENDING = "pending", "Waiting payment"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    sponsor = models.ForeignKey(
        "sponsors.SponsorProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=8, default="TZS")
    msisdn = models.CharField(max_length=15)
    order_id = models.CharField(max_length=40, unique=True)
    transid = models.CharField(max_length=40, blank=True)
    selcom_reference = models.CharField(max_length=80, blank=True)
    selcom_result = models.CharField(max_length=40, blank=True)
    selcom_message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    raw_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} {self.amount} {self.status}"

    def mark_paid(self, message="Paid"):
        self.status = self.Status.PAID
        self.selcom_result = "SUCCESS"
        self.selcom_message = message
        self.paid_at = timezone.now()
        self.save()
