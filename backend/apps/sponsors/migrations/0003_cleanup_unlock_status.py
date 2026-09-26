from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_lady_if_needed(apps, schema_editor):
    Unlock = apps.get_model("sponsors", "Unlock")
    for row in Unlock.objects.all():
        if getattr(row, "user_id", None) is None and getattr(row, "lady_id", None):
            row.user_id = row.lady_id
            row.save(update_fields=["user_id"])


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sponsors", "0002_gender_chat_access"),
    ]

    operations = [
        migrations.RunPython(copy_lady_if_needed, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="unlock",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="unlocks",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="unlock",
            unique_together={("user", "sponsor")},
        ),
        migrations.RemoveField(
            model_name="unlock",
            name="lady",
        ),
        migrations.RemoveField(
            model_name="sponsorprofile",
            name="listing_paid_at",
        ),
        migrations.AlterField(
            model_name="sponsorprofile",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("live", "Live"), ("paused", "Paused")],
                default="draft",
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
    ]
