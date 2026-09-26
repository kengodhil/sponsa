from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import CITY_CHOICES


class SponsorProfile(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        LIVE = "live", "Live"
        PAUSED = "paused", "Paused"

    class Gender(models.TextChoices):
        MAN = "man", "Man"
        WOMAN = "woman", "Woman"

    class Badge(models.TextChoices):
        NONE = "", "None"
        NEW = "new", "New"
        FEATURED = "featured", "Featured"
        POPULAR = "popular", "Popular"
        VERIFIED = "verified", "Verified"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="sponsor_profiles",
        null=True,
        blank=True,
    )
    public_name = models.CharField(max_length=80)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MAN)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(21), MaxValueValidator(80)])
    city = models.CharField(max_length=80, choices=CITY_CHOICES)
    lifestyle = models.CharField(max_length=120, blank=True, help_text="Short tags")
    preference = models.CharField(max_length=120, blank=True)
    teaser = models.CharField(max_length=180, help_text="Shown before payment")
    full_bio = models.TextField(help_text="Shown after unlock payment")
    photo = models.ImageField(upload_to="sponsors/", blank=True)
    badge = models.CharField(max_length=20, choices=Badge.choices, default=Badge.NONE, blank=True)
    accent = models.CharField(max_length=12, default="#6b4eff")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.public_name} · {self.city}"

    def is_live(self):
        return self.status == self.Status.LIVE

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
    """First payment: unlock full profile (10,000 TZS)."""
    user = models.ForeignKey(
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
        unique_together = ("user", "sponsor")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone} unlocked {self.sponsor.public_name}"


class ChatAccess(models.Model):
    """Second payment: open chat (5,000 TZS)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_accesses",
    )
    sponsor = models.ForeignKey(
        SponsorProfile,
        on_delete=models.CASCADE,
        related_name="chat_accesses",
    )
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.PROTECT,
        related_name="chat_access",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "sponsor")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone} chat {self.sponsor.public_name}"
