# Generated by Django 2.2.5 on 2020-04-09 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0035_auto_20200409_1258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expressiondata',
            name='species',
        ),
        migrations.RemoveField(
            model_name='genelist',
            name='species',
        ),
    ]
