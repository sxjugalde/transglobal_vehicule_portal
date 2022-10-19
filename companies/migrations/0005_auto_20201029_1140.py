# Generated by Django 3.1.2 on 2020-10-29 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_auto_20201028_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='code',
            field=models.CharField(default='Company code', help_text='Short identifying code for the company.', max_length=20, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='identification',
            field=models.CharField(blank=True, editable=False, max_length=150),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(fields=('company', 'name'), name='unique_company_location'),
        ),
    ]