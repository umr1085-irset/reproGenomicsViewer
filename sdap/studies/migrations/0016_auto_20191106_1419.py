# Generated by Django 2.2.5 on 2019-11-06 14:19

from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0015_auto_20191105_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='expressiondata',
            name='gene_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expressiondata',
            name='gene_type',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]