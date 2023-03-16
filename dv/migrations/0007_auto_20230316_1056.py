# Generated by Django 3.2.18 on 2023-03-16 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0006_organisation_null_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='achievement_eea',
            field=models.DecimalField(decimal_places=2, max_digits=15),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='achievement_norway',
            field=models.DecimalField(decimal_places=2, max_digits=15),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='achievement_total',
            field=models.DecimalField(decimal_places=2, help_text='Total results including some that cannot be allocated to either EEA or Norway.', max_digits=15),
        ),
    ]
