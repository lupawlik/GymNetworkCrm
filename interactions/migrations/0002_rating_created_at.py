# Generated by Django 5.0.4 on 2024-05-21 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rating",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
