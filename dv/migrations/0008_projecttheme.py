# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-23 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import dv.lib.models


class Migration(migrations.Migration):

    dependencies = [
        ('dv', '0007_auto_20170622_1620'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='dv.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(dv.lib.models.ImportableModelMixin, models.Model),
        ),
    ]