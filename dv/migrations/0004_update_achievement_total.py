# Generated by Django 3.2.10 on 2021-12-09 14:05

from django.db import migrations
from django.db.models import F


def forwards_func(apps, schema_editor):
    Indicator = apps.get_model("dv", "Indicator")
    Indicator.objects.using(schema_editor.connection.alias).update(
        achievement_total=F("achievement_eea") + F("achievement_norway")
    )


def reverse_func(apps, schema_editor):
    Indicator = apps.get_model("dv", "Indicator")
    Indicator.objects.using(schema_editor.connection.alias).update(achievement_total=0)


class Migration(migrations.Migration):

    dependencies = [
        ("dv", "0003_indicator_achievement_total"),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
