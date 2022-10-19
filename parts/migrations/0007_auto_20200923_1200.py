# Generated by Django 3.1.1 on 2020-09-23 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0006_auto_20200915_1435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseassembly',
            name='unit_price',
        ),
        migrations.AddField(
            model_name='part',
            name='material',
            field=models.TextField(blank=True),
        ),
        migrations.AddIndex(
            model_name='part',
            index=models.Index(fields=['full_code'], name='parts_part_full_co_3613ba_idx'),
        ),
    ]
