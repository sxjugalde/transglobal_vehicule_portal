# Generated by Django 3.1.2 on 2020-10-20 21:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0006_auto_20201007_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bom',
            name='import_file',
            field=models.FileField(blank=True, upload_to='uploads/boms/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xlsm', 'xls'])]),
        ),
    ]
