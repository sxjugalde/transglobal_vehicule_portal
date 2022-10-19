# Generated by Django 3.1.5 on 2022-07-31 10:03

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0009_auto_20220731_0602'),
        ('vehicles', '0018_auto_20201106_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assembly',
            name='code',
            field=models.CharField(help_text='4 digit assembly code. For example: 1010.', max_length=4, validators=[django.core.validators.RegexValidator(code='nomatch', message='Code has to be 4 digits long.', regex='^\\d{4}$')], verbose_name='Parent Assembly Code'),
        ),
        migrations.AlterField(
            model_name='assembly',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Parent Assembly Code'),
        ),
        migrations.AlterField(
            model_name='bom',
            name='code',
            field=models.CharField(max_length=20, verbose_name='BOM Code'),
        ),
        migrations.AlterField(
            model_name='bom',
            name='name',
            field=models.CharField(max_length=50, verbose_name='BOM Name'),
        ),
        migrations.AlterField(
            model_name='bom',
            name='revision',
            field=models.CharField(blank=True, help_text='Revision code. For example: A.', max_length=1, verbose_name='BOM Rev Level'),
        ),
        migrations.AlterField(
            model_name='subassembly',
            name='assembly',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='vehicle_family', chained_model_field='vehicle_family', on_delete=django.db.models.deletion.CASCADE, related_name='subassemblies', related_query_name='subassembly', to='vehicles.assembly', verbose_name='Parent Assembly'),
        ),
        migrations.AlterField(
            model_name='subassembly',
            name='code',
            field=models.CharField(help_text='Format: SXX, where XX is a number. For example: S01.', max_length=3, validators=[django.core.validators.RegexValidator(code='nomatch', message='Code has to begin with S and be followed by 2 digits.', regex='^[S]{1}\\d{2}$')], verbose_name='Sub Assembly Code'),
        ),
        migrations.AlterField(
            model_name='subassembly',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Sub Assembly Code'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='identification_number',
            field=models.CharField(max_length=20, unique=True, verbose_name='VIN#'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='location',
            field=models.ForeignKey(help_text='Location where the customer has this vehicle.', on_delete=django.db.models.deletion.PROTECT, related_name='vehicles', related_query_name='vehicle', to='companies.location', verbose_name='Company & Location'),
        ),
        migrations.AlterField(
            model_name='vehiclefamily',
            name='code',
            field=models.CharField(blank=True, max_length=20, verbose_name='Model Code'),
        ),
        migrations.AlterField(
            model_name='vehiclefamily',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Family Name'),
        ),
    ]
