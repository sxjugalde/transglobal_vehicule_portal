# Generated by Django 3.1.2 on 2020-11-19 19:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20201119_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartrow',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]