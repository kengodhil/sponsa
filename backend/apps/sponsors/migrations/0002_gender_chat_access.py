from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_lady_to_user(apps, schema_editor):
    Unlock = apps.get_model("sponsors", "Unlock")
    for u in Unlock.objects.all():
        if hasattr(u, "lady_id") and u.lady_id and not u.user_id:
            u.user_id = u.lady_id
            u.save(update_fields=["user_id"])


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sponsors", "0001_initial"),
        ("payments", "0003_status_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="sponsorprofile",
            name="gender",
            field=models.CharField(
                choices=[("man", "Man"), ("woman", "Woman")],
                default="man",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="sponsorprofile",
            name="badge",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "None"),
                    ("new", "New"),
                    ("featured", "Featured"),
                    ("popular", "Popular"),
                    ("verified", "Verified"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="sponsorprofile",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sponsor_profiles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="unlock",
            name="user",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="unlocks",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(copy_lady_to_user, migrations.RunPython.noop),
        migrations.CreateModel(
            name="ChatAccess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "payment",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="chat_access",
                        to="payments.payment",
                    ),
                ),
                (
                    "sponsor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_accesses",
                        to="sponsors.sponsorprofile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_accesses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user", "sponsor")}},
        ),
    ]
