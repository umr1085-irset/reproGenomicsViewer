# Generated by Django 2.2.5 on 2019-10-02 07:58

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0002_expressionstudy_samples_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expressionstudy',
            name='age',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='antibody',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='cell_sorted',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='dev_stage',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='experimental_design',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='keywords',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='mutant',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='ome',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='sex',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='species',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='technology',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='tissues',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='topics',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list(), size=None),
            preserve_default=False,
        ),
    ]
