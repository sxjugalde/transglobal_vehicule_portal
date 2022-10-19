# Generated by Django 3.1.2 on 2020-10-29 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0012_auto_20201029_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bom',
            name='vehicle_family',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='boms', related_query_name='bom', to='vehicles.vehiclefamily'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='bom',
            field=models.ForeignKey(help_text="BOM that represents this vehicle's structure.", on_delete=django.db.models.deletion.PROTECT, related_name='vehicles', related_query_name='vehicle', to='vehicles.bom', verbose_name='Bill of materials'),
        ),
    ]
