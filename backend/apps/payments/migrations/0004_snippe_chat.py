from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0003_status_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="provider_reference",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="payment",
            name="provider_result",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="payment",
            name="provider_message",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="payment",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("unlock", "Unlock profile"),
                    ("chat", "Open chat"),
                    ("listing", "Post sponsor card"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="selcom_reference",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
