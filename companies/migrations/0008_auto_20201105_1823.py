# Generated by Django 3.1.2 on 2020-11-05 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0007_remove_company_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='location',
            name='deleted_at',
        ),
    ]