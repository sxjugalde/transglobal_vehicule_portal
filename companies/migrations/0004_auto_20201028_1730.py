# Generated by Django 3.1.2 on 2020-10-28 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20200915_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='company',
            field=models.ForeignKey(help_text='Customer company that owns this location.', on_delete=django.db.models.deletion.PROTECT, related_name='locations', related_query_name='location', to='companies.company'),
        ),
    ]