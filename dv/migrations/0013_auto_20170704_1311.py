# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-04 10:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0012_auto_20170704_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='programmes',
            field=models.ManyToManyField(related_name='news', to='dv.Programme'),
        ),
        migrations.AlterField(
            model_name='news',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='news', to='dv.Project'),
        ),
    ]
