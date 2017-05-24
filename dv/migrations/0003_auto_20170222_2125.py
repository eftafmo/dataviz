# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 21:25
from __future__ import unicode_literals

from django.db import migrations, models
import dv.lib.models


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0002_auto_20170222_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='NUTS',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
            bases=(dv.lib.models.ImportableModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='organisation',
            name='nuts',
            field=models.CharField(default='', max_length=5),
            preserve_default=False,
        ),
    ]