# Generated by Django 4.2.14 on 2024-07-10 08:52

from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ("dv", "0008_alter_bilateralinitiative_promoter_organization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="staticcontent",
            name="body",
            field=django_ckeditor_5.fields.CKEditor5Field(),
        ),
    ]
