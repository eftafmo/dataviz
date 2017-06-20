# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-17 10:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0002_auto_nutsOrder_indicatorDupName'),
    ]

    operations = [
        migrations.AddField(
            model_name='programmeindicator',
            name='result_text',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='programmeindicator',
            name='state',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='dv.State'),
            preserve_default=False,
        ),
    ]