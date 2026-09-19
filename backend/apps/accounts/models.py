from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .phone import normalize_tz_phone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("A mobile number is required.")
        phone = normalize_tz_phone(phone)
        user = self.model(phone=phone, username=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_adult_confirmed", True)
        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        LADY = "lady", "Lady"
        SPONSOR = "sponsor", "Sponsor man"
        ADMIN = "admin", "Admin"

    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField("mobile number", max_length=15, unique=True)
    display_name = models.CharField(max_length=80, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LADY)
    is_adult_confirmed = models.BooleanField(default=False)
    city = models.CharField(max_length=80, blank=True)
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(80)],
    )
    looking_for = models.CharField(
        max_length=80,
        blank=True,
        help_text="Age or lifestyle preference, e.g. 35-55, generous, travel",
    )

    objects = UserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_display_label()} ({self.phone})"

    def get_display_label(self):
        return self.display_name or self.phone

    def get_listing(self):
        from apps.sponsors.models import SponsorProfile

        return SponsorProfile.objects.filter(owner=self).first()

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_tz_phone(self.phone)
            self.username = self.phone
        super().save(*args, **kwargs)


TZ_CITIES = [
    "Dar es Salaam",
    "Arusha",
    "Mwanza",
    "Dodoma",
    "Zanzibar",
    "Mbeya",
    "Moshi",
    "Morogoro",
    "Tanga",
    "Dodoma",
    "Iringa",
    "Other",
]
# unique while preserving order
TZ_CITIES = list(dict.fromkeys(TZ_CITIES))
CITY_CHOICES = [(city, city) for city in TZ_CITIES]
