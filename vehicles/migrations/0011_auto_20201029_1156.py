# Generated by Django 3.1.2 on 2020-10-29 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0010_vehicle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bom',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='vehiclefamily',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
