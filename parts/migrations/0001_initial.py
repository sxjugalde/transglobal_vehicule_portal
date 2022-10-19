# Generated by Django 3.1.1 on 2020-09-03 20:43

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=60)),
                ('code', models.CharField(help_text='5 digit TG code.', max_length=10, validators=[django.core.validators.RegexValidator(code='nomatch', message='Code has to be 5 digits', regex='^[0-9]{5}$')])),
                ('suffix', models.PositiveSmallIntegerField(blank=True, help_text='Subcomponent suffix.', null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('revision', models.CharField(blank=True, help_text='Revision code. For example: A.', max_length=1)),
                ('revision_notes', models.CharField(blank=True, max_length=100)),
                ('dimension', models.CharField(blank=True, max_length=25)),
                ('comments', models.CharField(blank=True, max_length=100)),
                ('is_made_locally', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
                ('is_obsolete', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'part',
                'verbose_name_plural': 'parts',
            },
        ),
        migrations.CreateModel(
            name='PurchaseAssembly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=60)),
                ('code', models.CharField(help_text='Format: AXXXXXXX, where XXXXXXX is an incremental number.', max_length=10, validators=[django.core.validators.RegexValidator(code='nomatch', message='Code has to begin with an A, followed by 8 digits.', regex='^([A]{1}\\d{8})$')])),
                ('unit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
            ],
            options={
                'verbose_name': 'purchase assembly',
                'verbose_name_plural': 'purchase assemblies',
            },
        ),
        migrations.CreateModel(
            name='PurchaseAssemblyPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1, help_text='Amount used in the purchase assembly.', validators=[django.core.validators.MinValueValidator(1)])),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', related_query_name='part', to='parts.part')),
                ('purchase_assembly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_assemblies', related_query_name='purchase_assembly', to='parts.purchaseassembly')),
            ],
            options={
                'verbose_name': 'purchase assembly part',
                'verbose_name_plural': 'purchase assembly parts',
            },
        ),
    ]