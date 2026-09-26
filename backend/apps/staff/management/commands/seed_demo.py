from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.sponsors.models import SponsorProfile


DEMO_MEN = [
    {
        "public_name": "Hassan M.",
        "age": 44,
        "city": "Dar es Salaam",
        "lifestyle": "dinners, travel, quiet luxury",
        "preference": "24-32, same city",
        "teaser": "Oyster Bay evenings. Discreet, generous, no games.",
        "full_bio": "I run a trading desk in Dar. I like calm conversation, good food, and weekend trips to Zanzibar. I support a lady who is honest about her time and her goals. WhatsApp after you unlock.",
        "gender": "man", "badge": "verified", "accent": "#C9A227",
    },
    {
        "public_name": "Daniel K.",
        "age": 38,
        "city": "Arusha",
        "lifestyle": "safari, fitness, cars",
        "preference": "21-30, confident",
        "teaser": "Arusha based. Weekend drives and lodge nights.",
        "full_bio": "I work with lodges around Arusha and Nairobi. I am looking for a lady who enjoys travel, stays private, and can join short trips. I cover travel and a monthly stipend after we meet once.",
        "gender": "man", "badge": "featured", "accent": "#8C2F39",
    },
    {
        "public_name": "Omar S.",
        "age": 51,
        "city": "Zanzibar",
        "lifestyle": "beach, hotels, fashion",
        "preference": "23-35, island or Dar",
        "teaser": "Stone Town sponsor. Soft life, hotel stays, no drama.",
        "full_bio": "Hotel and import business. I spend time between Zanzibar and Dar. I prefer a lady who dresses well, keeps our matter private, and can travel on short notice.",
        "gender": "man", "badge": "popular", "accent": "#1F4E5F",
    },
    {
        "public_name": "Peter L.",
        "age": 47,
        "city": "Mwanza",
        "lifestyle": "business, lakeside, support",
        "preference": "25-34, nearby",
        "teaser": "Lake zone. Practical support, weekly meet-ups.",
        "full_bio": "I own workshops in Mwanza. I am not on this site for chat only. If we match, I help with rent and airtime and we meet when I am in town.",
        "gender": "man", "badge": "new", "accent": "#B56B45",
    },
    {
        "public_name": "James N.",
        "age": 42,
        "city": "Dodoma",
        "lifestyle": "government town, dinners, mentorship",
        "preference": "22-28, educated",
        "teaser": "Capital city. Clear allowance, clear calendar.",
        "full_bio": "I work around Dodoma and fly to Dar. I like a lady who studies or works, speaks sense, and is not chasing ten men at once. Profile unlock shows how to reach me.",
        "gender": "man", "badge": "verified", "accent": "#5C2E91",
    },
    {
        "public_name": "Brian T.",
        "age": 36,
        "city": "Dar es Salaam",
        "lifestyle": "nightlife, gym, gifts",
        "preference": "21-27, Masaki / CBD",
        "teaser": "Younger sponsor energy. City nights and shopping.",
        "full_bio": "Fintech and side businesses in Dar. I move fast. If the chat is good after you unlock, we meet the same week in a public lounge first.",
        "gender": "man", "badge": "featured", "accent": "#9C1F3B",
    },
]

DEMO_WOMEN = [
    {
        "public_name": "Amina R.",
        "age": 29,
        "city": "Dar es Salaam",
        "gender": "woman",
        "badge": "verified",
        "lifestyle": "business, fashion, travel",
        "preference": "35-55, generous",
        "teaser": "Professional business woman and investor.",
        "full_bio": "I run businesses in Dar and invest in property. Looking for a serious connection.",
        "accent": "#ec4899",
    },
    {
        "public_name": "Sofia M.",
        "age": 32,
        "city": "Arusha",
        "gender": "woman",
        "badge": "featured",
        "lifestyle": "luxury, travel, wellness",
        "preference": "40-60",
        "teaser": "Elegant, discreet, based in Arusha and Nairobi.",
        "full_bio": "I divide time between Arusha and travel. Prefer mature, established partners.",
        "accent": "#a855f7",
    },
]

DEMO_MEN = DEMO_MEN + DEMO_WOMEN


def _photo_path(public_name):
    key = (public_name.split() or ["sponsor"])[0].lower()
    return Path(settings.FRONTEND_DIR) / "static" / "img" / "sponsors" / f"{key}.jpg"


def _attach_photo(profile, public_name):
    src = _photo_path(public_name)
    if not src.exists():
        return
    missing = not profile.photo or not profile.photo.storage.exists(profile.photo.name)
    if not missing:
        return
    key = src.name
    with src.open("rb") as fh:
        profile.photo.save(key, File(fh), save=True)


class Command(BaseCommand):
    help = "Create demo admin, a lady, and live sponsor cards (men and women)."

    def handle(self, *args, **options):
        admin, _created = User.objects.get_or_create(
            phone="255700000001",
            defaults={
                "display_name": "Site Admin",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_adult_confirmed": True,
                "city": "Dar es Salaam",
                "age": 34,
            },
        )
        admin.set_password("AdminPass123")
        admin.role = User.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_adult_confirmed = True
        admin.is_active = True
        admin.save()

        lady, _ = User.objects.get_or_create(
            phone="255712000002",
            defaults={
                "display_name": "Asha",
                "role": User.Role.LADY,
                "is_adult_confirmed": True,
                "city": "Dar es Salaam",
                "age": 26,
                "looking_for": "40+, Dar, travel",
            },
        )
        lady.set_password("LadyPass123")
        lady.is_adult_confirmed = True
        lady.save()

        for row in DEMO_MEN:
            defaults = {**row, "status": SponsorProfile.Status.LIVE, "owner": None}
            profile, made = SponsorProfile.objects.get_or_create(
                public_name=row["public_name"],
                city=row["city"],
                defaults=defaults,
            )
            changed = []
            for field, value in row.items():
                if getattr(profile, field, None) != value:
                    setattr(profile, field, value)
                    changed.append(field)
            if profile.status != SponsorProfile.Status.LIVE:
                profile.status = SponsorProfile.Status.LIVE
                changed.append("status")
            if changed:
                profile.save(update_fields=list(dict.fromkeys(changed + ["updated_at"])))
            _attach_photo(profile, row["public_name"])

        self.stdout.write(self.style.SUCCESS("Demo users ready."))
        self.stdout.write("Admin  255700000001 / AdminPass123")
        self.stdout.write("Lady   255712000002 / LadyPass123")
