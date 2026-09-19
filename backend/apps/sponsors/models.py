from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import CITY_CHOICES


class SponsorProfile(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_PAY = "pending_pay", "Waiting listing payment"
        LIVE = "live", "Live"
        PAUSED = "paused", "Paused"

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sponsor_profile",
        null=True,
        blank=True,
    )
    public_name = models.CharField(max_length=80)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(21), MaxValueValidator(80)])
    city = models.CharField(max_length=80, choices=CITY_CHOICES)
    lifestyle = models.CharField(
        max_length=120,
        help_text="Short tags, e.g. travel, cars, dinners",
    )
    preference = models.CharField(
        max_length=120,
        blank=True,
        help_text="Who he prefers to meet, e.g. 22-30, same city",
    )
    teaser = models.CharField(max_length=180, help_text="Shown before payment")
    full_bio = models.TextField(help_text="Shown after the lady pays 15,000 TZS")
    photo = models.ImageField(upload_to="sponsors/", blank=True)
    accent = models.CharField(max_length=12, default="#C9A227")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    listing_paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city", "age"]

    def __str__(self):
        return f"{self.public_name} · {self.city}"

    def is_live(self):
        return self.status == self.Status.LIVE

    def mark_live(self):
        self.status = self.Status.LIVE
        self.listing_paid_at = timezone.now()
        self.save(update_fields=["status", "listing_paid_at", "updated_at"])

    def initials(self):
        parts = self.public_name.split()
        return "".join(p[0] for p in parts[:2]).upper() or "S"

    def card_photo(self):
        if self.photo:
            return self.photo.url
        from django.templatetags.static import static

        key = (self.public_name.split() or ["sponsor"])[0].lower()
        return static(f"img/sponsors/{key}.jpg")


class Unlock(models.Model):
    lady = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="unlocks",
    )
    sponsor = models.ForeignKey(
        SponsorProfile,
        on_delete=models.CASCADE,
        related_name="unlocks",
    )
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.PROTECT,
        related_name="unlock",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lady", "sponsor")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.lady.phone} unlocked {self.sponsor.public_name}"
