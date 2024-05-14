# Generated by Django 5.0.4 on 2024-05-14 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0001_initial"),
        ("users", "0003_client_clientprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminpanelprofile",
            name="base_company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="crm.basecompany",
            ),
        ),
    ]
