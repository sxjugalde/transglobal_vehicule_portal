# Generated by Django 3.1.2 on 2020-11-06 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
        ('vehicles', '0017_auto_20201105_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bom',
            name='files',
            field=models.ManyToManyField(blank=True, help_text='General files related to the BOM.', related_name='boms', related_query_name='bom', to='files.File'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='files',
            field=models.ManyToManyField(blank=True, help_text='General files related to the vehicle.', related_name='vehicles', related_query_name='vehicle', to='files.File'),
        ),
    ]
