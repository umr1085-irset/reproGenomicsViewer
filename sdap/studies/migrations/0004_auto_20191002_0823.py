# Generated by Django 2.2.5 on 2019-10-02 08:23

from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0003_auto_20191002_0758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expressionstudy',
            name='age',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='antibody',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='cell_sorted',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='dev_stage',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='experimental_design',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='keywords',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='mutant',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='ome',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='sex',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='species',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='technology',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='tissues',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='expressionstudy',
            name='topics',
            field=django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, null=True, size=None),
        ),
    ]