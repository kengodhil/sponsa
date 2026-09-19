from django.apps import AppConfig


class SponsorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sponsors"
    label = "sponsors"
    verbose_name = "Sponsor profiles"
