# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programme',
            name='allocation',
        ),
        migrations.AddField(
            model_name='programme',
            name='allocation_eea',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='programme',
            name='allocation_norway',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='is_eea',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='is_norway',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]