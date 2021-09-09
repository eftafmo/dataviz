# Generated by Django 3.2.5 on 2021-09-09 12:19

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NUTS',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'NUTS',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='PrioritySector',
            fields=[
                ('code', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('code', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('status', models.CharField(max_length=16)),
                ('url', models.CharField(max_length=256, null=True)),
                ('summary', models.TextField()),
                ('allocation_eea', models.DecimalField(decimal_places=2, max_digits=15)),
                ('allocation_norway', models.DecimalField(decimal_places=2, max_digits=15)),
                ('co_financing', models.DecimalField(decimal_places=2, max_digits=15)),
                ('is_tap', models.BooleanField(help_text='Technical Assistance Programme')),
                ('is_bfp', models.BooleanField(help_text='Bilateral Fund Programme')),
            ],
        ),
        migrations.CreateModel(
            name='ProgrammeArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('code', models.CharField(max_length=4)),
                ('name', models.CharField(max_length=256)),
                ('short_name', models.CharField(max_length=32)),
                ('order', models.SmallIntegerField(null=True)),
                ('objective', models.TextField()),
                ('priority_sector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dv.prioritysector')),
            ],
            options={
                'unique_together': {('code', 'funding_period')},
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('code', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('status', models.CharField(max_length=19)),
                ('nuts_code', models.CharField(max_length=5)),
                ('url', models.CharField(max_length=256, null=True)),
                ('allocation', models.DecimalField(decimal_places=2, max_digits=15)),
                ('is_eea', models.BooleanField()),
                ('is_norway', models.BooleanField()),
                ('has_ended', models.BooleanField()),
                ('is_dpp', models.BooleanField()),
                ('is_positive_fx', models.BooleanField()),
                ('is_improved_knowledge', models.BooleanField()),
                ('is_continued_coop', models.BooleanField()),
                ('initial_description', models.TextField()),
                ('results_description', models.TextField()),
                ('priority_sectors', models.ManyToManyField(to='dv.PrioritySector')),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dv.programme')),
                ('programme_areas', models.ManyToManyField(to='dv.ProgrammeArea')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('url', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='StaticContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('body', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='dv.project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dv.state'),
        ),
        migrations.AddField(
            model_name='programme',
            name='programme_areas',
            field=models.ManyToManyField(to='dv.ProgrammeArea'),
        ),
        migrations.AddField(
            model_name='programme',
            name='states',
            field=models.ManyToManyField(to='dv.State'),
        ),
        migrations.CreateModel(
            name='OrganisationRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('role_code', models.CharField(max_length=8)),
                ('role_name', models.CharField(max_length=64)),
                ('organisation_country', models.CharField(max_length=64)),
                ('organisation_name', models.CharField(max_length=256)),
                ('nuts_code', models.CharField(max_length=5)),
                ('programme', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='organisation_roles', to='dv.programme')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='organisation_roles', to='dv.project')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dv.state')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('link', models.URLField(max_length=2000)),
                ('created', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(null=True)),
                ('summary', models.TextField(null=True)),
                ('image', models.URLField(max_length=2000)),
                ('is_partnership', models.BooleanField(default=False)),
                ('programmes', models.ManyToManyField(related_name='news', to='dv.Programme')),
                ('project', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='news', to='dv.project')),
            ],
            options={
                'verbose_name_plural': 'news',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('indicator', models.CharField(max_length=256)),
                ('outcome', models.CharField(max_length=256)),
                ('header', models.CharField(max_length=256)),
                ('unit_of_measurement', models.CharField(max_length=8)),
                ('achievement_eea', models.DecimalField(decimal_places=2, max_digits=9)),
                ('achievement_norway', models.DecimalField(decimal_places=2, max_digits=9)),
                ('is_core', models.BooleanField()),
                ('is_common', models.BooleanField()),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dv.programme')),
                ('programme_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dv.programmearea')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dv.state')),
            ],
        ),
        migrations.CreateModel(
            name='BilateralInitiative',
            fields=[
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('code', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=512)),
                ('level', models.CharField(max_length=16)),
                ('status', models.CharField(max_length=16)),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bilateral_initiatives', to='dv.programme')),
                ('programme_areas', models.ManyToManyField(to='dv.ProgrammeArea')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bilateral_initiatives', to='dv.project')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dv.state')),
            ],
        ),
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funding_period', models.IntegerField(choices=[(1, '2004-2009'), (2, '2009-2014'), (3, '2014-2021')])),
                ('financial_mechanism', models.CharField(choices=[('EEA', 'EEA Grants'), ('NOR', 'Norway Grants')], max_length=3)),
                ('gross_allocation', models.DecimalField(decimal_places=2, max_digits=15)),
                ('net_allocation', models.DecimalField(decimal_places=2, max_digits=15)),
                ('thematic', models.CharField(blank=True, max_length=16)),
                ('programme_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dv.programmearea')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dv.state')),
            ],
            options={
                'unique_together': {('state', 'programme_area', 'financial_mechanism', 'funding_period')},
            },
        ),
    ]
