# Generated by Django 3.2.15 on 2023-12-22 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0007_auto_20230316_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bilateralinitiative',
            name='promoter_organization',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]